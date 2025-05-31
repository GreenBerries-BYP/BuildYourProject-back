import { useState } from 'react';
import { PiCirclesThreeFill } from "react-icons/pi";
import { MdHome, MdLogout, MdInfo, MdOutlineCalendarMonth, MdShare, MdOutlineTaskAlt } from "react-icons/md";
import '../styles/Sidebar.css';
import { NavLink } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { i18n } from "../translate/i18n";


const Sidebar = ({ onToggle }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleMouseEnter = () => {
    setIsExpanded(true);
    onToggle(true);
  };
  const handleMouseLeave = () => {
    setIsExpanded(false);
    onToggle(false);
  };


  const topItems = [
    { icon: <MdHome />, label: i18n.t('sideBar.home'), path: '/home' },
    { icon: <PiCirclesThreeFill />, label: i18n.t('sideBar.myProjects'), path: '/projetos' },
    { icon: <MdOutlineTaskAlt />, label: i18n.t('sideBar.myTasks'), path: '/tarefas' },
    {
      icon: <MdShare />,
      label: i18n.t('sideBar.sharedWithMe'),
      path: '/compartilhados'
    },
    { icon: <MdOutlineCalendarMonth />, label: i18n.t('sideBar.googleCalendar'), path: '/calendario' },
  ];

  const bottomItems = [
    { icon: <MdInfo />, label: i18n.t('sideBar.info'), path: '/info' },
    { icon: <MdLogout />, label: i18n.t('sideBar.logOut'), path: '/logout' },
  ];

  const expandedWidth = '280px';
  const collapsedWidth = '80px';

  return (
    <div
      className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        width: isExpanded ? expandedWidth : collapsedWidth,
        flexShrink: 0,
        transition: 'width 0.3s ease'
      }}
    >
      <div className="sidebar-menu">
        {topItems.map((item, index) => {
          return (
            <NavLink
              key={index}
              to={item.path}
              aria-label={item.label}
              className={({ isActive }) =>
                `sidebar-item ${isActive ? 'on-page' : ''}`
              }
            >
              <span className="sidebar-icon">{item.icon}</span>
              {isExpanded && (
                <span className="sidebar-label">
                  {item.label.split('\n').map((line, i) => (
                    <div key={i}>{line}</div>
                  ))}
                </span>
              )}
            </NavLink>

          );
        })}
      </div>
      <div className="sidebar-footer">
        {bottomItems.map((item, index) => (
          <NavLink
            key={index}
            to={item.path}
            aria-label={item.label}
            className={({ isActive }) =>
              `sidebar-item ${isActive ? 'on-page' : ''}`
            }
          >
            <span className="sidebar-icon">{item.icon}</span>
            {isExpanded && <span className="sidebar-label">{item.label}</span>}
          </NavLink>

        ))}
      </div>
    </div>
  );
};

export default Sidebar;
