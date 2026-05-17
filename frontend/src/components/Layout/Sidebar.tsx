import React from 'react';
import { MessageSquare, Search, LayoutDashboard, History } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const menuItems = [
    { id: 'chat', icon: MessageSquare, label: 'Chat' },
    { id: 'search', icon: Search, label: 'Search' },
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'history', icon: History, label: 'History' },
  ];

  return (
    <div className="w-64 bg-dark-900 text-white h-screen flex flex-col">
      {/* Logo/Title */}
      <div className="p-6 border-b border-dark-700">
        <h1 className="text-2xl font-bold text-primary-400">CodeBot AI</h1>
        <p className="text-sm text-dark-400 mt-1">Intelligent Code Analysis</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center px-6 py-3 text-left transition-colors ${
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-dark-300 hover:bg-dark-800 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-dark-700 text-dark-400 text-xs">
        <p>&copy; 2024 CodeBot AI</p>
        <p className="mt-1">Powered by Claude & FastAPI</p>
      </div>
    </div>
  );
};
