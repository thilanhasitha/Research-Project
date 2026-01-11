"""
News RAG (Retrieval-Augmented Generation) Service
Handles querying news from Weaviate and generating contextual responses using LLM.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.Database.weaviate_client import WeaviateClient
from app.Database.repositories.rss_repository import RSSRepository
from app.llm.LLMFactory import LLMFactory
from weaviate.classes.query import Filter
import logging

logger = logging.getLogger(__name__)


class NewsRAGService:
    """Service for RAG-based news querying and response generation."""
    
    def __init__(self):
        self.weaviate_client = WeaviateClient(collection_name="RSSNews")
        self.rss_repository = RSSRepository()
        self.llm_provider = LLMFactory.get_provider("ollama")
        self.llm = self.llm_provider.get_llm()
        self._ensure_connected()
    
    def _ensure_connected(self):
        """Ensure Weaviate is connected."""
        if not self.weaviate_client.is_connected:
            self.weaviate_client.connect()
            logger.info("NewsRAGService: Connected to Weaviate")
    
    async def search_news_by_text(
        self,
        query: str,
        limit: int = 5,
        sentiment_filter: Optional[str] = None,
        date_from: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Search news using text-based semantic search.
        Falls back to MongoDB if Weaviate has no results.
        
        Args:
            query: Natural language search query
            limit: Maximum number of results
            sentiment_filter: Filter by sentiment (positive, negative, neutral)
            date_from: Only return news after this date
            
        Returns:
            List of news articles with metadata
        """
        try:
            collection = self.weaviate_client.collection
            
            # Build filters
            filters = None
            if sentiment_filter or date_from:
                filter_conditions = []
                
                if sentiment_filter:
                    filter_conditions.append(
                        Filter.by_property("sentiment").equal(sentiment_filter)
                    )
                
                if date_from:
                    filter_conditions.append(
                        Filter.by_property("published").greater_or_equal(date_from)
                    )
                
                # Combine filters with AND
                if len(filter_conditions) == 1:
                    filters = filter_conditions[0]
                else:
                    filters = Filter.all_of(filter_conditions)
            
            # Perform hybrid search with optimized settings for speed
            logger.info(f"Searching Weaviate with query: '{query}', limit: {limit}")
            
            response = collection.query.hybrid(
                query=query,
                limit=limit,
                filters=filters,
                return_metadata=["score"],
                alpha=0.75  # Favor vector search (0.5 = balanced, 1.0 = pure vector)
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "id": str(obj.uuid),
                    "mongoId": obj.properties.get("mongoId"),
                    "title": obj.properties.get("title"),
                    "content": obj.properties.get("content"),
                    "clean_text": obj.properties.get("clean_text"),
                    "summary": obj.properties.get("summary"),
                    "link": obj.properties.get("link"),
                    "published": obj.properties.get("published"),
                    "sentiment": obj.properties.get("sentiment"),
                    "score": obj.properties.get("score"),
                    "relevance_score": obj.metadata.score if hasattr(obj.metadata, 'score') else None
                })
            
            if results:
                logger.info(f"Found {len(results)} news articles in Weaviate")
                return results
            
            # For speed, return empty if Weaviate has no results
            # Only fallback to MongoDB if explicitly needed
            logger.warning("No results from Weaviate")
            return []
            
        except Exception as e:
            logger.error(f"Error searching Weaviate, falling back to MongoDB: {e}", exc_info=True)
            try:
                mongo_results = await self._search_mongodb(query, limit, sentiment_filter, date_from)
                logger.info(f"MongoDB fallback successful: {len(mongo_results)} articles")
                return mongo_results
            except Exception as mongo_err:
                logger.error(f"MongoDB fallback also failed: {mongo_err}", exc_info=True)
                return []
    
    async def _search_mongodb(
        self, 
        query: str, 
        limit: int,
        sentiment_filter: Optional[str] = None,
        date_from: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Search MongoDB for news articles using text search.
        """
        try:
            # Build MongoDB filter
            filter_dict = {}
            
            # Text search in title and content
            if query:
                filter_dict["$or"] = [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]
            
            if sentiment_filter:
                filter_dict["sentiment"] = sentiment_filter
            
            if date_from:
                filter_dict["published"] = {"$gte": date_from}
            
            # Use the repository to search
            articles = await self.rss_repository.find_by_filter(filter_dict, limit)
            
            # Format results to match Weaviate structure
            formatted = []
            for article in articles:
                if "error" in article:
                    continue
                formatted.append({
                    "id": article.get("_id"),
                    "mongoId": article.get("_id"),
                    "title": article.get("title", "No title"),
                    "content": article.get("content", ""),
                    "clean_text": article.get("clean_text", ""),
                    "summary": article.get("content", "")[:200] + "..." if article.get("content") else "",
                    "link": article.get("link", ""),
                    "published": article.get("published", ""),
                    "sentiment": article.get("sentiment", "neutral"),
                    "score": 0.5,  # Default score for MongoDB results
                    "relevance_score": None
                })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error searching MongoDB: {e}", exc_info=True)
            return []
    
    async def get_trending_topics(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending news from the last N days sorted by sentiment score.
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of trending news articles
        """
        try:
            collection = self.weaviate_client.collection
            date_from = datetime.utcnow() - timedelta(days=days)
            
            logger.info(f"Getting trending topics from last {days} days")
            
            response = collection.query.fetch_objects(
                filters=Filter.by_property("published").greater_or_equal(date_from),
                limit=limit
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "id": str(obj.uuid),
                    "mongoId": obj.properties.get("mongoId"),
                    "title": obj.properties.get("title"),
                    "summary": obj.properties.get("summary"),
                    "link": obj.properties.get("link"),
                    "published": obj.properties.get("published"),
                    "sentiment": obj.properties.get("sentiment"),
                    "score": obj.properties.get("score", 0)
                })
            
            # Sort by score descending
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            logger.info(f"Found {len(results)} trending articles")
            return results
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}", exc_info=True)
            return []
    
    async def answer_question(
        self,
        question: str,
        context_limit: int = 5,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a user question using RAG - retrieve relevant news and generate answer.
        
        Args:
            question: User's question
            context_limit: Number of news articles to use as context
            include_sources: Whether to include source articles in response
            
        Returns:
            Dict with answer, sources, and metadata
        """
        try:
            logger.info(f"Answering question: '{question}'")
            
            # Step 1: Retrieve relevant news articles
            news_articles = await self.search_news_by_text(
                query=question,
                limit=context_limit
            )
            
            if not news_articles:
                return {
                    "answer": "I couldn't find any relevant news articles to answer your question. Please try rephrasing or asking about a different topic.",
                    "sources": [],
                    "context_used": 0
                }
            
            # Step 2: Build compact context (optimized for speed)
            context_parts = []
            for idx, article in enumerate(news_articles, 1):
                # Use clean_text or content for better context
                content = article.get('clean_text', article.get('content', ''))
                if not content:
                    content = article.get('summary', '')
                
                # Truncate to 300 chars for better context
                content = content[:300] + '...' if len(content) > 300 else content
                
                # Include publication date for context
                pub_date = article.get('published', 'Unknown date')
                context_parts.append(
                    f"[Article {idx}]\nTitle: {article['title']}\nDate: {pub_date}\nContent: {content}\n"
                )
            
            context = "\n".join(context_parts)
            
            # Step 3: Generate answer using LLM with strict prompt
            prompt = f"""You are a news assistant. Answer the user's question using ONLY the information from the news articles provided below. 

STRICT RULES:
- Use ONLY the information from the articles below
- Do NOT use your general knowledge or training data
- If the articles don't contain information to answer the question, say "I don't have information about this in the recent news articles."
- Do NOT mention Bitcoin, cryptocurrency, or any other topics not present in the articles
- Be concise and factual
- Cite article numbers when referencing information (e.g., "According to Article 1...")

NEWS ARTICLES:
{context}

USER QUESTION: {question}

ANSWER (based only on the articles above):"""
            
            logger.info(f"Generating answer with {len(news_articles)} articles as context")
            answer = await self.llm_provider.generate(prompt)
            
            # Step 4: Prepare response
            response = {
                "answer": answer,
                "context_used": len(news_articles),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if include_sources:
                response["sources"] = [
                    {
                        "title": article["title"],
                        "summary": article["summary"],
                        "link": article["link"],
                        "published": article["published"],
                        "sentiment": article["sentiment"],
                        "relevance_score": article.get("relevance_score")
                    }
                    for article in news_articles
                ]
            
            logger.info("Successfully generated answer with RAG")
            return response
            
        except Exception as e:
            logger.error(f"Error answering question: {e}", exc_info=True)
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "context_used": 0,
                "error": str(e)
            }
    
    async def get_sentiment_summary(self, topic: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
        """
        Get sentiment analysis summary for a topic or overall market.
        
        Args:
            topic: Optional topic to filter by (uses semantic search)
            days: Number of days to analyze
            
        Returns:
            Sentiment summary with statistics
        """
        try:
            logger.info(f"Getting sentiment summary for topic: {topic}, days: {days}")
            
            date_from = datetime.utcnow() - timedelta(days=days)
            
            if topic:
                # Search by topic
                articles = await self.search_news_by_text(
                    query=topic,
                    limit=50,
                    date_from=date_from
                )
            else:
                # Get all recent articles
                collection = self.weaviate_client.collection
                response = collection.query.fetch_objects(
                    filters=Filter.by_property("published").greater_or_equal(date_from),
                    limit=50
                )
                articles = [
                    {
                        "sentiment": obj.properties.get("sentiment"),
                        "score": obj.properties.get("score", 0),
                        "title": obj.properties.get("title")
                    }
                    for obj in response.objects
                ]
            
            if not articles:
                return {
                    "topic": topic or "all",
                    "period_days": days,
                    "total_articles": 0,
                    "sentiment_distribution": {},
                    "average_score": 0,
                    "message": "No articles found for the specified criteria"
                }
            
            # Calculate statistics
            sentiments = {}
            total_score = 0
            
            for article in articles:
                sentiment = article.get("sentiment", "neutral")
                score = article.get("score", 0)
                
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
                total_score += score
            
            avg_score = total_score / len(articles) if articles else 0
            
            # Generate summary text
            dominant_sentiment = max(sentiments, key=sentiments.get) if sentiments else "neutral"
            
            summary_text = f"Over the last {days} days"
            if topic:
                summary_text += f" for '{topic}'"
            summary_text += f", the overall sentiment is **{dominant_sentiment}** "
            summary_text += f"with an average score of {avg_score:.2f}. "
            summary_text += f"Analyzed {len(articles)} articles."
            
            return {
                "topic": topic or "all",
                "period_days": days,
                "total_articles": len(articles),
                "sentiment_distribution": sentiments,
                "average_score": round(avg_score, 3),
                "dominant_sentiment": dominant_sentiment,
                "summary": summary_text
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment summary: {e}", exc_info=True)
            return {
                "error": str(e),
                "message": "Failed to generate sentiment summary"
            }
    
    def close(self):
        """Close connections."""
        if self.weaviate_client:
            self.weaviate_client.close()
            logger.info("NewsRAGService: Closed connections")
