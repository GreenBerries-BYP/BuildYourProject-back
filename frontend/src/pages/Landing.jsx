import React, { useState } from 'react';
import api from '../api/api';

import '../styles/Landing.css';

const Landing = () => {

  return (
    <div className='landing-page'>
      <img className='decor-1' src="/imgs/decor-landing/bx-label.svg"/>
      <img className='decor-2' src="/imgs/decor-landing/bx-code-alt.svg"/>
      <img className='decor-3' src="/imgs/decor-landing/bx-check-square.svg"/>
      <img className='decor-4' src="/imgs/decor-landing/bx-copy-alt.svg"/>
      <img className='decor-5' src="/imgs/decor-landing/bxs-calendar.svg"/>

      <header>
        <img src="/imgs/logo-horiz.svg"/>
        <div className="nav-group">
          <a href="#inicio">início</a>
          <a href="#ferramentas">ferramentas</a>
          <a href="#preview">preview</a>
          <a href="#sobre">sobre nós</a>
        </div>
        <div className="enter-group">
          <a href="/login">Fazer login</a>
          <a href="/register">Criar conta</a>
        </div>
      </header> 

      <div id="inicio" className="secao-inicio">
        <div className="container-inicio">
          <div className="topo-inicio">
            <h1 className="titulo-inicio">
              Transforme seus Projetos com a Organização que Você Precisa
            </h1>
            <p className="descricao-inicio">
              Gerencie, colabore e cumpra prazos com tecnologia inteligente.
            </p>
            <button className="botao-comecar">Começar agora</button>
          </div>
          <div className="blocos-inicio">
            <div className="bloco-roxo">
              <p>Ferramentas intuitivas para estudantes e grupos acadêmicos</p>
            </div>
            <div className="bloco-verde">
              <p>lide com seus  projetos de forma eficiente</p>
            </div>
            <div className="bloco-lilas">
              <p>do planejamento</p>
              <img src=" "/>
              <p>à entrega final.</p>
            </div>
            <div className="bloco-img">
              <img src=""/>
            </div>
          </div>
        </div>
      </div>

      <div id="ferramentas">
        <div className="container-ferramentas">
          <h2 className="titulo-ferramentas">Conheça nossas ferramentas</h2>
          <div className="grade-ferramentas">
            <div className="bloco-ferramenta">
              <h3>Planejamento Modular</h3>
              <p>Divida seu TCC ou projeto em etapas claras e gerenciáveis.</p>
            </div>
            <div className="bloco-ferramenta">
              <h3>Recalculagem de Prazos</h3>
              <p>Atrasou uma entrega? O BYP ajusta automaticamente seu cronograma.</p>
            </div>
            <div className="bloco-ferramenta">
              <h3>Colaboração em Tempo Real</h3>
              <p>Adicione colegas, oriente interações, e acompanhe o progresso conjunto.</p>
            </div>
            <div className="bloco-ferramenta">
              <h3>Alertas e Lembretes</h3>
              <p>Nunca perca um prazo ou atividade importante.</p>
            </div>
            <div className="bloco-ferramenta">
              <h3>Versão Web Responsiva</h3>
              <p>Acesse de qualquer lugar, em qualquer dispositivo.</p>
            </div>
            <div className="bloco-ferramenta">
              <h3>IA integrada</h3>
              <p>Dúvidas? Pergunte à Berry, nossa IA ajudante!</p>
            </div>
          </div>
        </div>
      </div>

      <div id="preview">
        <h1>Preview</h1>
        <p>Veja como é o BYP</p>
        <div id="carouselExampleControls" className="carousel slide" data-ride="carousel">
          <div className="carousel-inner">
            <div className="carousel-item active">
              <img className="d-block w-100" src="..." alt="First slide"/>
            </div>
            <div className="carousel-item">
              <img className="d-block w-100" src="..." alt="Second slide"/>
            </div>
            <div className="carousel-item">
              <img className="d-block w-100" src="..." alt="Third slide"/>
            </div>
          </div>
          <a className="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
            <span className="carousel-control-prev-icon" aria-hidden="true"></span>
            <span className="sr-only">Previous</span>
          </a>
          <a className="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
            <span className="carousel-control-next-icon" aria-hidden="true"></span>
            <span className="sr-only">Next</span>
          </a>
        </div>
      </div>

      <div id="sobre">
        <div className="titulo-sobre">
          <h1>Sobre a GreenBerries</h1>
          <p>Conheça nosso colaboradores</p>
        </div>
        <div className="quem-somos">
          <h2>Quem somos?</h2>
          <p>
            Somos um grupo de estudantes e desenvolvedores apaixonados 
            por resolver o caos dos projetos acadêmicos. 
            <br />
            Criamos o BYP com base nas dificuldades comuns dos 
            estudantes com a organização de projetos — e 
            transformamos isso em uma solução eficiente, 
            colaborativa e realmente útil para qualquer projeto. 
          </p>
        </div>
        <div className="integrantes">
          <div>
            <img src="imgs/integrantes/joao.png" />
            <p>João Félix</p>
          </div>
          <div>
            <img src="imgs/integrantes/jo.png" />
            <p>Jossana Tavares</p>
          </div>
          <div>
            <img src="imgs/integrantes/let.png" />
            <p>Leticia Rudeli</p>
          </div>
          <div>
            <img src="imgs/integrantes/maris.png" />
            <p>Marisa Morita</p>
          </div>
          <div>
            <img src="imgs/integrantes/mih.png" />
            <p>Millena Cupolillo</p>
          </div>
          <div>
            <img src="imgs/integrantes/rodrigo.png" />
            <p>Rodrigo Bettio</p>
          </div>
        </div>
      </div>

      <footer>
        <div className="logos">
          <img src="/imgs/logo-horiz.svg"/>
          <p>Este projeto foi desenvolvido por:</p>
          <img src="imgs/logo-horiz-greenberries.svg" />
        </div>
        <div className="doc">
          <h3>Documentção</h3>
          <p>Documentação: https://www.overleaf.com/project/67f168707c869626a81a641f </p>
        </div>
        <div className="contatos">
          <h3>Contatos</h3>
          <p>Email: <br/>greenberriesbyp@gmail.com</p>
          <p>Youtube: <br/>https://www.youtube.com/@GreenBerries-byp </p>
        </div>
        <hr/>
        <div className="end-footer">
          <p>@ 2025 GreenBerries All rights reserved</p>
          <div className="links">
            <a href="/terms"></a>
            <a href="/politics "></a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;

