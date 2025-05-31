import React, { useState } from 'react';
import api from '../api/api';
import '../styles/LoginCadastro.css';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();



  // Handle register faz a requisição para o backend para registrar um novo usuário.
  // Ele utiliza o axios para fazer a requisição POST para a rota /register/ do backend.
  const handleRegister = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }

    if (!acceptTerms) {
      setError('Você precisa aceitar os termos de uso e políticas de privacidade.');
      return;
    }

    try {
      const response = await api.post('/register/', {
        full_name: fullName,
        username,
        email,
        password
      });
      console.log('Cadastro realizado:', response.data);
      navigate('/login'); // Redireciona para a página de login após o cadastro
    } catch (err) {
      setError('Erro ao cadastrar. Verifique os dados e tente novamente.');
    }
  };

  return (
    <div className="container-fluid my-5 d-flex justify-content-center align-items-center">
      <div className="col-lg-5 col-9 rounded p-5 h-100 d-flex flex-column justify-content-between bg-white">
        <img className="row logo-h align-self-center" src="/imgs/logo_vert_BYP.svg" alt="logo BYP" />

        <form
          className="row p-5 m-5 h-100 d-flex flex-column justify-content-between"
          onSubmit={handleRegister}
        >
          <label className="row mt-3" htmlFor="fullName">Nome completo:</label>
          <input
            className="row input-text"
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Digite seu nome completo"
          />

          <label className="row mt-3" htmlFor="username">Usuário:</label>
          <input
            className="row input-text"
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Digite seu nome de usuário"
          />

          <label className="row mt-3" htmlFor="email">Email:</label>
          <input
            className="row input-text"
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Digite seu email"
          />

          <label className="row mt-3" htmlFor="password">Senha:</label>
          <input
            className="row input-text"
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Digite sua senha"
          />

          <label className="row mt-3" htmlFor="confirmPassword">Confirmar Senha:</label>
          <input
            className="row input-text"
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirme sua senha"
          />

          <span className="row py-5 d-flex align-items-center align-self-center">
            <input
              className="col-1 check"
              type="checkbox"
              id="acceptTerms"
              checked={acceptTerms}
              onChange={(e) => setAcceptTerms(e.target.checked)}
            />
            <label className="col check-label" htmlFor="acceptTerms">
              Ao criar uma conta nessa aplicação eu declaro que aceito os
              <a href="/terms" target="_blank"> termos de uso </a>
              e as
              <a href="/politics" target="_blank"> políticas de privacidade</a>.
            </label>
          </span>

          {error && (
            <div className="row mb-5 alert alert-danger mt-3" style={{ fontSize: '1.8rem' }}>
              {error}
            </div>
          )}

          <div className="row px-5 d-flex justify-content-between text-center">
            <button className="col btn-cadastro" type="submit">Realizar cadastro</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
