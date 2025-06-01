import axios from 'axios';
import { getToken } from '../auth/auth';

const instance = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor
instance.interceptors.request.use(
  async (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor para tratar erros globais
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Check if the request config has a flag to handle the error locally
    if (error.config && error.config.handleErrorLocally) {
      return Promise.reject(error); // Skip global handling, error will be caught by the component
    }
    
    return Promise.reject(error);
  }
);

// Função específica para buscar dados do usuário
export const fetchUserData = async () => {
  try {
    const response = await instance.get('/home/');
    return response.data;
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
};

// Função específica para buscar dados do projeto
export const fetchProjects = async () => {
  try {
    const response = await instance.get('/projetos/');
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar projetos:', error);
    throw error;
  }
};

export default instance;