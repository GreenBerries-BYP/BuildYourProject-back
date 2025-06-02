import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

import './styles/Main.css';

// Main.jsx é o ponto de entrada da aplicação React. Ele importa o React e o ReactDOM, além do componente App.

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
