/**
 * ChatContainer Component
 * Simplified wrapper around AIChat for backward compatibility
 */

import React from 'react';
import AIChat from './AIChat';

const ChatContainer: React.FC = () => {
  return <AIChat />;
};

export default ChatContainer;
