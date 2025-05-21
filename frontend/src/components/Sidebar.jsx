import React, { useState } from 'react';
import {
  FaHome, FaProjectDiagram, FaTasks, FaShareAlt,
  FaCalendarAlt, FaInfoCircle, FaSignOutAlt
} from 'react-icons/fa';
import '../styles/Sidebar.css';

const Sidebar = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleMouseEnter = () => setIsExpanded(true);
  const handleMouseLeave = () => setIsExpanded(false);

  const topItems = [
    { icon: <FaHome />, label: 'Home', path: '/home' },
    { icon: <FaProjectDiagram />, label: 'Meus projetos', path: '/projetos' },
    { icon: <FaTasks />, label: 'Minhas tarefas', path: '/tarefas' },
    {
      icon: <FaShareAlt />,
      label: 'Compartilhados\ncomigo',
      path: '/compartilhados'
    },
    { icon: <FaCalendarAlt />, label: 'Google calendário', path: '/calendario' },
  ];

  const bottomItems = [
    { icon: <FaInfoCircle />, label: 'Informações', path: '/info' },
    { icon: <FaSignOutAlt />, label: 'Sair', path: '/logout' },
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
