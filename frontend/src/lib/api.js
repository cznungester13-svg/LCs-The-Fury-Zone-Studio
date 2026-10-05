import axios from "axios";

// Backend base URL comes from the environment (CRA injects REACT_APP_* at build time).
// Falls back to same-origin "/api" (works behind the Kubernetes ingress and Vercel rewrite).
const BACKEND_URL = (typeof process !== "undefined" && process.env && process.env.REACT_APP_BACKEND_URL) || "";

// Create an axios instance pointing to your backend API
export const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
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
  return `${BACKEND_URL}${url}`;
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