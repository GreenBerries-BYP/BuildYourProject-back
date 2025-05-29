import axios from 'axios';
import { getToken } from '../auth/auth'; 

const instance = axios.create({
  baseURL: 'http://localhost:8000/api', 
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

export default instance;
