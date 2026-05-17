import React, { useState, useEffect } from 'react';
import { GitBranch, FileCode, GitCommit, Database } from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { repoService } from '../../services/repoService';
import type { RepoStatus, HealthCheck } from '../../types/repo';

export const DashboardPanel: React.FC = () => {
  const [repoStatus, setRepoStatus] = useState<RepoStatus | null>(null);
  const [healthCheck, setHealthCheck] = useState<HealthCheck | null>(null);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [status, health] = await Promise.all([
        repoService.getStatus(),
        repoService.getHealth(),
      ]);
      setRepoStatus(status);
      setHealthCheck(health);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleIndex = async () => {
    setIsIndexing(true);
    try {
      await repoService.triggerIndex();
      // Wait a bit then refresh
      setTimeout(loadData, 2000);
    } catch (error) {
      console.error('Failed to trigger indexing:', error);
    } finally {
      setIsIndexing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-dark-800">Repository Dashboard</h2>
        <Button onClick={handleIndex} disabled={isIndexing}>
          {isIndexing ? 'Indexing...' : 'Re-index Repository'}
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Branch Info */}
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-primary-100 rounded-lg">
              <GitBranch className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="text-sm text-dark-500">Current Branch</p>
              <p className="text-lg font-semibold text-dark-800">
                {repoStatus?.current_branch || 'N/A'}
              </p>
            </div>
          </div>
        </Card>

        {/* Files */}
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <FileCode className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-dark-500">Indexed Files</p>
              <p className="text-lg font-semibold text-dark-800">
                {repoStatus?.indexed_files || 0}
              </p>
            </div>
          </div>
        </Card>

        {/* Commits */}
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <GitCommit className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-dark-500">Latest Commit</p>
              <p className="text-lg font-semibold text-dark-800 font-mono">
                {repoStatus?.latest_commit.substring(0, 7) || 'N/A'}
              </p>
            </div>
          </div>
        </Card>

        {/* Status */}
        <Card className="p-4">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-dark-500">System Status</p>
              <p className="text-lg font-semibold text-green-600">
                {healthCheck?.status === 'healthy' ? 'Healthy' : 'Error'}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* System Health */}
      {healthCheck && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-dark-800 mb-4">
            System Health
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(healthCheck.checks).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between p-3 bg-dark-50 rounded-lg">
                <span className="text-sm font-medium text-dark-700 capitalize">
                  {key.replace('_', ' ')}
                </span>
                <span
                  className={`text-sm font-semibold ${
                    value === 'ok' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {value === 'ok' ? '✓ OK' : '✗ Error'}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Repository Info */}
      {repoStatus && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-dark-800 mb-4">
            Repository Information
          </h3>
          <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-dark-500">Last Sync</dt>
              <dd className="text-base font-medium text-dark-800">
                {new Date(repoStatus.last_sync).toLocaleString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-dark-500">Total Commits</dt>
              <dd className="text-base font-medium text-dark-800">
                {repoStatus.total_commits}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-dark-500">Syncing Status</dt>
              <dd className="text-base font-medium text-dark-800">
                {repoStatus.is_syncing ? (
                  <span className="text-yellow-600">In Progress</span>
                ) : (
                  <span className="text-green-600">Idle</span>
                )}
              </dd>
            </div>
          </dl>
        </Card>
      )}
    </div>
  );
};
