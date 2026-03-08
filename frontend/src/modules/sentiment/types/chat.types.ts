// Type definitions for chat-related data structures

export interface Message {
  id?: number;
  message: string;
  isUser: boolean;
  timestamp: number | string;
  sources?: NewsSource[] | null;
  metadata?: MessageMetadata | null;
  plots?: Plot[] | null;
  products?: any | null;
}

export interface Conversation {
  id: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  title?: string;
}

export interface NewsSource {
  title: string;
  url?: string;
  link?: string;
  snippet?: string;
  summary?: string;
  date?: string;
  sentiment?: 'positive' | 'negative' | 'neutral';
  relevance_score?: number;
}

export interface MessageMetadata {
  responseTime?: number;
  confidence?: number;
  contextUsed?: boolean;
  sourceCount?: number;
  timestamp?: string;
  source?: string;
  contexts?: any[];
  [key: string]: any;
}

export interface Plot {
  id?: string;
  title: string;
  description?: string;
  plot_type?: string;
  image_url?: string;
  created_at?: string;
  keywords?: string[];
  relevance_score?: number;
}

export interface ChatResponse {
  message?: string;
  answer?: string;
  conversationId?: string;
  sources?: NewsSource[];
  plots?: Plot[];
  metadata?: MessageMetadata;
  success?: boolean;
  error?: string;
  healthy?: boolean;
  products?: any;
}

export interface ConversationHistory {
  user_id: string;
  conversations: Conversation[];
}

export type ConnectionStatus = 'connected' | 'disconnected' | 'checking' | 'unknown';

export interface ServiceHealth {
  status: string;
  healthy?: boolean;
  index?: {
    chunks: number;
  };
}
