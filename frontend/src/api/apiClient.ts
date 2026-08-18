/**
 * Production API Client for EduSense AI connecting to FastAPI backend.
 */
import axios from 'axios';

export const API_BASE_URL = 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;
  constructor(message: string, status: number = 400, data: any = null) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor adding Authorization Bearer token from active session
apiClient.interceptors.request.use((config) => {
  let token: string | null = null;
  
  // 1. Prefer token from active edu_session
  const sessionStr = sessionStorage.getItem('edu_session') || localStorage.getItem('edu_session');
  if (sessionStr) {
    try {
      const parsed = JSON.parse(sessionStr);
      if (parsed?.token) {
        token = parsed.token;
      }
    } catch (e) {}
  }
  
  // 2. Fallback to direct token keys
  if (!token) {
    token = localStorage.getItem('edu_auth_token') || 
            sessionStorage.getItem('edu_auth_token') || 
            localStorage.getItem('token');
  }

  if (token && !config.headers.Authorization) {
    config.headers.Authorization = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Response interceptor handling status codes
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response ? error.response.status : 500;
    const message = error.response?.data?.error?.message || error.response?.data?.detail || error.message || 'An unexpected error occurred';
    return Promise.reject(new ApiError(message, status, error.response?.data));
  }
);

export default apiClient;
