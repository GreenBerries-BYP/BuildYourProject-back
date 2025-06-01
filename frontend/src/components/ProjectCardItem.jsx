import { useTranslation } from 'react-i18next';
import '../styles/ProjectCardItem.css';


const ProjectCardItem = ({ nomeTarefa, statusTarefa }) => {
  const { t } = useTranslation();

  return (
    <div className="project-card-item d-inline">

      <img
        src={statusTarefa ? "/imgs/checked.svg" : "/imgs/unchecked.svg"}
        alt={statusTarefa ? t("altText.taskCompleted", "Task completed") : t("altText.taskPending", "Task pending")}
      />

      <p className="task-name">{nomeTarefa}</p>

    </div>
  );
};

export default ProjectCardItem;