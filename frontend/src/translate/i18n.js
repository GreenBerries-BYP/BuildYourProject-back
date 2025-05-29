import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import { messages } from "./languages";

i18n.use(LanguageDetector).init({
  debug: false, //para não mostrar logs no console
  defaultNS: ['translations'], //define o namespace padrão
  fallbackLng: 'pt', // idioma padrão
  ns: ['translations'],
  resources: messages,
});

export { i18n };
