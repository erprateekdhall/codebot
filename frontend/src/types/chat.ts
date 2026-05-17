// Chat types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: CodeSource[];
  gitInfo?: GitInfo[];
}

export interface CodeSource {
  file: string;
  function: string;
  start_line: number;
  end_line: number;
  code: string;
  relevance_score?: number;
}

export interface GitInfo {
  author: string;
  date: string;
  message: string;
  commit?: string;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatRequest {
  message: string;
  conversation_id: string;
}

export interface ChatResponse {
  response: string;
  sources?: CodeSource[];
  git_info?: GitInfo[];
  intent?: string;
  confidence?: string;
}
