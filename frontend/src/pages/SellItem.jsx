import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Btn, CONDITION_LABEL } from "@/components/common";
import { toast } from "sonner";
import { Upload, X, Loader2 } from "lucide-react";

export default function SellItem() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ title: "", description: "", price: "", condition: "good" });
  const [images, setImages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    setUploading(true);
    try {
      for (const file of files) {
        const fd = new FormData();
        fd.append("file", file);
        const { data } = await api.post("/upload", fd, { headers: { "Content-Type": "multipart/form-data" } });
        setImages((prev) => [...prev, data.url]);
      }
      toast.success("Photos processed successfully");
    } catch (err) {
      toast.error("One or more images failed to upload");
    } finally {
      setUploading(false);
    }
  };

  const removeImage = (i) => setImages(images.filter((_, idx) => idx !== i));

  const submit = async (e) => {
    e.preventDefault();
    if (!form.price || Number(form.price) <= 0) return toast.error("Enter a valid price");
    if (images.length === 0) return toast.error("Add at least one photo");
    setSubmitting(true);
    try {
      const { data } = await api.post("/listings", {
        title: form.title,
        description: form.description,
        price: Number(form.price),
        condition: form.condition,
        images,
      });
      toast.success("Listing is live!");
      navigate(`/listing/${data.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Could not create listing");
    } finally {
      setSubmitting(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-md mx-auto py-24 text-center px-4">
        <h1 className="text-3xl font-black uppercase">Login to sell</h1>
        <p className="text-zinc-500 mt-2">You need an account to list items.</p>
        <Btn className="mt-6" onClick={() => navigate("/login")}>Login</Btn>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="border-b-2 border-black pb-4 mb-8">
        <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter">Sell an Item</h1>
        <p className="text-zinc-500 mt-1">List your used gear — it goes live instantly.</p>
      </div>

      <form onSubmit={submit} className="space-y-6">
        <div>
          <label className="block text-sm font-bold uppercase tracking-wider mb-2">Photos</label>
          <div className="flex flex-wrap gap-3">
            {images.map((im, i) => (
              <div key={i} className="relative w-24 h-24 border-2 border-black overflow-hidden">
                <img src={imgUrl(im)} alt="" className="w-full h-full object-cover" />
                <button type="button" onClick={() => removeImage(i)} className="absolute top-0 right-0 bg-[#FF3B30] text-white p-0.5"><X size={14} /></button>
              </div>
            ))}
            <label className={`w-24 h-24 border-2 border-dashed border-black flex flex-col items-center justify-center cursor-pointer hover:bg-zinc-100 ${uploading ? 'opacity-50 pointer-events-none' : ''}`} data-testid="upload-photo">
              {uploading ? <Loader2 className="animate-spin" size={20} /> : <><Upload size={20} /><span className="text-[10px] uppercase font-bold mt-1">Add</span></>}\n              <input type="file" accept="image/*" multiple onChange={handleUpload} className="hidden" disabled={uploading} />
            </label>
          </div>
        </div>

        <Field label="Title" value={form.title} onChange={set("title")} required testid="listing-title" />
        <div>
          <label className="block text-sm font-bold uppercase tracking-wider mb-2">Description</label>
          <textarea value={form.description} onChange={set("description")} rows={4} className="w-full border-2 border-zinc-200 focus:border-black px-4 py-3 outline-none" data-testid="listing-description" required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Price ($)" type="number" step="0.01" value={form.price} onChange={set("price")} required testid="listing-price" />
          <div>
            <label className="block text-sm font-bold uppercase tracking-wider mb-2">Condition</label>
            <select value={form.condition} onChange={set("condition")} className="w-full border-2 border-zinc-200 focus:border-black px-4 py-3 outline-none font-bold uppercase" data-testid="listing-condition">\n              {Object.entries(CONDITION_LABEL).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
        </div>
        <Btn type="submit" disabled={submitting || uploading} className="w-full" data-testid="submit-listing-btn">{submitting ? "Publishing..." : "Publish listing"}</Btn>
      </form>
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
