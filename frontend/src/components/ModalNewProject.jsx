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
        name: "",
        description: "",
        type: "TCC",
        template: abntTemplates.length > 0 ? abntTemplates[0].value : "",
        collaborators: [],
        created_at: "",
        due_date: "",
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
        if (name === "description") {
            setTimeout(() => autoResizeTextarea(descriptionTextareaRef.current), 0);
        }
    };

    const handleTypeChange = (type) => {
        setFormData(prev => ({ ...prev, type: type }));
        if (formErrors.type) {
            setFormErrors(prev => ({ ...prev, type: "" }));
        }
    };

    const handleTemplateChange = (selectedTemplateValue) => {
        setFormData(prev => ({ ...prev, template: selectedTemplateValue }));
        if (formErrors.template) {
            setFormErrors(prev => ({ ...prev, template: "" }));
        }
    };

    const handleCollaboratorChange = (newColaboradores) => {
        setFormData(prev => ({ ...prev, collaborators: newColaboradores }));
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

        if (formData.collaborators.includes(emailInput)) {
            setEmailError(t("messages.emailAlreadyAdded", { defaultValue: "Email já adicionado." }));
            return;
        }

        handleCollaboratorChange([...formData.collaborators, emailInput]);
        setEmailInput("");
        setEmailError("");
    };

    const removerColaborador = (email) => {
        handleCollaboratorChange(formData.collaborators.filter((e) => e !== email));
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
        if (!formData.name.trim()) errors.name = t("messages.projectNameRequired", { defaultValue: "Nome do projeto é obrigatório." });
        if (!formData.description.trim()) errors.description = t("messages.projectDescriptionRequired", { defaultValue: "Descrição do projeto é obrigatória." });

        if (!formData.created_at) {
            errors.created_at = t("messages.created_atRequired", { defaultValue: "Data de início é obrigatória." });
        }
        if (!formData.due_date) {
            errors.due_date = t("messages.due_dateRequired", { defaultValue: "Data de término é obrigatória." });
        } else if (formData.created_at && formData.due_date) {
            const start = new Date(formData.created_at);
            const end = new Date(formData.due_date);
            if (end < start) {
                errors.due_date = t("messages.due_dateAfterStartDate", { defaultValue: "Data de término não pode ser anterior à data de início." });
            }
        }
        return errors;
    };

    const nextStep = () => {
        let currentStepErrors = {};
        const allErrors = validateForm();

        if (currentStep === 1) {
            if (allErrors.name) currentStepErrors.name = allErrors.name;
            if (allErrors.description) currentStepErrors.description = allErrors.description;
        } else if (currentStep === 2) {
            if (allErrors.created_at) currentStepErrors.created_at = allErrors.created_at;
            if (allErrors.due_date) currentStepErrors.due_date = allErrors.due_date;
        }

        if (Object.keys(currentStepErrors).length > 0) {
            setFormErrors(prevErrors => ({ ...prevErrors, ...currentStepErrors }));
            return;
        }

        let relevantErrorKeys = [];
        if (currentStep === 1) relevantErrorKeys = ['name', 'description'];
        if (currentStep === 2) relevantErrorKeys = ['created_at', 'due_date'];

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
                if (allErrors.name || allErrors.description) {
                    setCurrentStep(1);
                } else if (allErrors.created_at || allErrors.due_date) {
                    setCurrentStep(2);
                }
                return;
            }
            setFormErrors({});
            setLoading(true);
            try {
                const token = getToken();
                const submissionData = {
                    name: formData.name,
                    description: formData.description,
                    type: formData.type,
                    collaborators: formData.collaborators,
                    template: formData.template,
                    created_at: formData.created_at,
                    due_date: formData.due_date,
                };
                // Add a comment about backend dependency
                // TODO: Ensure backend endpoint /api/projetos/ is fully implemented and handles auth correctly.
                const response = await api.post("/projetos/", submissionData, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                    handleErrorLocally: true // Add this flag
                });

                if (response.status && response.status >= 200 && response.status < 300) {
                    // Successful creation
                    onClose(); 
                    setFormData({
                        name: "",
                        description: "",
                        type: "TCC",
                        template: abntTemplates.length > 0 ? abntTemplates[0].value : "",
                        collaborators: [],
                        created_at: "",
                        due_date: "",
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
    }, [formData.description, currentStep]);

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
                                                name="name"
                                                placeholder={t("placeholders.projectName", { defaultValue: "Insira o name do projeto" })}
                                                value={formData.name}
                                                onChange={handleChange}
                                            />
                                            {formErrors.name && (
                                                <p className="input-error">{formErrors.name}</p>
                                            )}
                                        </div>
                                        <div className={`input-group floating-label-group ${formData.description ? 'has-value' : ''} ${formErrors.description ? 'has-error' : ''}`}
                                            onClick={() => descriptionTextareaRef.current && descriptionTextareaRef.current.focus()}
                                        >
                                            <textarea
                                                id="projectDescription"
                                                name="description"
                                                value={formData.description}
                                                onChange={handleChange}
                                                onFocus={(e) => e.target.parentElement.classList.add('focused')}
                                                onBlur={(e) => {
                                                    if (!formData.description) {
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
                                                <span>{formData.description.length} / 500</span>
                                            </div>
                                        </div>
                                        {formErrors.description && (
                                            <p className="input-error" style={{ marginTop: '-0.5rem' }}>{formErrors.description}</p>
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
                                                            className={formData.type === type ? "selected" : ""}
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
                                            <label htmlFor="created_at">{t("inputs.created_at", { defaultValue: "Data de Início" })}</label>
                                            <input
                                                type="date"
                                                id="created_at"
                                                name="created_at"
                                                value={formData.created_at}
                                                onChange={handleChange}
                                            />
                                            {formErrors.created_at && <p className="input-error">{formErrors.created_at}</p>}
                                        </div>
                                        <div className="input-group">
                                            <label htmlFor="due_date">{t("inputs.due_date", { defaultValue: "Data de Término" })}</label>
                                            <input
                                                type="date"
                                                id="due_date"
                                                name="due_date"
                                                value={formData.due_date}
                                                onChange={handleChange}
                                            />
                                            {formErrors.due_date && <p className="input-error">{formErrors.due_date}</p>}
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
                                            {formData.collaborators.map((email) => (
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
                                        <p><strong>{t("inputs.name", { defaultValue: "Nome do Projeto" })}:</strong> {formData.name || t("messages.notSpecified", { defaultValue: "N/A" })}</p>

                                        <div className="review-item review-description-wrapper">
                                            <p style={{ marginBottom: '0.5rem' }}>
                                                <strong>{t("inputs.descriptionShort", { defaultValue: "Descrição" })}:</strong>
                                            </p>
                                            <div
                                                className={`review-description-content ${isDescriptionExpanded ? 'expanded' : 'collapsed'}`}
                                            >
                                                {formData.description || t("messages.notSpecified", { defaultValue: "N/A" })}
                                            </div>
                                            {formData.description && formData.description.length > 150 && (
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

                                        <p><strong>{t("inputs.projectType", { defaultValue: "Tipo de Projeto" })}:</strong> {formData.type || t("messages.notSpecified", { defaultValue: "N/A" })}</p>
                                        <p><strong>{t("inputs.template", { defaultValue: "Template" })}:</strong> {
                                            (abntTemplates.find(tmpl => tmpl.value === formData.template) || {}).label || formData.template || t("messages.notSpecified", { defaultValue: "N/A" })
                                        }</p>
                                    </div>
                                    <div className="review-section">
                                        <h4>{t("titles.datesAndCollaborators", { defaultValue: "Datas e Colaboradores" })}</h4>
                                        <p><strong>{t("inputs.created_at", { defaultValue: "Data de Início" })}:</strong> {formData.created_at || t("messages.notSpecified", { defaultValue: "N/A" })}</p>
                                        <p><strong>{t("inputs.due_date", { defaultValue: "Data de Término" })}:</strong> {formData.due_date || t("messages.notSpecified", { defaultValue: "N/A" })}</p>
                                        <p><strong>{t("titles.collaborators", { defaultValue: "Colaboradores" })}:</strong></p>
                                        {formData.collaborators.length > 0 ? (
                                            <ul className="review-collaborators-list">
                                                {formData.collaborators.map(email => <li key={email}>{email}</li>)}
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