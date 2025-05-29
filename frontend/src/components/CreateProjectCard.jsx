import "../styles/CreateProjectCard.css";

import { i18n } from "../translate/i18n";

const CreateProjectCard = ({ onClick }) => {
    return (
        <div className="create-project-card d-flex align-items-center justify-items-center p-5" onClick={onClick}>
            <p>{i18n.t('titles.newProject')}</p>
            <div className="plus">+</div>
        </div>
    );
};

export default CreateProjectCard;
