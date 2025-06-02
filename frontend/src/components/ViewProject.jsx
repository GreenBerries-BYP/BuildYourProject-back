import { useState } from 'react';
import '../styles/ViewProject.css';
import { useTranslation } from 'react-i18next';
import { MdExpandLess, MdExpandMore } from 'react-icons/md';
import ModalNewTask from './ModalNewTask';


const ViewProject = ({
  nomeProjeto,
  admProjeto,
  numIntegrantes,
  collaborators, // Added collaborators prop
  tarefasProjeto,
  onVoltar
}) => {
  const { t } = useTranslation();
  const [expandedSections, setExpandedSections] = useState({});
  const [modalAberto, setModalAberto] = useState(false);

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  return (
    <div className='view-project'>
        <div className="project-header">
            <div className="project-data">
                <h1>{nomeProjeto}</h1>
                <p>{t("viewProject.createdBy", { adm: admProjeto })}</p>
                <p>{t("viewProject.membersCount", { count: numIntegrantes })}</p>
                {/* Displaying collaborators */}
                {collaborators && collaborators.length > 0 && (
                  <div className="project-collaborators">
                    <h4>{t("viewProject.collaboratorsTitle", "Collaborators")}:</h4>
                    <ul>
                      {collaborators.map(collab => (
                        <li key={collab.id || collab.email}>
                          {collab.full_name || collab.email}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
            </div>
            
            <div className="project-options">
                <div className="btns">
                    <button className='compartilhar-btn'><img src="/imgs/icons-project/Link.svg" alt={t("altText.shareLink")} /></button>
                    <button className='editar-btn'><img src="/imgs/icons-project/Edit.svg" alt={t("altText.editProject")} /></button>
                    <button className='calendario-btn'><img src="/imgs/icons-project/Calendar.svg" alt={t("altText.viewCalendar")} /></button>
                    <button className='fechar-btn' onClick={onVoltar}><img src="/imgs/icons-project/Close.svg" alt={t("altText.closeView")} /></button>
                </div>

                <button className='criar-tarefa-btn' onClick={() => setModalAberto(true)}>
                    <span>{t('buttons.newTask')}</span>
                    <img src="/imgs/icons-project/add.svg" />
                </button>
            </div>
        </div>

        <div className="project-tasks">
            {tarefasProjeto?.map((tarefa, index) => (
                <div key={index} className="task-section">
                    <div
                        className="task-header"
                        onClick={() => toggleSection(tarefa.nomeTarefa)}
                    >
                        <span className="task-title">
                            <img src={(tarefa.progresso == 100) ? "/imgs/checked.svg" : "/imgs/unchecked.svg"}/>
                            
                            {tarefa.nomeTarefa}
                        </span>
                        <span className='task-data'>
                            <span className="task-progress d-flex">
                                <span className="progress">
                                    <span className="progress-bar" role="progressbar" style={{width: `${tarefa.progresso}%`}} aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></span>
                                </span>
                                <span className='progress-label'>{tarefa.progresso}%</span>
                            </span>
                            
                            <span className="expand-icon">
                            {expandedSections[tarefa.nomeTarefa] ? (
                                <MdExpandLess />
                            ) : (
                                <MdExpandMore />
                            )}
                            </span>
                        </span>
                    </div>

                    {expandedSections[tarefa.nomeTarefa] && (
                        <table className="task-table">
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>{t("viewProject.taskHeaderTask")}</th>
                                    <th>{t("viewProject.taskHeaderResponsible")}</th>
                                    <th>{t("viewProject.taskHeaderStatus")}</th>
                                    <th>{t("viewProject.taskHeaderDueDate")}</th>
                                </tr>
                                <tr> {/* linhas horizontais */}
                                    <th><hr /></th>
                                    <th><hr /></th>
                                    <th><hr /></th>
                                    <th><hr /></th>
                                    <th><hr /></th>
                                </tr>
                            </thead>
                            
                            <tbody>
                                
                                {tarefa.tarefas.map((etapa, idx) => (
                                    <tr key={idx}>
                                        <img src={(etapa.status == 'concluído') ? "/imgs/checked.svg" : "/imgs/unchecked.svg"} alt={etapa.status === 'concluído' ? t("altText.taskCompleted") : t("altText.taskPending")}/>
                                        <td>{etapa.nome}</td>
                                        <td>{etapa.responsavel}</td>
                                        <td>{etapa.status}</td>
                                        <td>{etapa.prazo}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            ))}
        </div>
        <ModalNewTask isOpen={modalAberto} onClose={() => setModalAberto(false)} />
    </div>
  );
};

// Remover a linha jQuery se não estiver sendo usada em outro lugar do arquivo.
// Se esta linha for essencial para alguma funcionalidade, mantenha-a.
// Por padrão, estou removendo-a, pois não faz parte do React e 'popover' é geralmente do Bootstrap.
// $(function () {
//   $('[data-toggle="popover"]').popover({html: true})
// })

export default ViewProject;