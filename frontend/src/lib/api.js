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

// Helper function for handling image URLs
export const imgUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http")) return url;
  const base = import.meta.env.VITE_API_URL || "";
  return `${base}${url}`;
};

// Helper function for formatting currency
export const currency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount || 0);
};

// Helper function for formatting API error messages
export const apiError = (err) => {
  if (typeof err === "string") return err;
  return err?.message || "An unexpected error occurred";
};

export default api;