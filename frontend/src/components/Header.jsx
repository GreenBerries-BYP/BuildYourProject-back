import { useState } from 'react';
import { FaRegUserCircle } from "react-icons/fa";
import { TbBellRingingFilled } from "react-icons/tb";
import { MdOutlineWbSunny, MdDarkMode } from 'react-icons/md';
import { FiSearch } from "react-icons/fi";
import '../styles/Header.css';

const Header = () => {
  const [language, setLanguage] = useState("br");
  const [isDarkMode, setIsDarkMode] = useState(false);

  const toggleLanguage = () => {
    setLanguage(prev => (prev === "br" ? "us" : "br"));
  };

  const toggleDarkMode = () => {
    setIsDarkMode(prev => !prev);
  };

  const flagSrc = language === "br" ? "/imgs/brazil-.png" : "/imgs/united-states.png";
  const flagAlt = language === "br" ? "bandeira do Brasil" : "bandeira dos EUA";

  return (
    <header className="header">
      <div className="header-left">
        <img src="/imgs/byp_logo.svg" alt="logo" className="logo-img" />
        <span className="title mt-2">Build Your Project</span>
      </div>
      <div className="header-right">
        <div className="search">
          <FiSearch className="header-icon search-icon" />
        </div>
        <TbBellRingingFilled className="header-icon" />
        <button className="header-icon" onClick={toggleDarkMode}>
          {isDarkMode ? <MdOutlineWbSunny /> : <MdDarkMode />}
        </button>
        <button onClick={toggleLanguage} className="header-icon">
          <img src={flagSrc} alt={flagAlt} className="bandeira" />
        </button>
        <FaRegUserCircle className="header-icon" />
      </div>
    </header>
  );
};

export default Header;
