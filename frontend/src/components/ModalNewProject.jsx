import { useEffect, useRef, useState } from "react";
import "../styles/ModalNewProject.css";

const ModalNewProject = ({ isOpen, onClose }) => {
    const modalRef = useRef();
    const [selectedType, setSelectedType] = useState("TCC");
    const [nome, setNome] = useState("");
    const [descricao, setDescricao] = useState("");
    const [colaboradores, setColaboradores] = useState([]);
    const [emailInput, setEmailInput] = useState("");
    const [template, setTemplate] = useState("Introdução, Objetivo, Conclusão...");

    const [emailError, setEmailError] = useState("");
    const [formErrors, setFormErrors] = useState({});

    const adicionarColaborador = () => {
        if (!emailInput.trim()) {
            setEmailError("Email não pode estar vazio.");
            return;
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput)) {
            setEmailError("Formato de email inválido.");
            return;
        }

        if (colaboradores.includes(emailInput)) {
            setEmailError("Este email já foi adicionado.");
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
        if (!nome.trim()) errors.nome = "O nome do projeto é obrigatório.";
        if (!descricao.trim()) errors.descricao = "A descrição é obrigatória.";
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

        try {
            const response = await fetch("http://localhost:8000/api/projetos", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(projeto),
            });

            if (!response.ok) throw new Error("Erro ao criar projeto");

            onClose();
        } catch (err) {
            setFormErrors({ submit: err.message || "Erro inesperado ao criar projeto." });
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
                    <h2>Novo Projeto</h2>
                    <button className="close-btn" onClick={onClose}>×</button>
                </div>
                <div className="modal-body">
                    <form onSubmit={handleSubmit} noValidate>
                        <div className="form-grid">
                            <div className="form-left">
                                <div className="input-group">
                                    <input
                                        placeholder="Nome"
                                        value={nome}
                                        onChange={(e) => {
                                            setNome(e.target.value);
                                            setFormErrors({ ...formErrors, nome: "" });
                                        }}
                                    />
                                    {formErrors.nome && <p className="input-error">{formErrors.nome}</p>}
                                </div>
                                <div className="input-group">
                                    <input
                                        placeholder="Descrição"
                                        value={descricao}
                                        onChange={(e) => {
                                            setDescricao(e.target.value);
                                            setFormErrors({ ...formErrors, descricao: "" });
                                        }}
                                    />
                                    {formErrors.descricao && <p className="input-error">{formErrors.descricao}</p>}
                                </div>
                                <div className="input-group">
                                    <input
                                        type="email"
                                        placeholder="Digite um email e pressione Enter"
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
                                                <button type="button" onClick={() => removerColaborador(email)}>×</button>
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="form-right">
                                <div className="form-options">
                                    <div className="project-type">
                                        <label>Tipo de Projeto</label>
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
                                        <label>Modelo Base (template)</label>
                                        <select
                                            value={template}
                                            onChange={(e) => setTemplate(e.target.value)}
                                        >
                                            <option>Introdução, Objetivo, Conclusão...</option>
                                            <option>Teste 2</option>
                                            <option>Teste 3</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {formErrors.submit && (
                            <p className="input-error center">{formErrors.submit}</p>
                        )}
                        <div className="save-wrapper">
                            <button type="submit" className="save-btn">Salvar ✓</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ModalNewProject;
