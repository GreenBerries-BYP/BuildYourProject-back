import "../styles/CreateProjectCard.css";

const CreateProjectCard = ({ onClick }) => {
    return (
        <div className="create-project-card" onClick={onClick}>
            <p>Criar projeto</p>
            <div className="plus">+</div>
        </div>
    );
};

export default CreateProjectCard;
