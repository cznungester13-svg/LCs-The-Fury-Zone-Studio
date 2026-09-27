import axios from "axios";

// Create an axios instance pointing to your backend API
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Automatically attach authorization token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("fury_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;