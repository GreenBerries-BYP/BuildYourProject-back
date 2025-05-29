import { useEffect, useRef, useState } from "react";
import "../styles/ModalNewProject.css";
import { getToken } from "../auth/auth"; // ⚠️ Supondo que você tenha o mesmo helper usado no login.
import { abntTemplates } from "../mocks/abntMock";
import { i18n } from "../translate/i18n";

const ModalNewProject = ({ isOpen, onClose }) => {
  const modalRef = useRef();
  const [selectedType, setSelectedType] = useState("TCC");
  const [nome, setNome] = useState("");
  const [descricao, setDescricao] = useState("");
  const [colaboradores, setColaboradores] = useState([]);
  const [emailInput, setEmailInput] = useState("");
  const [template, setTemplate] = useState(
    "Introdução, Objetivo, Conclusão..."
  );

  const [emailError, setEmailError] = useState("");
  const [formErrors, setFormErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const adicionarColaborador = () => {
    if (!emailInput.trim()) {
      setEmailError(i18n.t("messages.emailCantBeEmpty"));
      return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput)) {
      setEmailError(i18n.t("messages.invalidEmailFormat"));
      return;
    }

    if (colaboradores.includes(emailInput)) {
      setEmailError(i18n.t("messages.emailAlreadyAdded"));
      return;
    }

    setColaboradores([...colaboradores, emailInput]);
    setEmailInput("");
    setEmailError("");
  };

  const removerColaborador = (email) => {
    setColaboradores(colaboradores.filter((e) => e !== email));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      adicionarColaborador();
    }
  };

  const validateForm = () => {
    const errors = {};
    if (!nome.trim()) errors.nome = i18n.t("messages.projectNameRequired");
    if (!descricao.trim())
      errors.descricao = i18n.t("messages.projectDescriptionRequired");
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errors = validateForm();
    setFormErrors(errors);
    if (Object.keys(errors).length > 0) return;

    const projeto = {
      nome,
      descricao,
      tipo: selectedType,
      colaboradores,
      template,
    };

    setLoading(true);

    try {
      const token = getToken();

      const response = await api.post("/projetos/", projeto, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || i18n.t("messages.errorNewProject"));
      }

      onClose();
    } catch (err) {
      setFormErrors({
        submit: err.message || i18n.t("messages.errorNewProject"),
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  if (!isOpen) return null;

  const projectTypes = ["TCC", "Artigo Acadêmico", "ABNT"];

  return (
    <div className="modal-overlay">
      <div className="modal-content" ref={modalRef}>
        <div className="modal-header">
          <h2>{i18n.t("titles.newProject")}</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          <form onSubmit={handleSubmit} noValidate>
            <div className="form-grid">
              <div className="form-left">
                <div className="input-group">
                  <input
                    placeholder={i18n.t("inputs.name")}
                    value={nome}
                    onChange={(e) => {
                      setNome(e.target.value);
                      setFormErrors({ ...formErrors, nome: "" });
                    }}
                  />
                  {formErrors.nome && (
                    <p className="input-error">{formErrors.nome}</p>
                  )}
                </div>
                <div className="input-group">
                  <input
                    placeholder={i18n.t("inputs.description")}
                    value={descricao}
                    onChange={(e) => {
                      setDescricao(e.target.value);
                      setFormErrors({ ...formErrors, descricao: "" });
                    }}
                  />
                  {formErrors.descricao && (
                    <p className="input-error">{formErrors.descricao}</p>
                  )}
                </div>
                <div className="input-group">
                  <input
                    type="email"
                    placeholder={i18n.t("messages.emailMessage")}
                    value={emailInput}
                    onChange={(e) => {
                      setEmailInput(e.target.value);
                      setEmailError("");
                    }}
                    onKeyDown={handleKeyDown}
                  />
                  {emailError && <p className="input-error">{emailError}</p>}
                  <div className="email-list">
                    {colaboradores.map((email) => (
                      <span key={email} className="email-chip">
                        {email}
                        <button
                          type="button"
                          onClick={() => removerColaborador(email)}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="form-right">
                <div className="form-options">
                  <div className="project-type">
                    <label>{i18n.t("inputs.projectType")}</label>
                    <div className="type-options">
                      {projectTypes.map((type) => (
                        <button
                          key={type}
                          type="button"
                          onClick={() => setSelectedType(type)}
                          className={selectedType === type ? "selected" : ""}
                        >
                          {type}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="template-select">
                    <label>{i18n.t("inputs.template")}</label>
                    <select
                      multiple
                      value={template}
                      onChange={(e) =>
                        setTemplate(
                          Array.from(e.target.selectedOptions, (option) =>
                            Number(option.value)
                          )
                        )
                      }
                    >
                      {abntTemplates.map((template) => (
                        <option key={template.value} value={template.value}>
                          {template.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
            {formErrors.submit && (
              <p className="input-error center">{formErrors.submit}</p>
            )}
            <div className="save-wrapper">
              <button type="submit" className="save-btn" disabled={loading}>
                {loading ? "Salvando..." : "Salvar ✓"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ModalNewProject;
