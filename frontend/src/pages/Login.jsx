import React, { useState } from "react";
import api from "../api/api";
import { saveToken } from "../auth/auth";
import { useNavigate, Link } from "react-router-dom";

import "../styles/LoginCadastro.css";
import { useTranslation } from "react-i18next";

const Login = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErro("");

    try {
      const res = await api.post("/login/", { email, password: senha });
      saveToken(res.data.access);
      setTimeout(() => navigate("/home"), 300);
    } catch {
      setErro(
        t(
          "login.invalidCredentials",
          "Invalid credentials. Check your email and password."
        )
      );
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
              alt={t("altText.puzzlePeople", "Two people doing a puzzle")}
              className="img-fluid"
            />
          </div>

          <div className="col-12 col-lg-5 d-flex flex-column">
            <img
              className="logo-h align-self-center mb-4"
              src="/imgs/logo_vert_BYP.svg"
              alt={t("altText.logoBYPVertical", "BYP Vertical Logo")}
            />

            <form
              className="row p-4 d-flex justify-content-between flex-column gap-3"
              onSubmit={handleLogin}
            >
              <div>
                <label htmlFor="email">{t("login.emailLabel", "Email")}</label>
                <input
                  className="input-text"
                  type="email"
                  id="email"
                  placeholder={t(
                    "login.emailPlaceholder",
                    "example@domain.com"
                  )}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>

              <div>
                <label htmlFor="senha">
                  {t("login.passwordLabel", "Password")}
                </label>
                <input
                  className="input-text"
                  type="password"
                  id="senha"
                  placeholder={t(
                    "login.passwordPlaceholder",
                    "Enter your password"
                  )}
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                  required
                />
                {erro && (
                  <div className="alert alert-danger text-center">{erro}</div>
                )}
              </div>

              <div className="d-flex justify-content-end">
                <Link className="link-esqueci" to="/forgot_password">
                  {t(
                    "login.forgotPasswordLink",
                    "I forgot or want to change my password"
                  )}
                </Link>
              </div>

              <div className="d-flex align-items-center">
                <input
                  className="check-form me-2"
                  type="checkbox"
                  id="manter_logado"
                />
                <label className="check-label" htmlFor="manter_logado">
                  {t("login.keepLoggedIn", "Keep me logged in")}
                </label>
              </div>

              <div className="d-flex justify-content-between gap-5">
                <button
                  className="btn-change-page flex-fill text-center"
                  onClick={() => navigate("/register")}
                >
                  {t("login.register")}
                </button>

                <button
                  className="btn-acesso-verde flex-fill d-flex justify-content-center align-items-center"
                  type="submit"
                  disabled={loading}
                >
                  {loading ? (
                    <div
                      className="spinner-border text-light"
                      style={{ width: "2rem", height: "2rem" }}
                      role="status"
                    >
                      <span className="visually-hidden">
                        {t("login.loading", "Loading...")}
                      </span>
                    </div>
                  ) : (
                    t("login.signIn")
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
