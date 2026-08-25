import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Upload, Tag, Loader2, PlusCircle } from "lucide-react";
import api, { formatApiErrorDetail } from "../lib/api";
import { useAuth } from "../context/AuthContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const DEPTS = [
  { slug: "fashion", name: "Fashion & Apparel" },
  { slug: "electronics", name: "Electronics" },
  { slug: "home", name: "Home & Decor" },
  { slug: "books", name: "Books & Media" },
  { slug: "sports", name: "Sports & Outdoors" },
  { slug: "toys", name: "Toys & Games" },
];
const CONDITIONS = ["Like New", "Gently Used", "Well Loved", "Vintage", "Refurbished"];

export default function Sell() {
  const { user, ready } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", department: "fashion", price: "", condition: "Gently Used", description: "", stock: 1 });
  const [image, setImage] = useState("");
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [mine, setMine] = useState([]);

  useEffect(() => {
    if (ready && !user) navigate("/login");
  }, [ready, user, navigate]);

  useEffect(() => {
    if (user) api.get("/products/mine").then((r) => setMine(r.data)).catch(() => {});
  }, [user]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await api.post("/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setImage(`${BACKEND_URL}${data.url}`);
      toast.success("Photo uploaded");
    } catch (err) {
      toast.error(formatApiErrorDetail(err.response?.data?.detail));
    } finally {
      setUploading(false);
    }
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!image) return toast.error("Upload a photo of your item first");
    setSaving(true);
    try {
      const { data } = await api.post("/products", {
        ...form,
        price: parseFloat(form.price),
        stock: parseInt(form.stock, 10),
        image,
      });
      toast.success("Listed! It's live on the marketplace.");
      navigate(`/product/${data.id}`);
    } catch (err) {
      toast.error(formatApiErrorDetail(err.response?.data?.detail));
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 md:px-6" data-testid="sell-page">
      <div className="mb-6 border-2 border-ink bg-electric p-6 text-white" style={{ boxShadow: "6px 6px 0 #0A0A0A" }}>
        <span className="tag bg-highlighter text-ink">SELLER HUB</span>
        <h1 className="mt-3 font-display text-5xl uppercase leading-none tracking-tight">List Your Junk</h1>
        <p className="mt-2 font-mono text-sm text-white/80">Snap it, price it, sell it. Every $20 in sales gets you a raffle ticket.</p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <form onSubmit={submit} className="space-y-4 border-2 border-ink bg-white p-6 lg:col-span-2" style={{ boxShadow: "4px 4px 0 #0A0A0A" }}>
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Item Photo</label>
            <div className="flex items-center gap-4">
              <div className="flex h-28 w-28 shrink-0 items-center justify-center border-2 border-ink bg-paper">
                {image ? (
                  <img src={image} alt="preview" className="h-full w-full object-cover" data-testid="upload-preview" />
                ) : (
                  <Upload size={28} strokeWidth={2} className="text-ash" />
                )}
              </div>
              <label className="brutal-btn cursor-pointer" data-testid="upload-btn">
                {uploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} strokeWidth={2.5} />}
                {uploading ? "Uploading..." : "Upload Photo"}
                <input type="file" accept="image/*" className="hidden" onChange={handleUpload} data-testid="file-input" />
              </label>
            </div>
          </div>

          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Item Name</label>
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="brutal-input" data-testid="sell-name" placeholder="e.g. Vintage Levi's Denim Jacket" />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block font-mono text-xs font-bold uppercase">Department</label>
              <select value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} className="brutal-input" data-testid="sell-department">
                {DEPTS.map((d) => <option key={d.slug} value={d.slug}>{d.name}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block font-mono text-xs font-bold uppercase">Condition</label>
              <select value={form.condition} onChange={(e) => setForm({ ...form, condition: e.target.value })} className="brutal-input" data-testid="sell-condition">
                {CONDITIONS.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block font-mono text-xs font-bold uppercase">Price ($)</label>
              <input required type="number" step="0.01" min="0.01" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} className="brutal-input" data-testid="sell-price" placeholder="4.99" />
            </div>
            <div>
              <label className="mb-1 block font-mono text-xs font-bold uppercase">Quantity</label>
              <input required type="number" min="1" value={form.stock} onChange={(e) => setForm({ ...form, stock: e.target.value })} className="brutal-input" data-testid="sell-stock" />
            </div>
          </div>

          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Description</label>
            <textarea required rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="brutal-input resize-none" data-testid="sell-description" placeholder="Condition notes, size, story..." />
          </div>

          <button type="submit" disabled={saving} className="brutal-btn brutal-btn-primary w-full py-4 text-lg disabled:opacity-50" data-testid="sell-submit">
            <Tag size={20} strokeWidth={2.5} /> {saving ? "Listing..." : "List It"}
          </button>
        </form>

        <div>
          <h2 className="mb-3 font-display text-2xl uppercase">Your Listings</h2>
          {mine.length === 0 ? (
            <div className="border-2 border-dashed border-ink/40 p-6 text-center font-mono text-xs text-ash" data-testid="no-listings">
              <PlusCircle className="mx-auto mb-2 text-ash" /> Nothing listed yet.
            </div>
          ) : (
            <div className="space-y-3" data-testid="my-listings">
              {mine.map((p) => (
                <Link key={p.id} to={`/product/${p.id}`} className="flex items-center gap-3 border-2 border-ink bg-white p-2 hover:bg-highlighter">
                  <img src={p.image} alt={p.name} className="h-12 w-12 border-2 border-ink object-cover" />
                  <div className="min-w-0 flex-1">
                    <div className="truncate font-heading text-xs font-bold">{p.name}</div>
                    <div className="font-mono text-xs text-orange">${p.price.toFixed(2)} · {p.stock} left</div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
