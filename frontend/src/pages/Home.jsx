import React, { useState, useEffect } from 'react';

import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import ProjectCard from "../components/ProjectCard";
import CreateProjectCard from "../components/CreateProjectCard";
import ViewProject from "../components/ViewProject";
import ModalNewProject from "../components/ModalNewProject";

import '../styles/Home.css';
import { fetchUserData } from '../api/userService';

function Home() {
  const [modalAberto, setModalAberto] = useState(false);
  const [sidebarAberta, setSidebarAberta] = useState(false);
  const [userData, setUserData] = useState(null);
  const [projetoSelecionado, setProjetoSelecionado] = useState(null);

  useEffect(() => {
    fetchUserData()
      .then(data => {
        setUserData(data);
        console.log('Email do usuário logado:', data.email);
      })
      .catch(error => {
        console.error('Erro ao buscar dados do usuário:', error);
      });
  }, []);

  useEffect(() => {
    if (modalAberto || projetoSelecionado) {
      document.body.classList.add('no-scroll');
    } else {
      document.body.classList.remove('no-scroll');
    }
    return () => {
      document.body.classList.remove('no-scroll');
    };
  }, [modalAberto, projetoSelecionado]);

  const handleCreateProject = () => {
    setModalAberto(true);
  };

  const handleAbrirProjeto = (projeto) => {
    setProjetoSelecionado(projeto);
  };

  const handleVoltar = () => {
    setProjetoSelecionado(null);
  };

  const projetos = [
    {
      nomeProjeto: 'Projeto Aplicação',
      progressoProjeto: 45,
      progressoIndividual: 30,
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
    },
    {
      nomeProjeto: "Documentação",
      progressoProjeto: 76,
      progressoIndividual: 100,
      admProjeto: 'Ana',
      numIntegrantes: 2,
      tarefasProjeto: [
        {
          nomeTarefa: "Conclusão",
          statusTarefa: true,
          progresso: 100,
          tarefas: [{ nome: "Revisão Final", responsavel: "Ana", status: "concluído", prazo: "20/05/2025" }]
        },
        {
          nomeTarefa: "Resumo",
          statusTarefa: false,
          progresso: 50,
          tarefas: [{ nome: "Escrever Resumo", responsavel: "Pedro", status: "em andamento", prazo: "05/06/2025" }]
        },
        {
          nomeTarefa: "Desenvolvimento",
          statusTarefa: true,
          progresso: 100,
          tarefas: [{ nome: "Capítulo 1-3", responsavel: "Ana", status: "concluído", prazo: "15/05/2025" }]
        },
        {
          nomeTarefa: "Justificativa",
          statusTarefa: true,
          progresso: 100,
          tarefas: [{ nome: "Definir Justificativa", responsavel: "Pedro", status: "concluído", prazo: "10/05/2025" }]
        },
        {
          nomeTarefa: "Introdução",
          statusTarefa: true,
          progresso: 100,
          tarefas: [{ nome: "Escrever Introdução", responsavel: "Ana", status: "concluído", prazo: "01/05/2025" }]
        },
      ],
      estaAtrasado: false,
    },
    {
      nomeProjeto: "Smart Home",
      progressoProjeto: 34,
      progressoIndividual: 80,
      admProjeto: 'Carlos',
      numIntegrantes: 5,
      tarefasProjeto: [
        {
          nomeTarefa: "Documentação",
          statusTarefa: true,
          progresso: 100,
          tarefas: [{ nome: "Especificações", responsavel: "Carlos", status: "concluído", prazo: "01/06/2025" }]
        },
        {
          nomeTarefa: "Montagem",
          statusTarefa: true,
          progresso: 70,
          tarefas: [{ nome: "Hardware", responsavel: "Mariana", status: "em andamento", prazo: "15/06/2025" }]
        },
        {
          nomeTarefa: "Peças",
          statusTarefa: false,
          progresso: 20,
          tarefas: [{ nome: "Orçamento", responsavel: "Rafael", status: "a fazer", prazo: "10/06/2025" }]
        },
        {
          nomeTarefa: "Desenhos",
          statusTarefa: false,
          progresso: 0,
          tarefas: [{ nome: "Esboços", responsavel: "João", status: "a fazer", prazo: "01/07/2025" }]
        },
        {
          nomeTarefa: "Sistemas",
          statusTarefa: false,
          progresso: 10,
          tarefas: [{ nome: "Software", responsavel: "Fernanda", status: "a fazer", prazo: "20/06/2025" }]
        },
      ],
      estaAtrasado: true,
    },
    {
      nomeProjeto: "Seminário",
      progressoProjeto: 12,
      progressoIndividual: 20,
      admProjeto: 'Patrícia',
      numIntegrantes: 3,
      tarefasProjeto: [
        {
          nomeTarefa: "Conclusão",
          statusTarefa: false,
          progresso: 0,
          tarefas: [{ nome: "Revisão Conclusão", responsavel: "Patrícia", status: "a fazer", prazo: "01/07/2025" }]
        },
        {
          nomeTarefa: "Resumo",
          statusTarefa: false,
          progresso: 0,
          tarefas: [{ nome: "Escrever Resumo", responsavel: "Ricardo", status: "a fazer", prazo: "25/06/2025" }]
        },
        {
          nomeTarefa: "Desenvolvimento",
          statusTarefa: false,
          progresso: 0,
          tarefas: [{ nome: "Pesquisa", responsavel: "Patrícia", status: "a fazer", prazo: "20/06/2025" }]
        },
        {
          nomeTarefa: "Slides",
          statusTarefa: false,
          progresso: 0,
          tarefas: [{ nome: "Criar Slides", responsavel: "Mariana", status: "a fazer", prazo: "10/07/2025" }]
        },
        {
          nomeTarefa: "Introdução",
          statusTarefa: true,
          progresso: 100,
          tarefas: [{ nome: "Escrever Introdução", responsavel: "Ricardo", status: "concluído", prazo: "05/06/2025" }]
        },
      ],
      estaAtrasado: false,
    }
  ];

  return (
    <div className="d-flex">
      <Sidebar onToggle={setSidebarAberta} />
      <Header />

      <div className={`main-page-content ${modalAberto ? "blur-background" : ""}`} style={{
        padding: sidebarAberta ? "12rem 3rem 0 32rem" : "12rem 3rem 0 15rem",
        transition: "padding 0.3s ease",
        flexGrow: 1,
        overflowY: 'auto'
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
          <div className="projects-area">
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
          </div>
        )}
      </div>

      <ModalNewProject
        isOpen={modalAberto}
        onClose={() => setModalAberto(false)}
      />
    </div>
  );
}

export default Home;