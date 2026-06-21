/**
 * Application entry point.
 *
 * Imports the accessibility stylesheet and mounts the React app.
 * Conditionally loads axe-core for development accessibility auditing.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/accessibility.css';
import './index.css';

// Load axe-core accessibility auditing in development only
if (import.meta.env.DEV) {
  import('@axe-core/react').then((axe) => {
    axe.default(React, ReactDOM, 1000);
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
