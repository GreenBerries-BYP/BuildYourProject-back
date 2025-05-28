import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import CreateProjectCard from "../components/CreateProjectCard";

function Home() {
  const handleCreateProject = () => {
    alert("Criar projeto clicado!");
  };

  return (
    <div className="d-flex">
      <Sidebar />
      <div className="flex-grow-1" style={{ marginLeft: "280px" }}>
        <Header />
        <div className="main-content" style={{ marginTop: "10rem", padding: "2rem" }}>
          <div className="d-flex flex-wrap gap-4">
            <CreateProjectCard onClick={handleCreateProject} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
