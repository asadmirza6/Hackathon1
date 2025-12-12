# Chatbot Widget Component

The ChatbotWidget is a React component that provides an AI-powered chat interface for the Physical AI & Humanoid Robotics Course. It integrates with the backend RAG system to answer questions about course content.

## Features

- **Context-aware queries**: Automatically detects selected text on the page and uses it as context
- **Real-time chat interface**: Clean, modern chat UI with message history
- **Source attribution**: Shows which chapters/lessons sources came from
- **Confidence scoring**: Displays confidence level of AI responses
- **Session management**: Maintains conversation context

## API Integration

The component communicates with the backend RAG system via:

- `/v1/query` - Main query endpoint for chat interactions
- `/v1/health` - Health check endpoint
- `/v1/logs` - Query history (for future features)
- `/v1/logs/metrics` - Analytics (for future features)

## Environment Variables

The component uses the following environment variable:

- `REACT_APP_API_BASE_URL` - Base URL for the backend API (defaults to `http://localhost:8000`)

## Usage

The component is automatically included in all pages via Docusaurus theme customization in `src/theme/Layout.js`.

## Styling

The component uses CSS modules for styling and is responsive across different screen sizes.