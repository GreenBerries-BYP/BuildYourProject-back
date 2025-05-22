import { useState } from 'react';
import { PiCirclesThreeFill } from "react-icons/pi";
import { MdHome, MdLogout, MdInfo, MdOutlineCalendarMonth, MdShare, MdOutlineTaskAlt    } from "react-icons/md";
import '../styles/Sidebar.css';

const Sidebar = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleMouseEnter = () => setIsExpanded(true);
  const handleMouseLeave = () => setIsExpanded(false);

  const topItems = [
    { icon: <MdHome />, label: 'Home', path: '/home' },
    { icon: <PiCirclesThreeFill />, label: 'Meus projetos', path: '/projetos' },
    { icon: <MdOutlineTaskAlt  />, label: 'Minhas tarefas', path: '/tarefas' },
    {
      icon: <MdShare  />,
      label: 'Compartilhados\ncomigo',
      path: '/compartilhados'
    },
    { icon: <MdOutlineCalendarMonth  />, label: 'Google calendário', path: '/calendario' },
  ];

  const bottomItems = [
    { icon: <MdInfo />, label: 'Informações', path: '/info' },
    { icon: <MdLogout />, label: 'Sair', path: '/logout' },
  ];

  return (
    <div
      className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="sidebar-menu">
        {topItems.map((item, index) => (
          <a key={index} href={item.path} className="sidebar-item">
            <span className="sidebar-icon">{item.icon}</span>
            {isExpanded && (
              <span className="sidebar-label">
                {item.label.split('\n').map((line, i) => (
                  <div key={i}>{line}</div>
                ))}
              </span>
            )}
          </a>
        ))}
      </div>
      <div className="sidebar-footer">
        {bottomItems.map((item, index) => (
          <a key={index} href={item.path} className="sidebar-item">
            <span className="sidebar-icon">{item.icon}</span>
            {isExpanded && <span className="sidebar-label">{item.label}</span>}
          </a>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
