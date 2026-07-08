import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
// Fix: Adjust relative path imports to step up one directory layer safely
import { useAuth } from "../context/AuthContext";
import { Btn } from "../components/common";
import { apiError } from "../lib/api";
import { toast } from "sonner";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", phone: "", as_seller: false });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await register(form);
      toast.success("Account created — welcome!");
      navigate("/");
    } catch (err) {
      setError(apiError(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md border-2 border-black brutal-shadow bg-white p-8">
        <h1 className="text-4xl font-black uppercase tracking-tighter">Register</h1>
        <p className="text-zinc-500 mt-1">Join the Zone. It's free.</p>
        {error && <div className="mt-4 border-2 border-[#FF3B30] bg-red-50 text-[#FF3B30] px-4 py-2 text-sm font-bold" data-testid="register-error">{error}</div>}
        
        <form onSubmit={submit} className="mt-6 space-y-4">
          <Field label="Full name" value={form.full_name} onChange={set("full_name")} testid="register-name" required />
          <Field label="Email" type="email" value={form.email} onChange={set("email")} testid="register-email" required />
          <Field label="Password" type="password" value={form.password} onChange={set("password")} testid="register-password" required />
          <Field label="Phone (optional)" value={form.phone} onChange={set("phone")} testid="register-phone" />
          
          <label className="flex items-center gap-3 border-2 border-zinc-200 px-4 py-3 cursor-pointer">
            <input type="checkbox" checked={form.as_seller} onChange={(e) => setForm({ ...form, as_seller: e.target.checked })} data-testid="register-seller" />
            <span className="font-bold text-sm uppercase">I want to sell used items too</span>
          </label>
          
          <Btn type="submit" disabled={loading} className="w-full" data-testid="register-submit">{loading ? "Creating..." : "Create account"}</Btn>
        </form>
        <p className="mt-4 text-sm text-center">Already have an account? <Link to="/login" className="font-bold text-[#FF3B30] underline">Login</Link></p>
      </div>
    </div>
  );
}

function Field({ label, testid, ...props }) {
  return (
    <div>
      <label className="block text-sm font-bold uppercase tracking-wider mb-2">{label}</label>
      <input {...props} data-testid={testid} className="w-full border-2 border-zinc-200 focus:border-black px-4 py-3 outline-none" />
    </div>
  );
}
