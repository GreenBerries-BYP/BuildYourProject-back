import { useState } from "react";

import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import ProjectCard from "../components/ProjectCard";
import CreateProjectCard from "../components/CreateProjectCard";
import ModalNewProject from "../components/ModalNewProject";

import "../styles/Home.css";

function Home() {
  const [modalAberto, setModalAberto] = useState(false);
  const [sidebarAberta, setSidebarAberta] = useState(false);

  const handleCreateProject = () => {
    setModalAberto(true);
  };

  return (
    <div className="d-flex">
      <Sidebar onToggle={setSidebarAberta} />
      <div className="flex-grow-1" style={{ marginLeft: "280px" }}>
        <Header />
        <div
          className={`main-content ${modalAberto ? "blur-background" : ""}`}
          style={{ marginTop: "10rem", padding: "2rem" }}
        >
          <div className="d-flex flex-wrap gap-4">
            <CreateProjectCard onClick={handleCreateProject} />
          </div>
        </div>
        <div
          className="projects-area"
          style={{
            padding: sidebarAberta
              ? "12rem 3rem 0 32rem"
              : "12rem 3rem 0 15rem",
            transition: "padding 0.3s ease",
          }}
        >
          <ProjectCard
            tituloProjeto="Projeto Aplicação"
            progressoProjeto={45}
            progressoIndividual={30}
          />

          <ProjectCard
            tituloProjeto="Documentação"
            progressoProjeto={76}
            progressoIndividual={100}
          />

          <ProjectCard
            tituloProjeto="Smart Home"
            progressoProjeto={34}
            progressoIndividual={80}
          />

          <ProjectCard
            tituloProjeto="Seminário"
            progressoProjeto={12}
            progressoIndividual={20}
          />
        </div>

        <ModalNewProject
          isOpen={modalAberto}
          onClose={() => setModalAberto(false)}
        />
      </div>
    </div>
  );
}

export default Home;
