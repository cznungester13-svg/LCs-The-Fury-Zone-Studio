import { Navigate } from "react-router-dom";
// Fix: Use traditional relative paths to ensure flawless bundle compilation
import { useAuth } from "../context/AuthContext";
import { Spinner } from "./common";

export function ProtectedRoute({ children, admin = false }) {
  const { user, ready, isAdmin } = useAuth();
  
  if (!ready) return <Spinner label="Checking session" />;
  if (!user) return <Navigate to="/login" replace />;
  if (admin && !isAdmin) return <Navigate to="/" replace />;
  
  return children;
}
