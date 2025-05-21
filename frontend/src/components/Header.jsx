import React from 'react';
import { FaSearch, FaBell, FaMoon, FaUserCircle } from 'react-icons/fa';
import { MdOutlineWbSunny } from 'react-icons/md';
import { GiBrazilFlag } from 'react-icons/gi';
import '../styles/Header.css';

const Header = ({ isDarkMode, toggleDarkMode }) => {
  return (
    <header className="header">
      <div className="header-left">
        <span className="logo">BYP</span>
        <span className="title">Build Your Project</span>
      </div>
      <div className="header-right">
        <FaSearch className="header-icon" />
        <FaBell className="header-icon" />
        <button className="header-icon toggle-mode" onClick={toggleDarkMode}>
          {isDarkMode ? <MdOutlineWbSunny /> : <FaMoon />}
        </button>
        <GiBrazilFlag className="header-icon" />
        <FaUserCircle className="header-icon" />
      </div>
    </header>
  );
};

export default Header;
