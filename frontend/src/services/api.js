import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

export const patientsAPI = {
  getPatients: async () => {
    const response = await api.get('/patients');
    return response.data;
  },
  getPatient: async (id) => {
    const response = await api.get(`/patients/${id}`);
    return response.data;
  },
};

export const formsAPI = {
  getForms: async (params = {}) => {
    const response = await api.get('/forms/', { params });
    return response.data;
  },
  getForm: async (id, excludeNull = true) => {
    const response = await api.get(`/forms/${id}`, { 
      params: { exclude_null: excludeNull } 
    });
    return response.data;
  },
  getFormsByPatient: async (patientId, excludeNull = true) => {
    const response = await api.get(`/forms/patient/${patientId}`, { 
      params: { exclude_null: excludeNull } 
    });
    return response.data;
  },
  summarizeForm: async (formId) => {
    const response = await api.post(`/forms/${formId}/summarize`);
    return response.data;
  },
};

export const statusAPI = {
  getStatus: async () => {
    const response = await api.get('/status');
    return response.data;
  },
};

export default api; 