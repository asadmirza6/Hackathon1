import React, { useState } from 'react';

const SimpleChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 1000 }}>
      <button
        onClick={toggleChat}
        style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: '#4f6fef',
          color: 'white',
          border: 'none',
          fontSize: '16px',
          cursor: 'pointer'
        }}
      >
        {isOpen ? 'X' : 'AI'}
      </button>

      {isOpen && (
        <div style={{
          width: '300px',
          height: '400px',
          backgroundColor: 'white',
          border: '1px solid #ccc',
          borderRadius: '8px',
          marginTop: '10px'
        }}>
          <div style={{ padding: '10px', backgroundColor: '#4f6fef', color: 'white' }}>
            <span>AI Assistant</span>
            <button
              onClick={toggleChat}
              style={{ float: 'right', background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}
            >
              X
            </button>
          </div>
          <div style={{ padding: '10px', height: '300px', overflowY: 'auto' }}>
            <p>Hello! I'm your AI assistant.</p>
          </div>
          <div style={{ padding: '10px', borderTop: '1px solid #eee' }}>
            <input
              type="text"
              placeholder="Ask a question..."
              style={{ width: 'calc(100% - 40px)', padding: '8px' }}
            />
            <button style={{ marginLeft: '5px', padding: '8px' }}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleChatbotWidget;