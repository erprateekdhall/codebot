// Search types
export interface SearchRequest {
  query: string;
  max_results?: number;
}

export interface SearchResult {
  file: string;
  function: string;
  start_line: number;
  end_line: number;
  code: string;
  relevance_score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
}
