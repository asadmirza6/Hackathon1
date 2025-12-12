import React, { useState, useEffect, useRef } from 'react';
import './ChatbotWidget.css';

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState(null);
  const messagesEndRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to get selected text from the page
  const getSelectedText = () => {
    const selectedText = window.getSelection().toString().trim();
    return selectedText || null;
  };

  // Handle sending a message
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { id: Date.now(), text: inputValue, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Get any selected text from the page
    const pageSelectedText = getSelectedText();
    const contextToUse = selectedText || pageSelectedText || null;

    try {
      const response = await fetch(`${API_BASE_URL}/v1/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputValue,
          session_id: 'web-user-' + Date.now(),
          selected_context: contextToUse,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const botMessage = {
        id: Date.now() + 1,
        text: data.response_text,
        sender: 'bot',
        sources: data.source_references,
        confidence: data.confidence_score,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        error: true,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setSelectedText(null); // Clear selected text after sending
    }
  };

  // Function to handle text selection on the page
  useEffect(() => {
    const handleSelection = () => {
      const selectedText = window.getSelection().toString().trim();
      if (selectedText) {
        setSelectedText(selectedText);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, []);

  // Toggle chat window
  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  // Clear chat history
  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="chatbot-widget">
      {isOpen ? (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-title">Physical AI Assistant</div>
            <div className="chat-controls">
              <button onClick={clearChat} className="clear-btn" title="Clear chat">
                X
              </button>
              <button onClick={toggleChat} className="close-btn" title="Close chat">
                -
              </button>
            </div>
          </div>
          <div className="chat-messages">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <p>Hello! I'm your Physical AI & Humanoid Robotics assistant.</p>
                <p>Ask me anything about the course content!</p>
                {selectedText && (
                  <div className="selected-text-preview">
                    <small>Selected: "{selectedText.substring(0, 50)}..."</small>
                  </div>
                )}
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.sender}-message`}
                >
                  <div className="message-text">{message.text}</div>
                  {message.sources && message.sources.length > 0 && (
                    <div className="message-sources">
                      <small>Sources: {message.sources.map(s => `Ch.${s.chapter} L.${s.lesson}`).join(', ')}</small>
                    </div>
                  )}
                  {message.confidence && (
                    <div className="message-confidence">
                      <small>Confidence: {(message.confidence * 100).toFixed(1)}%</small>
                    </div>
                  )}
                  {message.error && (
                    <div className="message-error">
                      <small>Please check your API configuration</small>
                    </div>
                  )}
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>
          <form className="chat-input-form" onSubmit={handleSendMessage}>
            {selectedText && (
              <div className="selected-text-indicator">
                Using context: "{selectedText.substring(0, 60)}..."
                <button
                  type="button"
                  onClick={() => setSelectedText(null)}
                  className="remove-context-btn"
                >
                  X
                </button>
              </div>
            )}
            <div className="input-container">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask about Physical AI & Robotics..."
                disabled={isLoading}
                className="chat-input"
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || isLoading}
                className="send-button"
              >
                {isLoading ? 'Sending...' : '→'}
              </button>
            </div>
          </form>
        </div>
      ) : null}

      <button
        className={`chat-toggle ${isOpen ? 'open' : ''}`}
        onClick={toggleChat}
      >
        {isOpen ? 'CLOSE' : 'CHAT'}
      </button>
    </div>
  );
};

export default ChatbotWidget;