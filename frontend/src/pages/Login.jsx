import React, { useState } from 'react'; 
import api from '../api/api';
import { saveToken } from '../auth/auth';

const Login = () => {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/login/', {
        email,
        password: senha,
      });
      saveToken(res.data.access);
      alert('Login realizado!');
    } catch (err) {
      setErro('Credenciais inválidas.');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Login</h2>
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required />
      <input type="password" value={senha} onChange={e => setSenha(e.target.value)} placeholder="Senha" required />
      <button type="submit">Entrar</button>
      {erro && <p style={{ color: 'red' }}>{erro}</p>}
    </form>
  );
};

export default Login;

//Feito com ia
