import axios from 'axios';
import store from '../store'; // Import store to get the token

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to dynamically add the Authorization header
apiClient.interceptors.request.use(
  (config) => {
    const token = store.getters['auth/token'];
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default apiClient;
