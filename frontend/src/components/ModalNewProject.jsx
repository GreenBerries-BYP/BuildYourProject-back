import { useEffect, useRef, useState } from "react";
import "../styles/ModalNewProject.css";
import api from "../api/api";
import { useTranslation } from "react-i18next"; // Added

import { getToken } from "../auth/auth";
import { abntTemplates } from "../mocks/abntMock";
// import { i18n } from "../translate/i18n"; // Removed

const ModalNewProject = ({ isOpen, onClose }) => {
    const { t } = useTranslation(); // Added
    const modalRef = useRef();
    const descriptionTextareaRef = useRef(null);
    const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
    const [currentStep, setCurrentStep] = useState(1);
    const [formData, setFormData] = useState({
        nome: "",
        descricao: "",
        tipo: "TCC",
        template: abntTemplates.length > 0 ? abntTemplates[0].value : "",
        colaboradores: [],
        startDate: "",
        endDate: "",
    });

    const [emailInput, setEmailInput] = useState("");
    const [emailError, setEmailError] = useState("");
    const [formErrors, setFormErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (formErrors[name]) {
            setFormErrors(prev => ({ ...prev, [name]: "" }));
        }
        if (name === "descricao") {
            setTimeout(() => autoResizeTextarea(descriptionTextareaRef.current), 0);
        }
    };

    const handleTypeChange = (type) => {
        setFormData(prev => ({ ...prev, tipo: type }));
        if (formErrors.tipo) {
            setFormErrors(prev => ({ ...prev, tipo: "" }));
        }
    };

    const handleTemplateChange = (selectedTemplateValue) => {
        setFormData(prev => ({ ...prev, template: selectedTemplateValue }));
        if (formErrors.template) {
            setFormErrors(prev => ({ ...prev, template: "" }));
        }
    };

    const handleCollaboratorChange = (newColaboradores) => {
        setFormData(prev => ({ ...prev, colaboradores: newColaboradores }));
    };

    const adicionarColaborador = () => {
        if (!emailInput.trim()) {
            setEmailError(t("messages.emailCantBeEmpty", { defaultValue: "Email não pode estar vazio." }));
            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput)) {
            setEmailError(t("messages.invalidEmailFormat", { defaultValue: "Formato de email inválido." }));
            return;
        }

        if (formData.colaboradores.includes(emailInput)) {
            setEmailError(t("messages.emailAlreadyAdded", { defaultValue: "Email já adicionado." }));
            return;
        }

        handleCollaboratorChange([...formData.colaboradores, emailInput]);
        setEmailInput("");
        setEmailError("");
    };

    const removerColaborador = (email) => {
        handleCollaboratorChange(formData.colaboradores.filter((e) => e !== email));
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            adicionarColaborador();
        }
    };

    const prevStep = () => setCurrentStep(prev => prev - 1);

    const validateForm = () => {
        const errors = {};
        if (!formData.nome.trim()) errors.nome = t("messages.projectNameRequired", { defaultValue: "Nome do projeto é obrigatório." });
        if (!formData.descricao.trim()) errors.descricao = t("messages.projectDescriptionRequired", { defaultValue: "Descrição do projeto é obrigatória." });

        if (!formData.startDate) {
            errors.startDate = t("messages.startDateRequired", { defaultValue: "Data de início é obrigatória." });
        }
        if (!formData.endDate) {
            errors.endDate = t("messages.endDateRequired", { defaultValue: "Data de término é obrigatória." });
        } else if (formData.startDate && formData.endDate) {
            const start = new Date(formData.startDate);
            const end = new Date(formData.endDate);
            if (end < start) {
                errors.endDate = t("messages.endDateAfterStartDate", { defaultValue: "Data de término não pode ser anterior à data de início." });
            }
        }
        return errors;
    };

    const nextStep = () => {
        let currentStepErrors = {};
        const allErrors = validateForm();

        if (currentStep === 1) {
            if (allErrors.nome) currentStepErrors.nome = allErrors.nome;
            if (allErrors.descricao) currentStepErrors.descricao = allErrors.descricao;
        } else if (currentStep === 2) {
            if (allErrors.startDate) currentStepErrors.startDate = allErrors.startDate;
            if (allErrors.endDate) currentStepErrors.endDate = allErrors.endDate;
        }

        if (Object.keys(currentStepErrors).length > 0) {
            setFormErrors(prevErrors => ({ ...prevErrors, ...currentStepErrors }));
            return;
        }

        let relevantErrorKeys = [];
        if (currentStep === 1) relevantErrorKeys = ['nome', 'descricao'];
        if (currentStep === 2) relevantErrorKeys = ['startDate', 'endDate'];

        const newErrors = { ...formErrors };

        relevantErrorKeys.forEach(key => {
            if (newErrors[key] && !currentStepErrors[key]) {
                delete newErrors[key];
            }
        });
        if (Object.keys(currentStepErrors).length === 0) {
            relevantErrorKeys.forEach(key => delete newErrors[key]);
        }

        setFormErrors(newErrors);
        setCurrentStep(prev => prev + 1);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (currentStep === 3) {
            const allErrors = validateForm();
            if (Object.keys(allErrors).length > 0) {
                setFormErrors(allErrors);
                if (allErrors.nome || allErrors.descricao) {
                    setCurrentStep(1);
                } else if (allErrors.startDate || allErrors.endDate) {
                    setCurrentStep(2);
                }
                return;
            }
            setFormErrors({});
            setLoading(true);
            try {
                const token = getToken();
                const submissionData = {
                    nome: formData.nome,
                    descricao: formData.descricao,
                    tipo: formData.tipo,
                    colaboradores: formData.colaboradores,
                    template: formData.template,
                    startDate: formData.startDate,
                    endDate: formData.endDate,
                };
                // Add a comment about backend dependency
                // TODO: Ensure backend endpoint /api/projetos/ is fully implemented and handles auth correctly.
                const response = await api.post("../api/projetos/", submissionData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                    handleErrorLocally: true // Add this flag
                });

                if (response.status && response.status >= 200 && response.status < 300) {
                    // Successful creation
                    onClose(); 
                    setFormData({
                        nome: "",
                        descricao: "",
                        tipo: "TCC",
                        template: abntTemplates.length > 0 ? abntTemplates[0].value : "",
                        colaboradores: [],
                        startDate: "",
                        endDate: "",
                    });
                    setCurrentStep(1);
                    setEmailInput("");
                    setFormErrors({});
                    setIsDescriptionExpanded(false);
                    // Maybe add a success notification/toast here in a real app
                } else {
                    // This block might not be strictly necessary if Axios throws on non-2xx by default
                    // For safety, keeping a generic error if it somehow reaches here
                    const errorData = response.data; 
                    throw new Error(errorData.detail || t("messages.errorNewProject", { defaultValue: "Erro ao criar novo projeto." }));
                }
            } catch (err) {
                if (err.response?.status === 401) {
                    setFormErrors({
                        submit: t("messages.errorNewProjectBackendNotReady", { defaultValue: "Falha ao criar projeto. O serviço pode estar indisponível ou acesso não autorizado. Tente novamente mais tarde." })
                    });
                } else if (err.response) { // Other HTTP errors (400, 500, etc.)
                    const errorData = err.response.data;
                    let detailedMessage = "";
                    if (typeof errorData === 'object' && errorData !== null) {
                        // Try to extract messages if backend sends structured errors like DRF
                        detailedMessage = Object.values(errorData).flat().join(' ');
                    }
                    setFormErrors({
                        submit: `${t("messages.errorNewProject", { defaultValue: "Erro ao criar novo projeto." })} ${detailedMessage || err.message}`.trim()
                    });
                }
                else { // Network errors or other issues
                    setFormErrors({
                        submit: err.message || t("messages.errorNewProject", { defaultValue: "Erro ao criar novo projeto." }),
                    });
                }
            } finally {
                setLoading(false);
            }
        } else {
            nextStep();
        }
    };

    const autoResizeTextarea = (element) => {
        if (element) {
            element.style.height = 'auto';
            const computedStyle = getComputedStyle(element);
            const maxHeight = parseInt(computedStyle.maxHeight, 10);

            if (!isNaN(maxHeight) && element.scrollHeight > maxHeight) {
                element.style.height = `${maxHeight}px`;
                element.style.overflowY = 'auto';
            } else {
                element.style.height = `${element.scrollHeight}px`;
                element.style.overflowY = 'hidden';
            }
        }
    };

    useEffect(() => {
        if (currentStep === 1 && descriptionTextareaRef.current) {
            autoResizeTextarea(descriptionTextareaRef.current);
        }
    }, [formData.descricao, currentStep]);

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
                    <h2>{t("titles.newProject", { defaultValue: "Novo Projeto" })}</h2>
                    <button className="close-btn" onClick={onClose}>
                        ×
                    </button>
                </div>
                <div className="modal-body">
                    <div className="step-indicator">
                        <div className={`step-item ${currentStep === 1 ? 'active' : ''} ${currentStep > 1 ? 'completed' : ''}`}>
                            <span className="step-number">1</span>
                            <span className="step-label">{t("steps.basicInfo", { defaultValue: "Info Básicas" })}</span>
                        </div>
                        <div className="step-connector"></div>
                        <div className={`step-item ${currentStep === 2 ? 'active' : ''} ${currentStep > 2 ? 'completed' : ''}`}>
                            <span className="step-number">2</span>
                            <span className="step-label">{t("steps.datesAndCollaborators", { defaultValue: "Datas e Colaboradores" })}</span>
                        </div>
                        <div className="step-connector"></div>
                        <div className={`step-item ${currentStep === 3 ? 'active' : ''}`}>
                            <span className="step-number">3</span>
                            <span className="step-label">{t("steps.review", { defaultValue: "Revisão" })}</span>
                        </div>
                    </div>
                    <form onSubmit={handleSubmit} noValidate>
                        {currentStep === 1 && (
                            <div>
                                <h3>{t("titles.step1BasicInfo", { defaultValue: "Etapa 1: Informações Básicas" })}</h3>
                                <div className="form-grid">
                                    <div className="form-left">
                                        <div className="input-group">
                                            <label htmlFor="projectName">{t("inputs.name", { defaultValue: "Nome do Projeto" })}</label>
                                            <input
                                                id="projectName"
                                                name="nome"
                                                placeholder={t("placeholders.projectName", { defaultValue: "Insira o nome do projeto" })}
                                                value={formData.nome}
                                                onChange={handleChange}
                                            />
                                            {formErrors.nome && (
                                                <p className="input-error">{formErrors.nome}</p>
                                            )}
                                        </div>
                                        <div className={`input-group floating-label-group ${formData.descricao ? 'has-value' : ''} ${formErrors.descricao ? 'has-error' : ''}`}
                                            onClick={() => descriptionTextareaRef.current && descriptionTextareaRef.current.focus()}
                                        >
                                            <textarea
                                                id="projectDescription"
                                                name="descricao"
                                                value={formData.descricao}
                                                onChange={handleChange}
                                                onFocus={(e) => e.target.parentElement.classList.add('focused')}
                                                onBlur={(e) => {
                                                    if (!formData.descricao) {
                                                        e.target.parentElement.classList.remove('focused');
                                                    }
                                                }}
                                                ref={descriptionTextareaRef}
                                                rows="4"
                                            />
                                            <label htmlFor="projectDescription">
                                                {t("inputs.description", { defaultValue: "Descrição do Projeto" })}
                                            </label>
                                            <div className="char-counter-footer">
                                                <span>{formData.descricao.length} / 500</span>
                                            </div>
                                        </div>
                                        {formErrors.descricao && (
                                            <p className="input-error" style={{ marginTop: '-0.5rem' }}>{formErrors.descricao}</p>
                                        )}
                                    </div>
                                    <div className="form-right">
                                        <div className="form-options">
                                            <div className="project-type">
                                                <label>{t("inputs.projectType", { defaultValue: "Tipo de Projeto" })}</label>
                                                <div className="type-options">
                                                    {projectTypes.map((type) => (
                                                        <button
                                                            key={type}
                                                            type="button"
                                                            onClick={() => handleTypeChange(type)}
                                                            className={formData.tipo === type ? "selected" : ""}
                                                        >
                                                            {type}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                            <div className="template-select">
                                                <label htmlFor="projectTemplate">{t("inputs.template", { defaultValue: "Template" })}</label>
                                                <select
                                                    id="projectTemplate"
                                                    name="template"
                                                    value={formData.template}
                                                    onChange={(e) => handleTemplateChange(e.target.value)}
                                                >
                                                    <option value="">{t("inputs.selectTemplate", { defaultValue: "Selecione um template" })}</option>
                                                    {abntTemplates.map((tmpl) => (
                                                        <option key={tmpl.value} value={tmpl.value}>
                                                            {tmpl.label}
                                                        </option>
                                                    ))}
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                        {currentStep === 2 && (
                            <div>
                                <h3>{t("titles.step2DatesAndCollabs", { defaultValue: "Etapa 2: Datas e Colaboradores" })}</h3>
                                <div className="form-grid">
                                    <div className="form-left">
                                        <div className="input-group">
                                            <label htmlFor="startDate">{t("inputs.startDate", { defaultValue: "Data de Início" })}</label>
                                            <input
                                                type="date"
                                                id="startDate"
                                                name="startDate"
                                                value={formData.startDate}
                                                onChange={handleChange}
                                            />
                                            {formErrors.startDate && <p className="input-error">{formErrors.startDate}</p>}
                                        </div>
                                        <div className="input-group">
                                            <label htmlFor="endDate">{t("inputs.endDate", { defaultValue: "Data de Término" })}</label>
                                            <input
                                                type="date"
                                                id="endDate"
                                                name="endDate"
                                                value={formData.endDate}
                                                onChange={handleChange}
                                            />
                                            {formErrors.endDate && <p className="input-error">{formErrors.endDate}</p>}
                                        </div>
                                    </div>
                                    <div className="form-right">
                                        <h4>{t("titles.collaborators", { defaultValue: "Colaboradores" })}</h4>
                                        <div className="input-group">
                                            <input
                                                id="collaboratorEmail"
                                                type="email"
                                                placeholder={t("messages.emailMessage", { defaultValue: "Insira o email e pressione Enter" })}
                                                value={emailInput}
                                                onChange={(e) => {
                                                    setEmailInput(e.target.value);
                                                    setEmailError("");
                                                }}
                                                onKeyDown={handleKeyDown}
                                            />
                                        </div>
                                        {emailError && <p className="input-error" style={{ marginTop: '0.5rem' }}>{emailError}</p>}
                                        <div className="email-list">
                                            {formData.colaboradores.map((email) => (
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
                            </div>
                        )}
                        {currentStep === 3 && (
                            <div>
                                <h3>{t("titles.step3Review", { defaultValue: "Etapa 3: Revisão dos Detalhes do Projeto" })}</h3>
        <p className="review-intro-message">{t("messages.reviewProjectDetails", { defaultValue: "Por favor, revise os detalhes do seu projeto antes de enviar." })}</p>
                                <div className="review-grid">
                                    <div className="review-section">
                                        <h4>{t("titles.projectDetails", { defaultValue: "Detalhes do Projeto" })}</h4>
                                        <p><strong>{t("inputs.name", { defaultValue: "Nome do Projeto" })}:</strong> {formData.nome || t("messages.notSpecified", { defaultValue: "N/A" })}</p>

                                        <div className="review-item review-description-wrapper">
                                            <p style={{ marginBottom: '0.5rem' }}>
                                                <strong>{t("inputs.descriptionShort", { defaultValue: "Descrição" })}:</strong>
                                            </p>
                                            <div
                                                className={`review-description-content ${isDescriptionExpanded ? 'expanded' : 'collapsed'}`}
                                            >
                                                {formData.descricao || t("messages.notSpecified", { defaultValue: "N/A" })}
                                            </div>
                                            {formData.descricao && formData.descricao.length > 150 && (
                                                <button
                                                    type="button"
                                                    onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                                                    className="toggle-description-btn"
                                                >
                                                    {isDescriptionExpanded
                                                        ? t("buttons.readLess", { defaultValue: "Ler menos" })
                                                        : t("buttons.readMore", { defaultValue: "Ler mais" })}
                                                </button>
                                            )}
                                        </div>

                                        <p><strong>{t("inputs.projectType", { defaultValue: "Tipo de Projeto" })}:</strong> {formData.tipo || t("messages.notSpecified", { defaultValue: "N/A" })}</p>
                                        <p><strong>{t("inputs.template", { defaultValue: "Template" })}:</strong> {
                                            (abntTemplates.find(tmpl => tmpl.value === formData.template) || {}).label || formData.template || t("messages.notSpecified", { defaultValue: "N/A" })
                                        }</p>
                                    </div>
                                    <div className="review-section">
                                        <h4>{t("titles.datesAndCollaborators", { defaultValue: "Datas e Colaboradores" })}</h4>
                                        <p><strong>{t("inputs.startDate", { defaultValue: "Data de Início" })}:</strong> {formData.startDate || t("messages.notSpecified", { defaultValue: "N/A" })}</p>
                                        <p><strong>{t("inputs.endDate", { defaultValue: "Data de Término" })}:</strong> {formData.endDate || t("messages.notSpecified", { defaultValue: "N/A" })}</p>
                                        <p><strong>{t("titles.collaborators", { defaultValue: "Colaboradores" })}:</strong></p>
                                        {formData.colaboradores.length > 0 ? (
                                            <ul className="review-collaborators-list">
                                                {formData.colaboradores.map(email => <li key={email}>{email}</li>)}
                                            </ul>
                                        ) : <p>{t("messages.noCollaborators", { defaultValue: "N/A" })}</p>}
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="navigation-buttons">
                            {currentStep > 1 && (
                                <button type="button" className="prev-btn" onClick={prevStep}>
                                    {t("buttons.previous", { defaultValue: "Anterior" })}
                                </button>
                            )}
                            {currentStep < 3 && (
                                <button type="button" className="next-btn" onClick={nextStep}>
                                    {t("buttons.next", { defaultValue: "Próximo" })}
                                </button>
                            )}
                            {currentStep === 3 && (
                                <button type="submit" className="save-btn" disabled={loading}>
                                    {loading ? t('buttons.saving', { defaultValue: 'Salvando...' }) : t('buttons.createProject', { defaultValue: 'Criar Projeto' })}
                                </button>
                            )}
                        </div>
                        {formErrors.submit && (
                            <p className="input-error center" style={{ marginTop: "10px" }}>{formErrors.submit}</p>
                        )}
                    </form>
                </div>
            </div>
        </div>
    );
};
export default ModalNewProject;