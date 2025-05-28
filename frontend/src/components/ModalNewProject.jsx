import { useEffect, useRef, useState } from "react";
import "../styles/ModalNewProject.css";

const ModalNewProject = ({ isOpen, onClose }) => {
  const modalRef = useRef();
  const [selectedType, setSelectedType] = useState("TCC");

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
          <form>
            <div className="form-grid">
              <div className="form-left">
                <input placeholder="Nome" />
                <input placeholder="Descrição" />
                <input placeholder="Colaboradores" />
              </div>
              <div className="form-right">
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
                  <select>
                    <option>Introdução, Objetivo, Conclusão...</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="save-wrapper">
              <button className="save-btn">Salvar ✓</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ModalNewProject;
