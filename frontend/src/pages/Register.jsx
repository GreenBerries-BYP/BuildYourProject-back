import React, { useState } from "react";
import api from "../api/api";
import "../styles/LoginCadastro.css";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

const Register = () => {
  const { t } = useTranslation();
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  // Handle register faz a requisição para o backend para registrar um novo usuário.
  // Ele utiliza o axios para fazer a requisição POST para a rota /register/ do backend.
  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(""); // Clear previous errors

    if (password !== confirmPassword) {
      setError(t("register.errorPasswordMismatch", "As senhas não coincidem."));
      setLoading(false);
      return;
    }

    if (!acceptTerms) {
      setError(
        t(
          "register.errorAcceptTerms",
          "Você precisa aceitar os termos de uso e políticas de privacidade."
        )
      );
      setLoading(false);
      return;
    }

    try {
      const response = await api.post("/register/", {
        full_name: fullName,
        username,
        email,
        password,
      });
      setLoading(false);
      console.log("Cadastro realizado:", response.data);
      navigate("/login"); // Redireciona para a página de login após o cadastro
    } catch (err) {
      setError(
        t(
          "register.errorRegistrationFailed",
          "Erro ao cadastrar. Verifique os dados e tente novamente."
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid my-5 d-flex justify-content-center align-items-center">
      <div className="col-lg-5 col-9 rounded p-5 h-100 d-flex flex-column justify-content-between bg-white">
        <img
          className="row logo-h align-self-center"
          src="/imgs/logo_vert_BYP.svg"
          alt={t("altText.logoBYPVertical", "BYP Vertical Logo")}
        />

        <form
          className="row p-5 m-5 h-100 d-flex flex-column justify-content-between"
          onSubmit={handleRegister}
        >
          <label className="row mt-3" htmlFor="fullName">
            {t("register.fullNameLabel", "Nome completo:")}
          </label>
          <input
            className="row input-text"
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder={t(
              "register.fullNamePlaceholder",
              "Digite seu nome completo"
            )}
          />

          <label className="row mt-3" htmlFor="username">
            {t("register.usernameLabel", "Usuário:")}
          </label>
          <input
            className="row input-text"
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder={t(
              "register.usernamePlaceholder",
              "Digite seu nome de usuário"
            )}
          />

          <label className="row mt-3" htmlFor="email">
            {t("register.emailLabel", "Email:")}
          </label>
          <input
            className="row input-text"
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder={t("register.emailPlaceholder", "Digite seu email")}
          />

          <label className="row mt-3" htmlFor="password">
            {t("register.passwordLabel", "Senha:")}
          </label>
          <input
            className="row input-text"
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={t("register.passwordPlaceholder", "Digite sua senha")}
          />

          <label className="row mt-3" htmlFor="confirmPassword">
            {t("register.confirmPasswordLabel", "Confirmar Senha:")}
          </label>
          <input
            className="row input-text"
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder={t(
              "register.confirmPasswordPlaceholder",
              "Confirme sua senha"
            )}
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
              {t(
                "register.terms.intro",
                "Ao criar uma conta nessa aplicação eu declaro que aceito os"
              )}
              <a href="/terms" target="_blank" rel="noopener noreferrer">
                {" "}
                {t("register.terms.termsLinkText", "termos de uso")}{" "}
              </a>
              {t("register.terms.and", "e as")}
              <a href="/politics" target="_blank" rel="noopener noreferrer">
                {" "}
                {t("register.terms.policyLinkText", "políticas de privacidade")}
              </a>
              .
            </label>
          </span>

          {error && (
            <div
              className="row mb-5 alert alert-danger mt-3"
              style={{ fontSize: "1.8rem" }}
            >
              {error}
            </div>
          )}

          <div className="row px-5 d-flex justify-content-center text-center gap-4">
            <button className="col btn-change-page justify-content-center" onClick={() => navigate("/login")}>
              {t("login.signIn")}
            </button>
            <button
              className="col btn-cadastro justify-content-center"
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
                    {t("login.loading")}
                  </span>
                </div>
              ) : (
                t("register.submitButton")
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;
