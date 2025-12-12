// API client for the RAG Chatbot Backend
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

class ChatbotAPI {
  static async query(question, sessionId, selectedContext = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          session_id: sessionId,
          selected_context: selectedContext,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API query error:', error);
      throw error;
    }
  }

  static async getHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/health`);
      return await response.json();
    } catch (error) {
      console.error('API health check error:', error);
      throw error;
    }
  }

  static async getLogs(limit = 10, offset = 0) {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/logs?limit=${limit}&offset=${offset}`);
      return await response.json();
    } catch (error) {
      console.error('API logs error:', error);
      throw error;
    }
  }

  static async getMetrics(daysBack = 7) {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/logs/metrics?days_back=${daysBack}`);
      return await response.json();
    } catch (error) {
      console.error('API metrics error:', error);
      throw error;
    }
  }
}

export default ChatbotAPI;