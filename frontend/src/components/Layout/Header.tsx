import React from 'react';
import { Activity, GitBranch } from 'lucide-react';
import type { RepoStatus, HealthCheck } from '../../types/repo';

interface HeaderProps {
  repoStatus: RepoStatus | null;
  systemHealth: HealthCheck | null;
}

export const Header: React.FC<HeaderProps> = ({ repoStatus, systemHealth }) => {
  const isHealthy = systemHealth?.status === 'healthy';

  return (
    <header className="bg-white border-b border-dark-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Repository Info */}
        <div className="flex items-center space-x-4">
          {repoStatus && (
            <>
              <div className="flex items-center text-dark-700">
                <GitBranch className="w-4 h-4 mr-2" />
                <span className="font-medium">{repoStatus.current_branch}</span>
                <span className="ml-2 text-dark-400 text-sm">
                  {repoStatus.latest_commit.substring(0, 7)}
                </span>
              </div>
              <div className="text-sm text-dark-500">
                {repoStatus.indexed_files} files indexed
              </div>
            </>
          )}
        </div>

        {/* System Health */}
        <div className="flex items-center space-x-2">
          <Activity
            className={`w-5 h-5 ${
              isHealthy ? 'text-green-500' : 'text-red-500'
            }`}
          />
          <span
            className={`text-sm font-medium ${
              isHealthy ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {isHealthy ? 'System Online' : 'System Error'}
          </span>
        </div>
      </div>
    </header>
  );
};
