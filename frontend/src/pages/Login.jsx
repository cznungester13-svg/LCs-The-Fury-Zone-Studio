import { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
// Fix: Adjust relative path imports to step up one directory layer safely
import { useAuth } from "../context/AuthContext";
import { Btn } from "../components/common";
import { apiError } from "../lib/api";
import { toast } from "sonner";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      toast.success("Welcome back to the Zone");
      navigate(location.state?.from || "/");
    } catch (err) {
      setError(apiError(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  const quick = (em) => { 
    setEmail(em); 
    setPassword(em.startsWith("admin") ? "Admin@123" : "Password@123"); 
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md border-2 border-black brutal-shadow bg-white p-8">
        <h1 className="text-4xl font-black uppercase tracking-tighter">Login</h1>
        <p className="text-zinc-500 mt-1">Enter the Fury Zone.</p>
        {error && <div className="mt-4 border-2 border-[#FF3B30] bg-red-50 text-[#FF3B30] px-4 py-2 text-sm font-bold" data-testid="login-error">{error}</div>}
        
        <form onSubmit={submit} className="mt-6 space-y-4">
          <div>
            <label className="block text-sm font-bold uppercase tracking-wider mb-2">Email</label>
            <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="w-full border-2 border-zinc-200 focus:border-black px-4 py-3 outline-none" data-testid="login-email" />
          </div>
          <div>
            <label className="block text-sm font-bold uppercase tracking-wider mb-2">Password</label>
            <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="w-full border-2 border-zinc-200 focus:border-black px-4 py-3 outline-none" data-testid="login-password" />
          </div>
          <Btn type="submit" disabled={loading} className="w-full" data-testid="login-submit">{loading ? "Entering..." : "Login"}</Btn>
        </form>
        
        <p className="mt-4 text-sm text-center">No account? <Link to="/register" className="font-bold text-[#FF3B30] underline">Register</Link></p>
        
        <div className="mt-6 pt-4 border-t-2 border-dashed border-zinc-200 text-xs">
          <p className="font-mono uppercase tracking-widest text-zinc-400 mb-2">Quick demo login</p>
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => quick("buyer@furyzone.com")} className="border border-black px-2 py-1 hover:bg-black hover:text-white">Buyer</button>
            <button onClick={() => quick("seller@furyzone.com")} className="border border-black px-2 py-1 hover:bg-black hover:text-white">Seller</button>
            <button onClick={() => quick("admin@furyzone.com")} className="border border-black px-2 py-1 hover:bg-black hover:text-white">Admin</button>
          </div>
        </div>
      </div>
    </div>
  );
}
