// services/userService.js
import axios from 'axios';
import { getToken } from '../auth/auth';

export const fetchUserData = async () => {
  const token = getToken();

  if (!token) {
    throw new Error('Token não encontrado. Usuário não autenticado.');
  }

  try {
    const response = await axios.get('http://localhost:8000/api/home/', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error) {
    console.error('Erro ao buscar dados do usuário:', error);
    throw error;
  }
};
