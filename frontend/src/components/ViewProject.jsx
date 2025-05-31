import { useState } from 'react';
import '../styles/ViewProject.css';
import { i18n } from '../translate/i18n';
import { MdExpandLess, MdExpandMore } from 'react-icons/md';

const ViewProject = ({
  nomeProjeto,
  admProjeto,
  numIntegrantes,
  tarefasProjeto,
  onVoltar 
}) => {
  const [expandedSections, setExpandedSections] = useState({});

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
                <p>Criado por: {admProjeto}</p>
                <p>{numIntegrantes} integrantes</p>
            </div>
            
            <div className="project-options">
                <div className="btns">
                    <button className='compartilhar-btn'><img src="/imgs/icons-project/Link.svg" /></button>
                    <button className='editar-btn'><img src="/imgs/icons-project/Edit.svg" /></button>
                    <button className='calendario-btn'><img src="/imgs/icons-project/Calendar.svg" /></button>
                    <button className='fechar-btn' onClick={onVoltar}><img src="/imgs/icons-project/Close.svg" /></button>
                </div>

                <button className='criar-tarefa-btn'>
                    <span>{i18n.t('project.newTask')}</span>
                    <img src="/imgs/icons-project/add.svg" />
                </button>
            </div>
        </div>

        <div className="project-tasks">
            {tarefasProjeto.map((tarefa, index) => (
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
                                    <th>Tarefa</th>
                                    <th>Responsável</th>
                                    <th>Status</th>
                                    <th>Prazo</th>
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
                                        <img src={(etapa.status == 'concluído') ? "/imgs/checked.svg" : "/imgs/unchecked.svg"}/>
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
    </div>
  );
};

$(function () {
  $('[data-toggle="popover"]').popover({html: true})
})

export default ViewProject;
