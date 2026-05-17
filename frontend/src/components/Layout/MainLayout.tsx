import React, { useState, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { repoService } from '../../services/repoService';
import type { RepoStatus, HealthCheck } from '../../types/repo';

interface MainLayoutProps {
  children: (activeTab: string) => React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [activeTab, setActiveTab] = useState('chat');
  const [repoStatus, setRepoStatus] = useState<RepoStatus | null>(null);
  const [systemHealth, setSystemHealth] = useState<HealthCheck | null>(null);

  useEffect(() => {
    // Load initial data
    loadRepoStatus();
    loadSystemHealth();

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      loadRepoStatus();
      loadSystemHealth();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadRepoStatus = async () => {
    try {
      const status = await repoService.getStatus();
      setRepoStatus(status);
    } catch (error) {
      console.error('Failed to load repo status:', error);
    }
  };

  const loadSystemHealth = async () => {
    try {
      const health = await repoService.getHealth();
      setSystemHealth(health);
    } catch (error) {
      console.error('Failed to load system health:', error);
    }
  };

  return (
    <div className="flex h-screen bg-dark-50">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header repoStatus={repoStatus} systemHealth={systemHealth} />
        <main className="flex-1 overflow-auto">
          {children(activeTab)}
        </main>
      </div>
    </div>
  );
};
