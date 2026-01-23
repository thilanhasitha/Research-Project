import axios from 'axios';
import type { AxiosInstance, AxiosError } from 'axios';

// Base API configuration
const createApiClient = (baseURL: string): AxiosInstance => {
  const client = axios.create({
    baseURL,
    // timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add auth token if available
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
      // Handle common errors
      if (error.response?.status === 401) {
        // Handle unauthorized
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  return client;
};

// API base URLs for each microservice
// TODO: Update these URLs with your actual backend endpoints
export const API_BASE_URLS = {
  valuation: import.meta.env.VITE_VALUATION_API_URL || 'http://localhost:8001/api/v1',
  sentiment: import.meta.env.VITE_SENTIMENT_API_URL || 'http://localhost:8002/api/v1',
  fraud: import.meta.env.VITE_FRAUD_API_URL || 'http://localhost:8003/api/v1',
  recommendation: import.meta.env.VITE_RECOMMENDATION_API_URL || 'http://localhost:8004/api/v1',
};

// Create API clients for each service
export const valuationApi = createApiClient(API_BASE_URLS.valuation);
export const sentimentApi = createApiClient(API_BASE_URLS.sentiment);
export const fraudApi = createApiClient(API_BASE_URLS.fraud);
export const recommendationApi = createApiClient(API_BASE_URLS.recommendation);

// Export default client
export default createApiClient;
