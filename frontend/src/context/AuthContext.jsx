import { createContext, useContext, useEffect, useState, useCallback } from "react";
// Fix: Use standard relative path resolution instead of assuming an @ alias is configured
import api from "../lib/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null); // null = loading, false = anon
  const [ready, setReady] = useState(false);

  const loadMe = useCallback(async () => {
    const token = localStorage.getItem("fury_token");
    if (!token) {
      setUser(false);
      setReady(true);
      return;
    }
    try {
      const { data } = await api.get("/auth/me");
      setUser(data);
    } catch {
      localStorage.removeItem("fury_token");
      setUser(false);
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => {
    loadMe();
  }, [loadMe]);

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem("fury_token", data.token);
    setUser(data.user);
    return data.user;
  };

  const register = async (payload) => {
    const { data } = await api.post("/auth/register", payload);
    localStorage.setItem("fury_token", data.token);
    setUser(data.user);
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem("fury_token");
    setUser(false);
  };

  const isAdmin = user && user.roles?.includes("admin");
  const isSeller = user && user.roles?.includes("seller");

  return (
    <AuthContext.Provider value={{ user, ready, login, register, logout, refresh: loadMe, setUser, isAdmin, isSeller }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
