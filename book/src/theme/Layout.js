import React from 'react';
import OriginalLayout from '@theme-original/Layout';
import SimpleChatbotWidget from '../components/ChatbotWidget/SimpleChatbotWidget';

export default function Layout(props) {
  return (
    <>
      <OriginalLayout {...props} />
      <SimpleChatbotWidget />
    </>
  );
}