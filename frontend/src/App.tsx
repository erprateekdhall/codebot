import React from 'react';
import { MainLayout } from './components/Layout/MainLayout';
import { ChatWindow } from './components/Chat/ChatWindow';
import { SearchPanel } from './components/Search/SearchPanel';
import { DashboardPanel } from './components/Dashboard/DashboardPanel';
import { HistoryPanel } from './components/History/HistoryPanel';
import { ChatProvider, useChatContext } from './context/ChatContext';

const AppContent: React.FC = () => {
  const {
    activeConversation,
    conversations,
    createConversation,
    loadConversation,
    deleteConversation,
    updateMessages,
  } = useChatContext();

  return (
    <MainLayout>
      {(activeTab) => {
        switch (activeTab) {
          case 'chat':
            return (
              <ChatWindow
                conversationId={activeConversation?.id || ''}
                messages={activeConversation?.messages || []}
                onNewConversation={createConversation}
                onMessagesUpdate={updateMessages}
              />
            );
          case 'search':
            return <SearchPanel />;
          case 'dashboard':
            return <DashboardPanel />;
          case 'history':
            return (
              <HistoryPanel
                conversations={conversations}
                activeConversationId={activeConversation?.id}
                onSelectConversation={loadConversation}
                onDeleteConversation={deleteConversation}
              />
            );
          default:
            return <div>Unknown tab</div>;
        }
      }}
    </MainLayout>
  );
};

const App: React.FC = () => {
  return (
    <ChatProvider>
      <AppContent />
    </ChatProvider>
  );
};

export default App;
