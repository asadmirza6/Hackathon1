import React from 'react';
import ChatbotWidget from '../components/ChatbotWidget';

const LayoutWrapper = ({ children }) => {
  return (
    <>
      {children}
      <ChatbotWidget />
    </>
  );
};

export default LayoutWrapper;