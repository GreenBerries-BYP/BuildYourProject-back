import "../styles/CreateProjectCard.css";
import { useTranslation } from 'react-i18next';

const CreateProjectCard = ({ onClick }) => {
  const { t } = useTranslation();

  return (
    <div className="create-project-card" onClick={onClick}>
      <p>{t('titles.newProject')}</p>
      <div className="plus">+</div>
    </div>
  );
};
export default CreateProjectCard;

