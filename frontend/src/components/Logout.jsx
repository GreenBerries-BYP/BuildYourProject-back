// src/pages/Logout.jsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { removeToken } from '../auth/auth'; 

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    removeToken();              
    navigate('/login');         
  }, [navigate]);

  return null; // Não renderiza nada
};

export default Logout;
