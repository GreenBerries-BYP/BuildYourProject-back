
import '../styles/ProjectCardItem.css';


const ProjectCardItem = ({nomeTarefa, statusTarefa}) => {

  return (
    <div className="project-card-item d-inline">

      <img 
        src={statusTarefa ? "/imgs/checked.svg" : "/imgs/unchecked.svg"} 
        alt={statusTarefa ? "Tarefa concluída" : "Tarefa pendente"} 
      />
      
      <p className="task-name">{nomeTarefa}</p>
      
    </div>
  );
};

export default ProjectCardItem;