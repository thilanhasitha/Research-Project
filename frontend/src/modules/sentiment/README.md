# Sentiment Analysis Module

## Overview
This module contains the AI-powered sentiment analysis chatbot and related components migrated from the original JavaScript implementation to TypeScript.

## Migration Status ✅

All components have been successfully migrated from:
- **Source:** `services/sentiment_chatbot_service/frontend/src/components`
- **Target:** `frontend/src/modules/sentiment/components`

### Migrated Components (9 files)

#### Chat Components (7 files)
- ✅ `AIChat.tsx` - Main chat orchestration component
- ✅ `ChatContainer.tsx` - Wrapper component for backward compatibility  
- ✅ `ChatFloatingButton.tsx` - Floating chat button with connection status
- ✅ `ChatHistory.tsx` - Conversation history sidebar
- ✅ `ChatMessage.tsx` - Individual message display with sources/plots
- ✅ `ChatPanel.tsx` - Main chat panel UI
- ✅ `QuickActions.tsx` - Quick action buttons for common queries

#### Additional Components (2 files)
- ✅ `AnnualReportQA.tsx` - Annual report Q&A interface
- ✅ `AnnualReportQA-Fetch.tsx` - Annual report Q&A with fetch API

## Structure

```
frontend/src/modules/sentiment/
├── components/
│   ├── chat/
│   │   ├── AIChat.tsx              # Main chat component
│   │   ├── ChatContainer.tsx       # Wrapper component
│   │   ├── ChatFloatingButton.tsx  # Floating button
│   │   ├── ChatHistory.tsx         # History sidebar
│   │   ├── ChatMessage.tsx         # Message display
│   │   ├── ChatPanel.tsx           # Chat panel UI
│   │   ├── QuickActions.tsx        # Quick actions
│   │   └── index.ts                # Chat exports
│   ├── AnnualReportQA.tsx          # Annual report Q&A
│   ├── AnnualReportQA-Fetch.tsx    # Annual report Q&A (fetch)
│   └── index.ts                    # Component exports
├── types/
│   ├── chat.types.ts               # Type definitions
│   └── index.ts                    # Type exports
└── pages/
    └── SentimentDashboard.tsx      # Main dashboard page
```

## Features

### AIChat Component
- Real-time AI chat interface
- Conversation history with localStorage persistence
- Connection status monitoring
- Support for news sources and plot visualizations
- Quick action buttons for common queries
- Collapsible history sidebar

### Message Display
- User/Bot message differentiation
- Source citations with sentiment analysis
- Plot/chart visualization support
- Expandable plot modal
- Timestamp display

### Quick Actions
- Market News queries
- CSE Annual Report queries
- Collapsible action groups
- Disabled state during typing

## Type Safety

All components are fully typed with TypeScript interfaces:
- `Message` - Chat message structure
- `Conversation` - Conversation data
- `NewsSource` - News article data
- `Plot` - Chart/visualization data
- `ConnectionStatus` - Connection state
- `ServiceHealth` - Health check response

## Usage

### Basic Integration

```typescript
import { AIChat } from '@/modules/sentiment/components';

function App() {
  return (
    <div>
      {/* Your app content */}
      <AIChat />
    </div>
  );
}
```

### Standalone Components

```typescript
import { 
  ChatFloatingButton, 
  ChatPanel, 
  ChatMessage 
} from '@/modules/sentiment/components/chat';

// Use individual components as needed
```

## Environment Variables

Required environment variables (add to `.env`):

```bash
# Sentiment Service API
VITE_SENTIMENT_API_URL=http://localhost:8002/api

# Knowledge Base API
VITE_KNOWLEDGE_BASE_API_URL=http://localhost:8002/api

# News RAG API  
VITE_NEWS_RAG_API_URL=http://localhost:8002/api
```

## Dependencies

Required packages (already installed):
- `react` - Core React library
- `lucide-react` - Icon components
- `tailwindcss` - Styling

## Next Steps

### TODO: API Integration
The current implementation has placeholder API calls. To complete the integration:

1. **Create Service Layer** - Add service files:
   - `services/aiResponseService.ts`
   - `services/newsRAGService.ts`
   - `services/knowledgeBaseService.ts`

2. **Replace Placeholders** in `AIChat.tsx`:
   ```typescript
   // Replace this:
   // TODO: Replace with actual API calls
   
   // With actual service imports:
   import { askQuestion } from '../../services/newsRAGService';
   import { queryKnowledgeBase } from '../../services/knowledgeBaseService';
   ```

3. **Test Backend Connection**:
   ```bash
   # Ensure sentiment service is running
   cd services/sentiment_chatbot_service
   python -m uvicorn main:app --reload --port 8002
   ```

## Development

### Running the Frontend

```bash
cd frontend
npm install  # Install dependencies (if not done)
npm run dev  # Start development server
```

### Building for Production

```bash
npm run build
```

### Type Checking

```bash
npm run build  # Runs tsc -b before building
```

## Testing Checklist

- [ ] Chat opens via floating button
- [ ] Messages send and display correctly
- [ ] Quick actions work
- [ ] Conversation history persists
- [ ] History sidebar opens/closes
- [ ] Connection status displays
- [ ] Plot visualizations render (when API connected)
- [ ] Source citations display (when API connected)
- [ ] Mobile responsive layout
- [ ] TypeScript compiles without errors

## Known Issues / Notes

1. **API Placeholders**: Currently returns simulated responses. Connect actual backend APIs.
2. **Service Health**: Hardcoded to 'connected' - implement actual health check.
3. **User Authentication**: Uses 'anonymous' user ID - integrate with auth system.
4. **Plot Service**: Needs integration with plot API endpoints.

## Migration Changes

### JavaScript → TypeScript Conversions
- Added type annotations for all props and state
- Created comprehensive type definitions
- Converted all arrow functions to typed versions
- Added proper return types
- Fixed implicit `any` types

### Import Path Updates
- Updated relative import paths for new structure
- Changed `.jsx` to `.tsx` extensions
- Added index barrel exports

### Style Improvements
- Maintained all original Tailwind CSS classes
- No visual changes from original
- Preserved all animations and transitions

## Support

For issues or questions about the sentiment module:
1. Check this README
2. Review type definitions in `types/chat.types.ts`
3. Examine the original source in `services/sentiment_chatbot_service/frontend`

---

**Migration completed:** March 6, 2026
**Migrated by:** AI Assistant
**Original source:** `services/sentiment_chatbot_service/frontend/src/components`
