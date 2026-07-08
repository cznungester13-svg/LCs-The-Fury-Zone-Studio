import axios from "axios";

// Universal environment fallback checking both Vite and Create React App configs
const BACKEND_URL = 
  (typeof import.meta !== "undefined" && import.meta.env?.VITE_BACKEND_URL) ||
  (typeof process !== "undefined" && process.env?.REACT_APP_BACKEND_URL) || 
  "";

export const API = `${BACKEND_URL}/api`;

const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("fury_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function imgUrl(u) {
  if (!u) return "";
  if (u.startsWith("http://") || u.startsWith("https://")) return u;
  
  // If the path is a partial route from storage, prepend /api/files/ safely
  if (!u.startsWith("/api/") && !u.startsWith("api/")) {
    const cleanPath = u.startsWith("/") ? u.slice(1) : u;
    return `${BACKEND_URL}/api/files/${cleanPath}`;
  }
  
  // Otherwise ensure proper leading slash formatting
  const formattedPath = u.startsWith("/") ? u : `/${u}`;
  return `${BACKEND_URL}${formattedPath}`;
}

export function apiError(detail) {
  if (detail == null) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).join(" ");
  }
  if (detail && typeof detail.msg === "string") return detail.msg;
  if (detail && detail.response?.data?.detail) {
    return apiError(detail.response.data.detail);
  }
  return String(detail);
}

export default api;
