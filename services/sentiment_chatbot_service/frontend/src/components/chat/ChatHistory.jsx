import React from 'react';
import { MessageSquare, Trash2, Plus, Calendar } from 'lucide-react';

const ChatHistory = ({ 
  isOpen, 
  conversations, 
  currentConversationId, 
  onSelectConversation, 
  onNewConversation,
  onDeleteConversation 
}) => {
  if (!isOpen) return null;

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getConversationTitle = (conversation) => {
    if (conversation.title) return conversation.title;
    
    // Generate title from first user message
    const firstUserMsg = conversation.messages.find(m => m.isUser);
    if (firstUserMsg) {
      return firstUserMsg.message.slice(0, 40) + (firstUserMsg.message.length > 40 ? '...' : '');
    }
    return 'New Conversation';
  };

  const groupConversationsByDate = () => {
    const groups = {
      today: [],
      yesterday: [],
      thisWeek: [],
      older: []
    };

    conversations.forEach(conv => {
      const date = new Date(conv.createdAt);
      const now = new Date();
      const diff = now - date;
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));

      if (days === 0) groups.today.push(conv);
      else if (days === 1) groups.yesterday.push(conv);
      else if (days < 7) groups.thisWeek.push(conv);
      else groups.older.push(conv);
    });

    return groups;
  };

  const groups = groupConversationsByDate();

  return (
    <div
      className="
        fixed top-0 left-0 bottom-0 z-50
        w-72 bg-white border-r border-gray-200
        shadow-2xl transform transition-transform duration-300
        flex flex-col
      "
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-purple-600 to-pink-600">
        <h2 className="text-white font-semibold text-lg flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          Chat History
        </h2>
        <p className="text-white text-xs mt-1 opacity-90">
          {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* New Chat Button */}
      <div className="p-3 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="
            w-full flex items-center justify-center gap-2
            bg-gradient-to-r from-purple-600 to-pink-600
            text-white py-2.5 px-4 rounded-lg
            hover:opacity-90 transition-opacity
            font-medium text-sm
          "
        >
          <Plus className="w-4 h-4" />
          New Conversation
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-3" style={{ scrollbarWidth: 'thin' }}>
        {conversations.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p className="text-sm">No conversations yet</p>
            <p className="text-xs mt-1">Start chatting to see history</p>
          </div>
        ) : (
          <>
            {/* Today */}
            {groups.today.length > 0 && (
              <div className="mb-4">
                <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Today
                </h3>
                {groups.today.map(conv => (
                  <ConversationItem
                    key={conv.id}
                    conversation={conv}
                    isActive={conv.id === currentConversationId}
                    onSelect={() => onSelectConversation(conv.id)}
                    onDelete={() => onDeleteConversation(conv.id)}
                    getTitle={getConversationTitle}
                    formatDate={formatDate}
                  />
                ))}
              </div>
            )}

            {/* Yesterday */}
            {groups.yesterday.length > 0 && (
              <div className="mb-4">
                <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Yesterday
                </h3>
                {groups.yesterday.map(conv => (
                  <ConversationItem
                    key={conv.id}
                    conversation={conv}
                    isActive={conv.id === currentConversationId}
                    onSelect={() => onSelectConversation(conv.id)}
                    onDelete={() => onDeleteConversation(conv.id)}
                    getTitle={getConversationTitle}
                    formatDate={formatDate}
                  />
                ))}
              </div>
            )}

            {/* This Week */}
            {groups.thisWeek.length > 0 && (
              <div className="mb-4">
                <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  This Week
                </h3>
                {groups.thisWeek.map(conv => (
                  <ConversationItem
                    key={conv.id}
                    conversation={conv}
                    isActive={conv.id === currentConversationId}
                    onSelect={() => onSelectConversation(conv.id)}
                    onDelete={() => onDeleteConversation(conv.id)}
                    getTitle={getConversationTitle}
                    formatDate={formatDate}
                  />
                ))}
              </div>
            )}

            {/* Older */}
            {groups.older.length > 0 && (
              <div className="mb-4">
                <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2 flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Older
                </h3>
                {groups.older.map(conv => (
                  <ConversationItem
                    key={conv.id}
                    conversation={conv}
                    isActive={conv.id === currentConversationId}
                    onSelect={() => onSelectConversation(conv.id)}
                    onDelete={() => onDeleteConversation(conv.id)}
                    getTitle={getConversationTitle}
                    formatDate={formatDate}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

// Conversation Item Component
const ConversationItem = ({ 
  conversation, 
  isActive, 
  onSelect, 
  onDelete, 
  getTitle, 
  formatDate 
}) => {
  const [showDelete, setShowDelete] = React.useState(false);

  return (
    <div
      className={`
        relative group mb-2 rounded-lg transition-all cursor-pointer
        ${isActive 
          ? 'bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-300' 
          : 'bg-gray-50 border border-gray-200 hover:bg-gray-100'
        }
      `}
      onClick={onSelect}
      onMouseEnter={() => setShowDelete(true)}
      onMouseLeave={() => setShowDelete(false)}
    >
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h4 className={`
              text-sm font-medium truncate
              ${isActive ? 'text-purple-900' : 'text-gray-900'}
            `}>
              {getTitle(conversation)}
            </h4>
            <p className="text-xs text-gray-500 mt-0.5">
              {conversation.messages.length} message{conversation.messages.length !== 1 ? 's' : ''}
            </p>
          </div>
          
          {showDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (window.confirm('Delete this conversation?')) {
                  onDelete();
                }
              }}
              className="
                p-1.5 rounded-md
                bg-red-100 hover:bg-red-200
                text-red-600 hover:text-red-700
                transition-colors opacity-0 group-hover:opacity-100
              "
              aria-label="Delete conversation"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
        
        <p className="text-xs text-gray-400 mt-1.5">
          {formatDate(conversation.createdAt)}
        </p>
      </div>
    </div>
  );
};

export default ChatHistory;
