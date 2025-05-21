import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

function Home() {
  return (
    <div className="d-flex">
      <Sidebar />
      <div className="flex-grow-1" style={{ marginLeft: '250px' }}> {/* Formatando o espaço entre a sidebar e o conteúdo */}
        <Header />
        <div style={{ marginTop: '100px' }}> {/*Formatando o espaço entre o header e o conteúdo */}
          <h1>Bem-vindo ao Build Your Project</h1>
        </div>
      </div>
    </div>
  );
}

export default Home;
