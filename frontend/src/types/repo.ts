// Repository types
export interface RepoStatus {
  total_files: number;
  indexed_files: number;
  last_sync: string;
  current_branch: string;
  latest_commit: string;
  total_commits: number;
  is_syncing: boolean;
}

export interface HealthCheck {
  status: string;
  checks: {
    rag_engine: string;
    static_analyzer: string;
    git_analyzer: string;
  };
}

export interface IndexResponse {
  message: string;
  status: string;
}
