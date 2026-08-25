import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    const res = await register(form.name, form.email, form.password);
    setLoading(false);
    if (res.ok) navigate("/");
    else setError(res.error);
  };

  return (
    <div className="mx-auto max-w-md px-4 py-16" data-testid="register-page">
      <div className="border-2 border-ink bg-white p-8" style={{ boxShadow: "8px 8px 0 #0038FF" }}>
        <div className="mb-6">
          <span className="bg-ink px-2 py-1 font-display text-2xl leading-none text-highlighter">LC</span>
          <h1 className="mt-4 font-display text-4xl uppercase leading-none tracking-tight">Join the hunt</h1>
          <p className="mt-2 font-mono text-xs text-ash">Create an account. It's free, obviously.</p>
        </div>
        {error && <div className="mb-4 border-2 border-ink bg-sale px-3 py-2 font-mono text-xs font-bold text-white" data-testid="register-error">{error}</div>}
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Name</label>
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="brutal-input" data-testid="register-name" />
          </div>
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Email</label>
            <input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="brutal-input" data-testid="register-email" />
          </div>
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Password</label>
            <input type="password" required minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="brutal-input" data-testid="register-password" />
          </div>
          <button type="submit" disabled={loading} className="brutal-btn brutal-btn-blue w-full py-3 disabled:opacity-50" data-testid="register-submit">
            <UserPlus size={18} strokeWidth={2.5} /> {loading ? "Creating..." : "Create Account"}
          </button>
        </form>
        <p className="mt-6 font-mono text-xs text-ash">
          Already have one?{" "}
          <Link to="/login" className="font-bold text-orange underline" data-testid="to-login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
