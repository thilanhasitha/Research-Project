/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SENTIMENT_API_URL?: string;
  readonly VITE_KNOWLEDGE_BASE_API_URL?: string;
  readonly VITE_NEWS_RAG_API_URL?: string;
  readonly VITE_API_URL?: string;
  readonly VITE_VALUATION_API_URL?: string;
  readonly VITE_FRAUD_API_URL?: string;
  readonly VITE_RECOMMENDATION_API_URL?: string;
  // Add more env variables as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
