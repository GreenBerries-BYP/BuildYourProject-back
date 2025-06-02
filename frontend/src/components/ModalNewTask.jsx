import { useEffect, useRef, useState } from "react";
import "../styles/ModalNewTask.css";
import { getToken } from "../auth/auth";
import { useTranslation } from "react-i18next";
import api from "../api/api";


const ModalNewTask = ({ isOpen, onClose, projetoId }) => {
    const modalRef = useRef();
    const [nome, setNome] = useState("");
    const [descricao, setDescricao] = useState("");
    const [responsavel, setResponsavel] = useState(null); // Will store collaborator's ID
    const [dataEntrega, setDataEntrega] = useState("");
    const [collaborators, setCollaborators] = useState([]);


    const { t } = useTranslation();
    const [formErrors, setFormErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const validateForm = () => {
        const errors = {};
        if (!nome.trim()) errors.nome = t("messages.taskNameRequired");
        if (!descricao.trim()) errors.descricao = t("messages.taskDescriptionRequired");
        if (!dataEntrega) errors.dataEntrega = t("messages.dueDateRequired");
        if (!responsavel) errors.responsavel = t("messages.responsibleRequired"); // Changed check for ID
        return errors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const errors = validateForm();
        setFormErrors(errors);
        if (Object.keys(errors).length > 0) return;

        const tarefa = {
            nome,
            descricao,
            dataEntrega,
            user: responsavel, // responsavel now holds the user ID
            projetoId
        };

        setLoading(true);
        try {
            const token = getToken();
            await api.post("/api/tarefas/", tarefa, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            onClose();
        } catch (err) {
            setFormErrors({
                submit: err.message || t("messages.errorNewTask"),
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

    useEffect(() => {
        if (isOpen && projetoId) {
            const fetchCollaborators = async () => {
                try {
                    const token = getToken();
                    const response = await api.get(`/api/projetos/${projetoId}/collaborators/`, {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    });
                    // The new endpoint directly returns the list of users (collaborators)
                    if (response.data && Array.isArray(response.data)) {
                        setCollaborators(response.data);
                    } else {
                        console.error("Fetched collaborators data is not an array or is missing:", response.data);
                        setCollaborators([]); // Ensure it's an array
                    }
                } catch (error) {
                    console.error("Failed to fetch collaborators:", error);
                    setCollaborators([]); // Reset or handle error appropriately
                }
            };
            fetchCollaborators();
        } else if (!isOpen) {
            setCollaborators([]); // Clear collaborators when modal is closed
            // Optionally reset other form fields here if needed
            // setNome("");
            // setDescricao("");
            // setResponsavel("");
            // setDataEntrega("");
            // setFormErrors({});
        }
    }, [isOpen, projetoId]);

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content" ref={modalRef}>
                <div className="modal-header">
                    <h2>{t("titles.newTask")}</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>
                <div className="modal-body">
                    <form onSubmit={handleSubmit} noValidate>
                        <div className="form-grid-2x2">
                            {/* Primeira linha de inputs */}
                            <div className="input-group">
                                <label>{t('inputs.name')}</label>
                                <input
                                    placeholder={t("inputs.name")}
                                    value={nome}
                                    onChange={(e) => setNome(e.target.value)}
                                />
                                {formErrors.nome && <p className="input-error">{formErrors.nome}</p>}
                            </div>
                            <div className="input-group">
                                <label>{t('inputs.endDate')}</label>
                                <input
                                    type="date"
                                    value={dataEntrega}
                                    onChange={(e) => setDataEntrega(e.target.value)}
                                />
                                {formErrors.dataEntrega && <p className="input-error">{formErrors.dataEntrega}</p>}
                            </div>

                            {/* Segunda linha de inputs */}
                            <div className="input-group">
                                <label>{t('inputs.description')}</label>
                                <textarea
                                    placeholder={t("inputs.description")}
                                    value={descricao}
                                    onChange={(e) => setDescricao(e.target.value)}
                                />
                                {formErrors.descricao && <p className="input-error">{formErrors.descricao}</p>}
                            </div>


                            <div className="input-group">
                                <label>{t("inputs.selectResponsible")}</label>
                                <div className="options">
                                    {collaborators.length > 0 ? (
                                        collaborators.map((collaborator) => (
                                            <button
                                                key={collaborator.id} // Use id for key
                                                type="button"
                                                onClick={() => setResponsavel(collaborator.id)} // Set ID
                                                className={responsavel === collaborator.id ? "selected" : ""} // Compare with ID
                                            >
                                                {collaborator.full_name || collaborator.email} {/* Display name or email */}
                                            </button>
                                        ))
                                    ) : (
                                        <p>{t("messages.noCollaborators")}</p> // Inform user if no collaborators
                                    )}
                                </div>
                                {formErrors.responsavel && <p className="input-error">{formErrors.responsavel}</p>}
                            </div>
                        </div>
                        {formErrors.submit && (
                            <p className="input-error center">{formErrors.submit}</p>
                        )}

                        <div className="save-wrapper" >
                            <button type="submit" className="save-btn" disabled={loading}>
                                {loading ? t("buttons.saving") : t("buttons.save") + ' ✔'}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ModalNewTask;