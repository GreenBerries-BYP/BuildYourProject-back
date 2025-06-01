import { useEffect, useRef, useState } from "react";
import "../styles/ModalNewTask.css";
import { getToken } from "../auth/auth";
import { useTranslation } from "react-i18next";
import api from "../api/api"; // Assuming api is used in handleSubmit


const responsavelOptions = ["lelerudeli@gmail.com", "rodrigobettio@gmail.com"];

const ModalNewTask = ({ isOpen, onClose, projetoId }) => {
    const modalRef = useRef();
    const [nome, setNome] = useState("");
    const [descricao, setDescricao] = useState("");
    const [responsavel, setResponsavel] = useState("");
    const [dataEntrega, setDataEntrega] = useState("");


    const { t } = useTranslation();
    const [formErrors, setFormErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const validateForm = () => {
        const errors = {};
        if (!nome.trim()) errors.nome = t("messages.taskNameRequired", "Task name is required");
        if (!descricao.trim()) errors.descricao = t("messages.taskDescriptionRequired", "Task description is required");
        if (!dataEntrega) errors.dataEntrega = t("messages.dueDateRequired", "Due date is required");
        if (!responsavel.trim()) errors.responsavel = t("messages.responsibleRequired", "Responsible is required");
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
            responsavel,
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

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="modal-content" ref={modalRef}>
                <div className="modal-header">
                    <h2>{t("titles.newTask", "New Task")}</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>
                <div className="modal-body">
                    <form onSubmit={handleSubmit} noValidate>
                        <div className="input-group">
                            <input
                                placeholder={t("inputs.name")}
                                value={nome}
                                onChange={(e) => setNome(e.target.value)}
                            />
                            {formErrors.nome && <p className="input-error">{formErrors.nome}</p>}
                        </div>

                        <div className="input-group">
                            <textarea
                                placeholder={t("inputs.description")}
                                value={descricao}
                                onChange={(e) => setDescricao(e.target.value)}
                            />
                            {formErrors.descricao && <p className="input-error">{formErrors.descricao}</p>}
                        </div>

                        <div className="input-group">
                            <input
                                type="date"
                                value={dataEntrega}
                                onChange={(e) => setDataEntrega(e.target.value)}
                            />
                            {formErrors.dataEntrega && <p className="input-error">{formErrors.dataEntrega}</p>}
                        </div>

                        <div className="input-group">
                             <select value={responsavel} onChange={(e) => setResponsavel(e.target.value)}>
                                <option value="">{t("inputs.selectResponsible", "Select responsible")}</option>
                                {responsavelOptions.map((s) => (
                                    <option key={s} value={s}>{s}</option>
                                ))}
                            </select>
                            {formErrors.responsavel && <p className="input-error">{formErrors.responsavel}</p>}
                        </div>

                        {formErrors.submit && (
                            <p className="input-error center">{formErrors.submit}</p>
                        )}

                        <div className="save-wrapper">
                            <button type="submit" className="save-btn" disabled={loading}>
                                {loading ? t("buttons.saving", "Saving...") : t("buttons.saveTask", "Save ✓")}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ModalNewTask;
