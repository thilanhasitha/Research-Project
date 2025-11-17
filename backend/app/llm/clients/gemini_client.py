import os
from typing import Optional, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.llms import LLM
from app.llm.LLMProvider import LLMProvider


class GeminiClient(LLMProvider):
    
    _instance: Optional['GeminiClient'] = None 
    _llm_instance: Optional[LLM] = None          
    
    def __new__(cls) -> 'GeminiClient':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._api_key = os.getenv('GEMINI_API_KEY')
            self._default_model = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')
            self._default_temperature = float(os.getenv('GEMINI_TEMPERATURE', '0.2'))
            self._default_max_tokens = int(os.getenv('GEMINI_MAX_TOKENS', '1024'))
            
            if not self._api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required")
    
    def create_llm(self, **kwargs) -> LLM:
        """
        Configuration parameters for the Gemini LLM:
            - model: Model name (default: gemini-1.5-pro)
            - temperature: Sampling temperature (default: 0.2)
            - max_output_tokens: Maximum tokens to generate (default: 1024)
            - top_p: Top-p sampling
            - stop: Stop sequences
            - convert_system_message_to_human: Convert system messages to human messages (default: True)
        """
        config = {
            'google_api_key': self._api_key,
            'model': kwargs.get('model', self._default_model),
            'temperature': kwargs.get('temperature', self._default_temperature),
            'max_output_tokens': kwargs.get('max_tokens', self._default_max_tokens),
        }
        
        optional_params = ['top_p', 'stop']
        for param in optional_params:
            if param in kwargs:
                config[param] = kwargs[param]
        
        return ChatGoogleGenerativeAI(**config)
    
    def get_llm(self) -> LLM:
        if self._llm_instance is None:
            self._llm_instance = self.create_llm()
        return self._llm_instance
    
    @property
    def current_config(self) -> Dict[str, Any]:
        return {
            'model': self._default_model,
            'temperature': self._default_temperature,
            'max_tokens': self._default_max_tokens,
            'api_key_set': bool(self._api_key),
        }
        

"""
Available Gemini models:
- "gemini-1.5-flash"  (fast, cheaper, lower latency)
- "gemini-1.5-pro"    (more capable, higher quality)
"""