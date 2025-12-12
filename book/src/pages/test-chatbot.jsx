import React from 'react';
import Layout from '@theme/Layout';
import ChatbotWidget from '../components/ChatbotWidget';

export default function TestChatbotPage() {
  return (
    <Layout title="Test Chatbot" description="Test page for the chatbot widget">
      <div style={{ padding: '20px' }}>
        <h1>Physical AI & Humanoid Robotics Course - Test Page</h1>
        <p>This is a test page to verify the chatbot widget integration.</p>
        <p>Select any text on this page and the chatbot will be able to use it as context for your questions.</p>
        <p>Try selecting this text and asking the chatbot a question!</p>

        <h2>Course Topics</h2>
        <ul>
          <li>Physical AI Foundations</li>
          <li>Control Systems & Hardware</li>
          <li>Mechanical Design & Motion</li>
          <li>Human-AI Collaboration</li>
        </ul>

        <p>The chatbot widget should appear as a floating button on the bottom right of the screen.</p>
      </div>
    </Layout>
  );
}