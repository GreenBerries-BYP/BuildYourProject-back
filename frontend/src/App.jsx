// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Landing from './pages/Landing';


//App.jsx faz o roteamento da aplicação, definindo as rotas para as páginas de login e registro.
// Ele utiliza o BrowserRouter do react-router-dom para gerenciar as rotas da aplicação.

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;