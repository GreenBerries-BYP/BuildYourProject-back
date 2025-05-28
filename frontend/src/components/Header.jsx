import { useState, useRef } from "react";
import { FaRegUserCircle } from "react-icons/fa";
import { TbBellRingingFilled } from "react-icons/tb";
import { MdOutlineWbSunny, MdDarkMode } from "react-icons/md";
import { FiSearch } from "react-icons/fi";
import "../styles/Header.css";

const Header = () => {
  const [language, setLanguage] = useState("br");
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const searchInputRef = useRef(null);

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === "br" ? "us" : "br"));
  };

  const toggleDarkMode = () => {
    setIsDarkMode((prev) => !prev);
  };

  const flagSrc =
    language === "br" ? "/imgs/brazil-.png" : "/imgs/united-states.png";
  const flagAlt = language === "br" ? "bandeira do Brasil" : "bandeira dos EUA";

  const handleSearchFocus = () => {
    setIsSearchFocused(true);
  };

  const handleSearchBlur = () => {
    setTimeout(() => {
      if (
        !searchInputRef.current ||
        !searchInputRef.current.contains(document.activeElement)
      ) {
        setIsSearchFocused(false);
      }
    }, 0);
  };

  return (
    <header className="header d-flex align-items-center justify-content-between">
      <div className="header-left d-flex align-items-center">
        <img src="/imgs/byp_logo.svg" alt="logo" className="logo-img" />
        <span className="title mt-2">Build Your Project</span>
      </div>
      <div className="header-right d-flex align-items-center">
        <div
          className={`search ${isSearchFocused ? "focused" : ""
            } d-flex align-items-center`}
        >
          <input
            type="text"
            placeholder="Pesquisar..."
            className="search-input"
            onFocus={handleSearchFocus}
            onBlur={handleSearchBlur}
            ref={searchInputRef}
          />
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
