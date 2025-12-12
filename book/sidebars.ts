import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Hardcoded 4 chapters × 2 lessons structure (immutable per constitution)
  default: [
    {
      type: 'category',
      label: 'Chapter 1: Physical AI Foundations',
      items: [
        'chapter-1/lesson-1',  // Physical AI Basics
        'chapter-1/lesson-2',  // Humanoid Robotics Overview
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Chapter 2: Control & Hardware',
      items: [
        'chapter-2/lesson-1',  // Control Systems
        'chapter-2/lesson-2',  // Sensors & Actuators
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Chapter 3: Mechanical Design & Motion',
      items: [
        'chapter-3/lesson-1',  // Humanoid Mechanical Design
        'chapter-3/lesson-2',  // Locomotion & Planning
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Chapter 4: Human-AI Collaboration',
      items: [
        'chapter-4/lesson-1',  // Human-AI Interaction
        'chapter-4/lesson-2',  // Future of Physical AI
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'AI Assistant',
      items: [
        'chatbot-integration',
      ],
      collapsed: false,
    },
  ],
};

export default sidebars;
