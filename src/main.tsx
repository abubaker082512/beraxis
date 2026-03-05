import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

console.log("Beraxis main.tsx: Loading...");
const rootElement = document.getElementById('root');
if (rootElement) {
  console.log("Beraxis main.tsx: Found root, rendering App.");
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
} else {
  console.error("Beraxis main.tsx: Root element not found!");
}
