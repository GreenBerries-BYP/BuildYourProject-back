import React, { useState } from 'react';
import api from '../api/api';
import { saveToken } from '../auth/auth';
import { useNavigate, Link } from 'react-router-dom';

import '../styles/LoginCadastro.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErro('');

    try {
      const res = await api.post('/login/', { email, password: senha });
      saveToken(res.data.access);
      setTimeout(() => navigate('/home'), 300);
    } catch {
      setErro('Credenciais inválidas. Verifique seu e-mail e senha.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid login d-flex justify-content-center align-items-center p-0">
      <div className="col-10 card-login rounded d-flex justify-content-center align-items-center bg-white shadow-lg">
        <div className="row w-100 justify-content-center">

          <div className="col-12 col-lg-6 d-none d-lg-flex justify-content-center align-items-center">
            <img
              src="/imgs/problem-solving.svg"
              alt="Duas pessoas montando um quebra-cabeça"
              className="img-fluid"
            />
          </div>

          <div className="col-12 col-lg-5 d-flex flex-column">
            <img
              className="logo-h align-self-center mb-4"
              src="/imgs/logo_vert_BYP.svg"
              alt="Logo amigosConnect"
            />

            <form className="row p-4 d-flex flex-column gap-3" onSubmit={handleLogin}>
              <div>
                <label htmlFor="email">Email</label>
                <input
                  className="input-text"
                  type="email"
                  id="email"
                  placeholder="exemplo@dominio.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div>
                <label htmlFor="senha">Senha</label>
                <input
                  className="input-text"
                  type="password"
                  id="senha"
                  placeholder="Digite sua senha"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  required
                />
              </div>

              {erro && (
                <div className="alert alert-danger text-center py-2" role="alert">
                  {erro}
                </div>
              )}

              <div className="d-flex justify-content-end">
                <Link className="link-esqueci" to="/forgot_password">
                  Esqueci ou quero alterar minha senha
                </Link>
              </div>

              <div className="d-flex align-items-center">
                <input
                  className="check-form me-2"
                  type="checkbox"
                  id="manter_logado"
                />
                <label className="check-label" htmlFor="manter_logado">
                  Manter-me logado
                </label>
              </div>

              <div className="d-flex justify-content-between gap-3">
                <Link to="/register" className="link-cadastre flex-fill text-center">
                  Cadastre-se
                </Link>

                <button
                  className="btn-acesso-verde flex-fill d-flex justify-content-center align-items-center"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? (
                    <div
                      className="spinner-border text-light"
                      style={{ width: '2rem', height: '2rem' }}
                      role="status"
                    >
                      <span className="visually-hidden">Carregando...</span>
                    </div>
                  ) : (
                    'Entrar'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
