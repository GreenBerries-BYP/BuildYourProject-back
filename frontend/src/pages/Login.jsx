import React, { useState } from 'react'; 
import api from '../api/api';
import { saveToken } from '../auth/auth';
import { useNavigate } from 'react-router-dom';

import '../styles/LoginCadastro.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [erro, setErro] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/login/', {
        email,
        password: senha,
      });
      saveToken(res.data.access);
      alert('Login realizado!');
      navigate('/home'); // Redireciona para a página inicial após o login
    } catch (err) {
      setErro('Credenciais inválidas.');
    }
  };

  return (
    
    <div className="container-fluid login d-flex justify-content-center align-items-center p-0">
      <div className="col-10 card-login rounded d-flex justify-content-center align-items-center bg-white">
        <div className="row w-100 justify-content-center">
          <div className="col-12 col-lg-6 d-none d-lg-flex justify-content-center align-items-center">
            <img
              src="/imgs/problem-solving.svg"
              alt="duas pessoas unindo peças de quebra-cabeça "
            />
          </div>

          <div className="col-12 col-lg-5 d-flex flex-column ">
            <img
              className="row logo-h align-self-center"
              src="/imgs/logo_vert_BYP.svg"
              alt="logo amigosConnect"
            />

            <form
              className="mt-5 row p-5 h-100 d-flex flex-column"
              onSubmit={handleLogin}
              method="POST"
            >
              <div className="row d-flex flex-column">
                <label htmlFor="email">Email:</label>
                <input
                  className="input-text"
                  type="text"
                  name="email"
                  id="email"
                  placeholder="Digite seu email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>


              <div className="row d-flex flex-column">
                <label htmlFor="senha">Senha:</label>
                <input
                  className="input-text"
                  type="password"
                  name="senha"
                  id="senha"
                  placeholder="Digite sua senha"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  required
                />
              </div>

              {erro && (
                <div
                  className="row my-3 alert alert-danger"
                  style={{ fontSize: '1.8rem' }}
                  role="alert"
                >
                  {erro}
                </div>
              )}

              <a
                className="py-5 row link-esqueci align-self-end"
                href="/forgot_password"
              >
                esqueci ou quero alterar minha senha
              </a>

              <span className="row py-5 w-75 d-flex align-items-center align-self-left">
                  <input className="col-1 check check-form" type="checkbox" name="manter-logado" id="manter_logado"/> 
                  <label className="col check-label" for="manter-logado">
                      Manter-me logado
                  </label>
              </span>

              <div className="row botoes-login d-flex justify-content-between text-center">
                <a className="col-5 link-cadastre" href="/register">
                  Cadastre-se
                </a>
                <button className="col-5 btn-acesso-verde" type="submit">
                  Entrar
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

