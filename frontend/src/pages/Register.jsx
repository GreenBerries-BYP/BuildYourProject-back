import React, { useState } from 'react';
import api from '../api/api';

const Register = () => {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState(''); 
  const [erro, setErro] = useState('');

  // Handle register faz a requisição para o backend para registrar um novo usuário.
  // Ele utiliza o axios para fazer a requisição POST para a rota /register/ do backend.
  const handleRegister = async (e) => { 
    e.preventDefault();
    try {
      await api.post('/register/', {
        email,
        password: senha,
        username,
        full_name: fullName,
      });
      alert('Cadastro realizado com sucesso!');
    } catch (err) {
      console.error(err);
      setErro('Erro ao cadastrar. Verifique os dados.');
    }
  };

  return (
    <form onSubmit={handleRegister}>
      <h2>Cadastro</h2>
      <input type="text" value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Nome completo" required />
      <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Nome de usuário" required />
      <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" required />
      <input type="password" value={senha} onChange={e => setSenha(e.target.value)} placeholder="Senha" required />
      <button type="submit">Cadastrar</button>
      {erro && <p style={{ color: 'red' }}>{erro}</p>}
    </form>
  );
};

export default Register;
