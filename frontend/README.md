# StockSense - Stock Market Decision Support System

A modern React frontend application for a microservices-based stock market decision support system. Built with React, TypeScript, Vite, and Tailwind CSS.

## Features

- **Stock Valuation**: DCF-based intrinsic value calculation
- **Sentiment Analysis**: AI-powered market sentiment with chatbot interface
- **Fraud Detection**: Real-time suspicious trading pattern detection
- **Smart Recommendations**: Personalized stock recommendations based on risk profile

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool with SWC
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first styling

## Project Structure

```
src/
├── app/
│   ├── layouts/          # Layout components (Public, Private)
│   └── routes.tsx        # Centralized routing configuration
├── modules/
│   ├── core/             # Shared pages (Home, About, Contact, NotFound)
│   ├── componentA/       # Valuation Service module
│   ├── componentB/       # Sentiment Chatbot module
│   ├── componentC/       # Fraud Detection module
│   └── componentD/       # Recommendation module
├── shared/
│   ├── components/       # Reusable UI components
│   ├── types/           # Shared TypeScript types
│   └── utils/           # Utility functions
└── services/            # API service layer
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your backend API URLs

### Development

Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Module Structure

Each service module follows this structure:

```
componentX/
├── pages/         # Feature pages
├── components/    # Module-specific components
├── hooks/         # Custom React hooks
└── types/         # TypeScript interfaces
```

## API Configuration

Backend service URLs are configured in `src/services/api.ts`. Update the following environment variables:

- `VITE_VALUATION_API_URL` - Valuation service
- `VITE_SENTIMENT_API_URL` - Sentiment chatbot service
- `VITE_FRAUD_API_URL` - Fraud detection service
- `VITE_RECOMMENDATION_API_URL` - Recommendation service

## Styling Guidelines

- Use Tailwind utility classes for all styling
- Reusable components are in `src/shared/components`
- Follow mobile-first responsive design
- Keep custom CSS minimal

## Contributing

This is a group project. When adding features:

1. Keep module code isolated
2. Use TypeScript strictly
3. Follow the existing folder structure
4. Update types as needed
5. Keep components small and readable

## License

MIT

