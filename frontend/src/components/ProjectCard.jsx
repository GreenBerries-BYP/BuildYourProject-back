import { useState, useRef, useEffect } from 'react';
import ApexCharts from 'apexcharts'
import '../styles/ProjectCard.css';
import { i18n } from '../translate/i18n';


const ProjectCard = ({
  tituloProjeto = "Projeto Aplicação",
  progressoProjeto = 50,
  progressoIndividual = 30,
}) => {

  const [isExpanded, setIsExpanded] = useState(false);
  
  const handleMouseEnter = () => setIsExpanded(true);
  const handleMouseLeave = () => setIsExpanded(false);
  
  const chartRef = useRef(null);

  useEffect(() => {
    const options = {
      series: [progressoIndividual],
      chart: {
        height: 60,
        type: 'radialBar',
        sparkline: { enabled: true }, // opcional, ajuda com layout pequeno
      },
      plotOptions: {
        radialBar: {
          hollow: {
            size: '40%',
          },
          dataLabels: {
            show: false,
          }
        },
      },
      labels: ['Progresso'],
    };

    const chart = new ApexCharts(chartRef.current, options);
    chart.render();

    return () => chart.destroy();
  }, [progressoIndividual]);

  return (
    <div
      className={`project-card ${isExpanded ? 'expanded' : ''}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
        <div className="card-header">
            {tituloProjeto}
            <button className='d-inline btn-more'>
                <img src="/imgs/more_vert.svg" alt="mais opções no projeto" />
            </button>
        </div>
        <div className="project-progress d-flex">
            <div className="progress w-75">
                <div className="progress-bar" role="progressbar" style={{width: `${progressoProjeto}%`}} aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            <span className='progress-label'>{progressoProjeto}%</span>
        </div>
        <div className="tasks"></div>
        <div className='individual-progress d-flex align-items-center justify-content-between'>
            <span className="alert-task">
              <img src="/imgs/alert.svg"/>
            </span>
            <span>{i18n.t('project.yourTasks')}</span>
            <div className='round-progress d-inline' id='roundProgress'>
              <div ref={chartRef}></div>
            </div>
        </div>
    </div>
  );
};

export default ProjectCard;
