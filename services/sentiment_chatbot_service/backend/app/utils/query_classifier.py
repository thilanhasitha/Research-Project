"""
Query Classifier Utility
Detects greetings and out-of-scope queries to provide direct responses
without retrieving articles from the database.
"""

from typing import Dict, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class QueryClassifier:
    """
    Classifies user queries to determine if they are:
    - Greetings
    - Out-of-scope (not related to finance/trading/stock market)
    - In-scope (financial queries)
    """
    
    # Greeting patterns
    GREETING_PATTERNS = [
        r'\b(hi|hello|hey|hiya|howdy|greetings|sup|yo)\b',
        r'\b(good\s+(morning|afternoon|evening|day|night))\b',
        r'\b(what\'?s\s+up|whats\s+up|how\s+(are\s+you|is\s+it\s+going))\b',
        r'^\s*(hi+|he+y+|hello+|yo+)\s*[!.]*\s*$',  # Just greetings with variations
        r'\b(nice\s+to\s+meet\s+you|pleased\s+to\s+meet)\b',
        r'\b(how\s+do\s+you\s+do)\b',
    ]
    
    # Financial/stock market keywords that indicate in-scope queries
    FINANCIAL_KEYWORDS = [
        # Market terms
        'stock', 'stocks', 'share', 'shares', 'market', 'markets', 'trading', 'trade',
        'equity', 'equities', 'portfolio', 'investment', 'investing', 'investor',
        
        # Financial instruments
        'bond', 'bonds', 'derivative', 'derivatives', 'option', 'options', 'futures',
        'commodity', 'commodities', 'forex', 'currency', 'currencies', 'crypto',
        'cryptocurrency', 'bitcoin', 'ethereum', 'etf', 'mutual fund',
        
        # Financial metrics
        'price', 'valuation', 'earnings', 'revenue', 'profit', 'dividend', 'dividends',
        'eps', 'pe ratio', 'p/e', 'market cap', 'capitalization', 'yield',
        'return', 'returns', 'roi', 'growth', 'quarterly', 'annual',
        
        # Market activities
        'bull', 'bear', 'rally', 'crash', 'correction', 'volatility', 'volume',
        'buy', 'sell', 'buying', 'selling', 'bid', 'ask', 'spread', 'margin',
        'ipo', 'listing', 'delisting', 'merger', 'acquisition',
        
        # Financial institutions
        'bank', 'banking', 'broker', 'brokerage', 'exchange', 'nasdaq', 'nyse',
        'wall street', 'sec', 'federal reserve', 'fed', 'central bank',
        
        # Financial news terms
        'quarterly report', 'earnings report', 'financial statement', 'balance sheet',
        'income statement', 'cash flow', 'fiscal', 'finance', 'financial',
        'economy', 'economic', 'recession', 'inflation', 'interest rate',
        
        # Sentiment/Analysis
        'sentiment', 'analysis', 'forecast', 'prediction', 'outlook', 'trend',
        'technical analysis', 'fundamental analysis', 'bullish', 'bearish',
        
        # Company/Business
        'company', 'companies', 'corporation', 'firm', 'business', 'sector',
        'industry', 'startup', 'enterprise', 'ceo', 'cfo', 'executive',
        
        # News/Updates
        'news', 'update', 'announcement', 'report', 'article', 'headline',
        'latest', 'recent', 'current', 'today', 'yesterday', 'this week'
    ]
    
    # Common out-of-scope query patterns
    OUT_OF_SCOPE_PATTERNS = [
        # Personal questions
        r'\b(who\s+(are\s+you|created\s+you|made\s+you|built\s+you))\b',
        r'\b(what\s+(is\s+your\s+name|can\s+you\s+do))\b',
        r'\b(tell\s+me\s+(about\s+yourself|your\s+purpose))\b',
        
        # Weather
        r'\b(weather|temperature|forecast|rain|sunny|cloudy|snow)\b',
        
        # Sports (unless it's sports companies/stocks)
        r'\b(football|soccer|basketball|baseball|cricket|tennis|sports\s+game)\b',
        
        # Entertainment
        r'\b(movie|movies|film|music|song|artist|actor|actress|celebrity)\b',
        
        # Food
        r'\b(recipe|cook|cooking|food|restaurant|meal|dinner|lunch)\b',
        
        # General knowledge (non-financial)
        r'\b(what\s+is\s+the\s+(capital|population|area)|who\s+is\s+the\s+president)\b',
        r'\b(historical?\s+event|history\s+of(?!\s+(stock|market|trading)))\b',
        
        # Math problems (unless financial calculations)
        r'\b(solve|calculate|math\s+problem)(?!.*\b(profit|loss|return|price|value)\b)',
        
        # Technology (unless fintech)
        r'\b(how\s+to\s+(code|program|install|setup|fix))(?!.*\b(trading|financial)\b)',
    ]
    
    # Greeting responses
    GREETING_RESPONSES = [
        "Hello! I'm your financial news assistant. I can help you with information about stocks, markets, trading, and financial news. What would you like to know?",
        "Hi there! I specialize in providing insights on financial markets and trading news. How can I assist you today?",
        "Greetings! I'm here to help you with stock market news, financial analysis, and trading insights. What can I help you with?",
        "Hello! I can provide you with the latest financial news, market trends, and trading insights. What would you like to explore?",
    ]
    
    # Out-of-scope responses
    OUT_OF_SCOPE_RESPONSES = {
        'default': "I'm specialized in financial markets, trading, and stock-related queries. I don't have information about that topic. Please ask me about stocks, markets, financial news, or trading-related topics.",
        
        'personal': "I'm a financial news assistant focused on providing insights about stocks, markets, and trading. Let me help you with financial queries instead!",
        
        'weather': "I don't provide weather information, but I can help you with financial news, stock market updates, and trading insights. Would you like to know about market conditions instead?",
        
        'entertainment': "I specialize in financial markets and trading news, not entertainment. However, if you're interested in entertainment industry stocks or companies, I'd be happy to help with that!",
        
        'general': "I'm focused on financial markets, trading, and stock-related information. For that topic, you might want to consult a different resource. Can I help you with any financial or market-related questions?",
    }
    
    def __init__(self):
        """Initialize the query classifier."""
        # Compile patterns for efficiency
        self.greeting_regex = re.compile(
            '|'.join(self.GREETING_PATTERNS), 
            re.IGNORECASE
        )
        self.out_of_scope_regex = re.compile(
            '|'.join(self.OUT_OF_SCOPE_PATTERNS),
            re.IGNORECASE
        )
        
        # Compile financial keywords pattern
        financial_pattern = '|'.join([re.escape(kw) for kw in self.FINANCIAL_KEYWORDS])
        self.financial_regex = re.compile(
            r'\b(' + financial_pattern + r')\b',
            re.IGNORECASE
        )
    
    def is_greeting(self, query: str) -> bool:
        """
        Check if the query is a greeting.
        
        Args:
            query: User's query string
            
        Returns:
            True if query is a greeting
        """
        query = query.strip()
        
        # Check for exact short greetings
        if len(query) <= 20 and self.greeting_regex.search(query):
            # Make sure it's not part of a larger financial query
            if not self.financial_regex.search(query):
                return True
        
        return False
    
    def is_in_scope(self, query: str) -> bool:
        """
        Check if the query is related to finance/trading/stock market.
        
        Args:
            query: User's query string
            
        Returns:
            True if query is in scope (financial)
        """
        query_lower = query.lower()
        
        # Check for financial keywords
        if self.financial_regex.search(query_lower):
            return True
        
        # Check for specific financial question patterns
        financial_question_patterns = [
            r'\b(should\s+i\s+(buy|sell|invest))\b',
            r'\b(how\s+(is|are)\s+the\s+market)',
            r'\b(what.*?(going\s+up|going\s+down|trending))\b',
            r'\b(price\s+of|value\s+of)\b',
        ]
        
        for pattern in financial_question_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False
    
    def classify_query(self, query: str) -> Tuple[str, Optional[str]]:
        """
        Classify a query and return appropriate response.
        
        Args:
            query: User's query string
            
        Returns:
            Tuple of (classification, response)
            - classification: 'greeting', 'out_of_scope', or 'in_scope'
            - response: Pre-generated response for greeting/out_of_scope, None for in_scope
        """
        query = query.strip()
        
        if not query:
            return ('out_of_scope', self.OUT_OF_SCOPE_RESPONSES['default'])
        
        # Check for greeting
        if self.is_greeting(query):
            # Use first greeting response (can be randomized if desired)
            logger.info(f"Classified as greeting: '{query}'")
            return ('greeting', self.GREETING_RESPONSES[0])
        
        # Check for specific out-of-scope categories BEFORE checking in-scope
        # This prevents "today" in "weather today" from triggering financial classification
        query_lower = query.lower()
        
        # Personal questions
        if any(word in query_lower for word in ['who are you', 'what are you', 'your name', 'tell me about yourself']):
            logger.info(f"Classified as out-of-scope (personal): '{query}'")
            return ('out_of_scope', self.OUT_OF_SCOPE_RESPONSES['personal'])
        
        # Weather (check before financial because might contain "today", "current", etc.)
        if any(word in query_lower for word in ['weather', 'temperature', 'rain', 'sunny', 'cloudy', 'forecast']):
            logger.info(f"Classified as out-of-scope (weather): '{query}'")
            return ('out_of_scope', self.OUT_OF_SCOPE_RESPONSES['weather'])
        
        # Entertainment (unless it's about companies/stocks)
        if any(word in query_lower for word in ['movie', 'film', 'music', 'song']) and 'company' not in query_lower and 'stock' not in query_lower:
            logger.info(f"Classified as out-of-scope (entertainment): '{query}'")
            return ('out_of_scope', self.OUT_OF_SCOPE_RESPONSES['entertainment'])
        
        # Sports (unless it's about sports companies/stocks)
        if any(word in query_lower for word in ['football match', 'soccer match', 'game score', 'sports game']) and 'company' not in query_lower and 'stock' not in query_lower:
            logger.info(f"Classified as out-of-scope (sports): '{query}'")
            return ('out_of_scope', self.OUT_OF_SCOPE_RESPONSES['general'])
        
        # Check if in scope (financial)
        if self.is_in_scope(query):
            logger.info(f"Classified as in-scope (financial): '{query}'")
            return ('in_scope', None)
        
        # Default out-of-scope
        logger.info(f"Classified as out-of-scope (general): '{query}'")
        return ('out_of_scope', self.OUT_OF_SCOPE_RESPONSES['general'])
    
    def get_response_metadata(self, classification: str) -> Dict:
        """
        Get metadata for the response based on classification.
        
        Args:
            classification: 'greeting', 'out_of_scope', or 'in_scope'
            
        Returns:
            Dict with metadata
        """
        return {
            'classification': classification,
            'articles_retrieved': False,
            'llm_used': False,
            'is_direct_response': classification in ['greeting', 'out_of_scope']
        }
