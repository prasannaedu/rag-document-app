// src/services/api.js
import axios from 'axios';
import { getToken } from '../utils/auth';

const api = axios.create({
  baseURL: '/api', 
});


api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


export const register = (username, email, password) => {
  return api.post('/auth/register', {
    username,
    email,
    password,
  });
};


export const login = (username, password) => {
  const data = new URLSearchParams();
  data.append('username', username);
  data.append('password', password);
  return api.post('/auth/login', data, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
};


export const uploadDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};


export const queryDocument = (query) => {
  return api.post('/documents/query', { query }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};