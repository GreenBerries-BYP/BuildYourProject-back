
import { useState, useRef, useEffect } from 'react';
import ApexCharts from 'apexcharts'
import '../styles/ProjectCard.css';
import ProjectCardItem from './ProjectCardItem';
import { useTranslation } from 'react-i18next';


const ProjectCard = ({
  nomeProjeto,
  progressoProjeto,
  progressoIndividual,
  tarefasProjeto,
  estaAtrasado,
  onClick
}) => {

  const { t } = useTranslation();

  const [isExpanded, setIsExpanded] = useState(false);

  const handleMouseEnter = () => setIsExpanded(true);
  const handleMouseLeave = () => setIsExpanded(false);

  const btnRef = useRef(null);

  const chartRef = useRef(null);

  useEffect(() => {
    $(btnRef.current).popover({
      html: true,
      content: `<button class="btn-popover">${t('buttons.deleteProject')}</button>`,
    });
  }, [t]);

  useEffect(() => {
     if (!chartRef.current) return;

    const safeProgressoIndividual = typeof progressoIndividual === 'number' ? progressoIndividual : 0;

    const options = {
      series: [safeProgressoIndividual],
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
      labels: [t('projectCard.progressLabel', "Progress")],
    };

    const chart = new ApexCharts(chartRef.current, options);
    chart.render();

    return () => chart.destroy();
  }, [progressoIndividual]);

  return (
    <div className='project-card' onClick={onClick}>
        <div className="card-header">
            {nomeProjeto}
            <button className='d-inline btn-more'  data-toggle="popover" data-content='
              <button class="btn-popover">apagar projeto<button/>
            '>

                <img src="/imgs/more_vert.svg" alt={t("altText.projectOptions", "Project options")} />
            </button>
        </div>
        <div className="project-progress d-flex">
            <div className="progress w-75">
                <div className="progress-bar" role="progressbar" style={{width: `${progressoProjeto}%`}} aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            <span className='progress-label'>{progressoProjeto}%</span>
        </div>
        <div className="tasks">
            {tarefasProjeto?.map((tarefa, index)=>(
                <ProjectCardItem 
                    key={index}
                    nomeTarefa={tarefa.nomeTarefa} 
                    statusTarefa={tarefa.statusTarefa} 
                />      
            ))}
            
        </div>
       
      <div className='individual-progress d-flex align-items-center justify-content-end'>
        <span className={estaAtrasado ? "" : "d-none"}>
          <img src="/imgs/alert.svg" alt={t("altText.alertIcon", "Alert")} />
        </span>

        <span className='text-center mx-3'>{t('project.yourTasks')}</span>

        <div className='round-progress d-inline' id='roundProgress'>
          <div ref={chartRef}></div>
        </div>


      </div>
    </div>
  );
};

export default ProjectCard;

$(function () {
  $('[data-toggle="popover"]').popover({ html: true })
})
