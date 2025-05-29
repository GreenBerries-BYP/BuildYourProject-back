import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import CreateProjectCard from "../components/CreateProjectCard";
import ModalNewProject from "../components/ModalNewProject";

function Home() {
  const [modalAberto, setModalAberto] = useState(false);

  const handleCreateProject = () => {
    setModalAberto(true);
  };

  return (
    <div className="d-flex">
      <Sidebar />
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
      </div>
      <ModalNewProject isOpen={modalAberto} onClose={() => setModalAberto(false)} />
    </div>

  );
}

export default Home;
