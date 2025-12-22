"""
News RAG (Retrieval-Augmented Generation) Service
Handles querying news from Weaviate and generating contextual responses using LLM.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.Database.weaviate_client import WeaviateClient
from app.llm.LLMFactory import LLMFactory
from weaviate.classes.query import Filter
import logging

logger = logging.getLogger(__name__)


class NewsRAGService:
    """Service for RAG-based news querying and response generation."""
    
    def __init__(self):
        self.weaviate_client = WeaviateClient(collection_name="RSSNews")
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
            
            # Perform hybrid search (combines vector + BM25)
            logger.info(f"Searching news with query: '{query}', limit: {limit}")
            
            response = collection.query.hybrid(
                query=query,
                limit=limit,
                filters=filters,
                return_metadata=["score"]
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
            
            logger.info(f"Found {len(results)} news articles")
            return results
            
        except Exception as e:
            logger.error(f"Error searching news: {e}", exc_info=True)
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
            
            # Step 2: Build context from retrieved articles
            context_parts = []
            for idx, article in enumerate(news_articles, 1):
                context_parts.append(
                    f"Article {idx}:\n"
                    f"Title: {article['title']}\n"
                    f"Summary: {article['summary']}\n"
                    f"Sentiment: {article['sentiment']} (score: {article['score']})\n"
                    f"Published: {article['published']}\n"
                )
            
            context = "\n\n".join(context_parts)
            
            # Step 3: Generate answer using LLM
            prompt = f"""You are a financial news analyst assistant. Use the following news articles to answer the user's question accurately and concisely.

NEWS CONTEXT:
{context}

USER QUESTION:
{question}

INSTRUCTIONS:
1. Answer the question based ONLY on the provided news articles
2. If the articles don't contain enough information, say so
3. Cite specific articles when making claims (e.g., "According to Article 1...")
4. Highlight sentiment and market trends when relevant
5. Keep your answer concise but informative (2-3 paragraphs max)

ANSWER:"""
            
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
