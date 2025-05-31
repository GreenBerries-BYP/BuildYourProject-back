
import React, { useState } from 'react';

import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import ProjectCard from "../components/ProjectCard";
import CreateProjectCard from "../components/CreateProjectCard";
import ViewProject from "../components/ViewProject";
import ModalNewProject from "../components/ModalNewProject";

import '../styles/Home.css';


function Home() {
  const [projetoSelecionado, setProjetoSelecionado] = useState(null); 

  const handleAbrirProjeto = (projeto) => {
    setProjetoSelecionado(projeto); 
  };

  const handleVoltar = () => {
    setProjetoSelecionado(null); 
  };

  const [modalAberto, setModalAberto] = useState(false);
  const [sidebarAberta, setSidebarAberta] = useState(false);

  const handleCreateProject = () => {
    setModalAberto(true);
  };

const projetos = [
  {
    nomeProjeto: 'Projeto A',
    progressoProjeto: 70,
    progressoIndividual: 50,
    admProjeto: 'João',
    numIntegrantes: 4,
    estaAtrasado: true,
    tarefasProjeto: [
      {
        nomeTarefa: 'Design',
        statusTarefa: false,
        progresso: 50,
        tarefas: [
          {
            nome: 'protótipo',
            responsavel: 'Letícia',
            status: 'em andamento',
            prazo: '10/05/2025',
          },
          {
            nome: 'figma',
            responsavel: 'Marisa',
            status: 'concluído',
            prazo: '02/05/2025',
          },
          {
            nome: 'implementação',
            responsavel: 'Jo',
            status: 'a fazer',
            prazo: '01/06/2025',
          }
        ]
      },
      {
        nomeTarefa: 'POC',
        statusTarefa: false,
        progresso: 80,
        tarefas: [
          {
            nome: 'POC',
            responsavel: 'João',
            status: 'em andamento',
            prazo: '01/06/2025',
          }
        ]
      },
      {
        nomeTarefa: 'Documentação',
        statusTarefa: true,
        progresso: 100,
        tarefas: [
          {
            nome: 'Introdução',
            responsavel: 'João',
            status: 'concluído',
            prazo: '01/06/2025',
          },
          {
            nome: 'Desenvolvimento',
            responsavel: 'Millena',
            status: 'concluído',
            prazo: '01/06/2025',
          }
        ]
      }
    ]
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

      {projetoSelecionado ? (
        <div className='d-flex w-100 justify-content-center align-items-center'>
          <ViewProject
            nomeProjeto={projetoSelecionado.nomeProjeto}
            admProjeto={projetoSelecionado.admProjeto}
            numIntegrantes={projetoSelecionado.numIntegrantes}
            tarefasProjeto={projetoSelecionado.tarefasProjeto}
            onVoltar={handleVoltar}
          />
        </div>
        ) : (
      <>
          <CreateProjectCard onClick={handleCreateProject} />
        
          {projetos.map((projeto, index) => (
            <ProjectCard 
              key={index}
              nomeProjeto={projeto.nomeProjeto}
              progressoProjeto={projeto.progressoProjeto}
              progressoIndividual={projeto.progressoIndividual}
              tarefasProjeto={projeto.tarefasProjeto}
              estaAtrasado={projeto.estaAtrasado}
              onClick={() => handleAbrirProjeto(projeto)}
            />
          ))}
        </>
      )}

      </div>
      
      <ModalNewProject isOpen={modalAberto} onClose={() => setModalAberto(false)} />
    </div>
  );
}

export default Home;
