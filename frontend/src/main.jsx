import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "bootstrap/dist/css/bootstrap.min.css";
import "./styles/Main.css";

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";


// Main.jsx é o ponto de entrada da aplicação React. Ele importa o React e o ReactDOM, além do componente App.

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
