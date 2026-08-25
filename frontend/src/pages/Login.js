import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogIn } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    const res = await login(email, password);
    setLoading(false);
    if (res.ok) navigate("/");
    else setError(res.error);
  };

  return (
    <div className="mx-auto max-w-md px-4 py-16" data-testid="login-page">
      <div className="border-2 border-ink bg-white p-8" style={{ boxShadow: "8px 8px 0 #FF5C00" }}>
        <div className="mb-6">
          <span className="bg-ink px-2 py-1 font-display text-2xl leading-none text-highlighter">LC</span>
          <h1 className="mt-4 font-display text-4xl uppercase leading-none tracking-tight">Welcome back</h1>
          <p className="mt-2 font-mono text-xs text-ash">Sign in to grab your treasure.</p>
        </div>
        {error && <div className="mb-4 border-2 border-ink bg-sale px-3 py-2 font-mono text-xs font-bold text-white" data-testid="login-error">{error}</div>}
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="brutal-input" data-testid="login-email" />
          </div>
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Password</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="brutal-input" data-testid="login-password" />
          </div>
          <button type="submit" disabled={loading} className="brutal-btn brutal-btn-primary w-full py-3 disabled:opacity-50" data-testid="login-submit">
            <LogIn size={18} strokeWidth={2.5} /> {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <p className="mt-6 font-mono text-xs text-ash">
          No account?{" "}
          <Link to="/register" className="font-bold text-orange underline" data-testid="to-register">Create one</Link>
        </p>
      </div>
    </div>
  );
}
