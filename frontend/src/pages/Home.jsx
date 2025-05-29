import React, { useState } from 'react';

import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import ProjectCard from "../components/ProjectCard";
import CreateProjectCard from "../components/CreateProjectCard";
import ModalNewProject from "../components/ModalNewProject";

import '../styles/Home.css';

function Home() {
  const [modalAberto, setModalAberto] = useState(false);
  const [sidebarAberta, setSidebarAberta] = useState(false);
  
  const handleCreateProject = () => {
    setModalAberto(true);
  };

   const projetos = [
    {
      nomeProjeto: "Projeto Aplicação",
      progressoProjeto: 45,
      progressoIndividual: 30,
      tarefasProjeto: [
        { nomeTarefa: "Design", statusTarefa: false },
        { nomeTarefa: "POC", statusTarefa: false },
        { nomeTarefa: "Conceito", statusTarefa: true },
        { nomeTarefa: "Introdução", statusTarefa: true },
      ],
      estaAtrasado:true,
    },
    {
      nomeProjeto: "Documentação",
      progressoProjeto: 76,
      progressoIndividual: 100,
      tarefasProjeto: [
        { nomeTarefa: "Conclusão", statusTarefa: true },
        { nomeTarefa: "Resumo", statusTarefa: false },
        { nomeTarefa: "Desenvolvimento", statusTarefa: true },
        { nomeTarefa: "Justificativa", statusTarefa: true },
        { nomeTarefa: "Introdução", statusTarefa: true },
      ],
      estaAtrasado:false,
    },
    {
      nomeProjeto: "Smart Home",
      progressoProjeto: 34,
      progressoIndividual: 80,
      tarefasProjeto: [
        { nomeTarefa: "Documentação", statusTarefa: true },
        { nomeTarefa: "Montagem", statusTarefa: true },
        { nomeTarefa: "Peças", statusTarefa: false },
        { nomeTarefa: "Desenhos", statusTarefa: false },
        { nomeTarefa: "Sistemas", statusTarefa: false },
      ],
      estaAtrasado:true,
    },
    {
      nomeProjeto: "Seminário",
      progressoProjeto: 12,
      progressoIndividual: 20,
      tarefasProjeto: [
        { nomeTarefa: "Conclusão", statusTarefa: false },
        { nomeTarefa: "Resumo", statusTarefa: false },
        { nomeTarefa: "Desenvolvimento", statusTarefa: false },
        { nomeTarefa: "Slides", statusTarefa: false },
        { nomeTarefa: "Introdução", statusTarefa: true },
      ],
      estaAtrasado:false,
    }
  ];

  return (
    <div className="d-flex">
      <Sidebar onToggle={setSidebarAberta}/>
      <Header />
      <div className="projects-area" style={{
          padding: sidebarAberta ? "12rem 3rem 0 32rem" : "12rem 3rem 0 15rem", 
          transition: "padding 0.3s ease"
      }}>
        <CreateProjectCard onClick={handleCreateProject} />
        
        {projetos.map((projeto, index) => (
          <ProjectCard 
            key={index}
            nomeProjeto={projeto.nomeProjeto}
            progressoProjeto={projeto.progressoProjeto}
            progressoIndividual={projeto.progressoIndividual}
            tarefasProjeto={projeto.tarefasProjeto}
          />
        ))}
      </div>
      
      <ModalNewProject isOpen={modalAberto} onClose={() => setModalAberto(false)} />
    </div>
  );
}

export default Home;
