import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

function Home() {
  return (
    <div className="d-flex">
      <Sidebar />
      <div className="flex-grow-1" style={{ marginLeft: "250px" }}>
        {" "}
        {/* Formatando o espaço entre a sidebar e o conteúdo */}
        <Header />
        <h2 className="text-white" style={{marginTop: "12rem"}}>Bem-vindo ao Build Your Project</h2>
      </div>
    </div>
  );
}

export default Home;
