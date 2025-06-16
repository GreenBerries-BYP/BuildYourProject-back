import { useState, useEffect, useRef } from "react";
import { FaRegUserCircle } from "react-icons/fa";
import { TbBellRingingFilled } from "react-icons/tb";
import { MdOutlineWbSunny, MdDarkMode } from "react-icons/md";
import { FiSearch } from "react-icons/fi";
import "../styles/Header.css";
import { useTranslation } from "react-i18next";

const I18N_STORAGE_KEY = "i18nextLng";

const Header = () => {
  const { t, i18n } = useTranslation();
  const [language, setLanguage] = useState(
    localStorage.getItem(I18N_STORAGE_KEY)
  );
  const [isDark, setIsDark] = useState(() => {
    const savedTheme = localStorage.getItem("theme");
    return savedTheme === "dark";
  });
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const searchInputRef = useRef(null);

  useEffect(() => {
    if (isDark) {
      document.body.classList.add("dark-theme");
    } else {
      document.body.classList.remove("dark-theme");
    }
    localStorage.setItem("theme", isDark ? "dark" : "light");
  }, [isDark]);

  //inicia o idioma com o valor do localStorage ou padrão para "pt-BR"
  const toggleLanguage = () => {
    setLanguage((prev) => (prev === "pt-BR" ? "en-US" : "pt-BR"));
    localStorage.setItem(
      language === "pt-BR" ? "en-US" : "pt-BR",
      I18N_STORAGE_KEY
    );
    i18n.changeLanguage(language === "pt-BR" ? "en-US" : "pt-BR");
  };

  const toggleDarkMode = () => {
    setIsDark((prev) => !prev);
  };

  const flagSrc =
    i18n.language === "pt-BR" ? "/imgs/brazil-.png" : "/imgs/united-states.png";
  const flagAlt =
    i18n.language === "pt-BR" ? t("altText.brazilFlag", "Brazilian Flag") : t("altText.usFlag", "US Flag");

  const handleSearchFocus = () => setIsSearchFocused(true);
  const handleSearchBlur = () => {
    setTimeout(() => {
      if (
        !searchInputRef.current ||
        !searchInputRef.current.contains(document.activeElement)
      ) {
        setIsSearchFocused(false);
        searchInputRef.current.value = ""; 
      }
    }, 0);
  };

  return (
    <header className="header d-flex align-items-center justify-content-between">
      <div className="header-left d-flex align-items-center">
        <img src="/imgs/byp_logo.svg" alt={t("altText.logoBYP", "BYP Logo")} className="logo-img" />
        <span className="title mt-2">{t("header.title", "Build Your Project")}</span>
      </div>
      <div className="header-right d-flex align-items-center">
        <div
          className={`search ${
            isSearchFocused ? "focused" : ""
          } d-flex align-items-center`}
        >
          <input
            type="text"
            placeholder={t("messages.searchPlaceholder", "Search...")}
            className="search-input"
            onFocus={handleSearchFocus}
            onBlur={handleSearchBlur}
            ref={searchInputRef}
          />
          <FiSearch className="header-icon search-icon" />
        </div>
        <TbBellRingingFilled className="header-icon" aria-label={t("header.notifications", "Notifications")} />
        <button className="header-icon" onClick={toggleDarkMode} aria-label={isDark ? t("header.switchToLightMode", "Switch to Light Mode") : t("header.switchToDarkMode", "Switch to Dark Mode")}>
          {isDark ?  <MdOutlineWbSunny /> : <MdDarkMode />}
        </button>

        <button onClick={toggleLanguage} className="header-icon" aria-label={t("header.changeLanguage")}>
          <img src={flagSrc} alt={flagAlt} className="bandeira" />
        </button>
        <FaRegUserCircle className="header-icon" aria-label={t("header.userProfile", "User Profile")} />
      </div>
    </header>
  );
};

export default Header;
