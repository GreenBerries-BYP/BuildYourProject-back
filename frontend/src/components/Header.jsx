import { FaRegUserCircle } from "react-icons/fa";
import { TbBellRingingFilled } from "react-icons/tb";
import { MdOutlineWbSunny, MdDarkMode } from 'react-icons/md';
import { GiBrazilFlag } from 'react-icons/gi';
import { FiSearch } from "react-icons/fi";
import '../styles/Header.css';

const Header = ({ isDarkMode, toggleDarkMode }) => {
  return (
    <header className="header">
      <div className="header-left">
        <img src="/imgs/byp_logo.svg" alt="logo" className="logo-img" />
        <span className="title mt-2">Build Your Project</span>
      </div>
      <div className="header-right">
        <FiSearch className="header-icon" />
        <TbBellRingingFilled className="header-icon" />
        <button className="header-icon toggle-mode" onClick={toggleDarkMode}>
          {isDarkMode ? <MdOutlineWbSunny /> : <MdDarkMode />}
        </button>
        <GiBrazilFlag className="header-icon" />
        <FaRegUserCircle className="header-icon" />
      </div>
    </header>
  );
};

export default Header;
