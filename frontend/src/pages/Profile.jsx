import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Btn, Badge, Spinner, EmptyState } from "@/components/common";
import { toast } from "sonner";
import { Plus, Heart } from "lucide-react";

export default function Profile() {
  const { user } = useAuth();
  const [addresses, setAddresses] = useState(null);
  const [wishlist, setWishlist] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ label: "Home", full_name: "", line1: "", city: "", state: "", postal_code: "", country: "USA", phone: "" });

  const load = () => {
    Promise.all([
      api.get("/addresses").catch(() => ({ data: [] })),
      api.get("/wishlist").catch(() => ({ data: [] }))
    ]).then(([{ data: addrData }, { data: wishData }]) => {
      setAddresses(addrData || []);
      setWishlist(wishData || []);
    });
  };

  useEffect(() => {
    load();
  }, []);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const addAddress = async (e) => {
    e.preventDefault();
    try {
      await api.post("/addresses", form);
      toast.success("Address saved");
      setShowForm(false);
      setForm({ label: "Home", full_name: "", line1: "", city: "", state: "", postal_code: "", country: "USA", phone: "" });
      load();
    } catch (err) {
      toast.error("Failed to save address");
    }
  };

  const removeWish = async (item) => {
    try {
      await api.post("/wishlist/toggle", { item_type: item.item_type, item_id: item.item_id });
      toast.success("Removed from wishlist");
      load();
    } catch (err) {
      toast.error("Failed to modify wishlist");
    }
  };

  if (!addresses || !wishlist) return <Spinner />;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="border-2 border-black brutal-shadow p-6 mb-10 flex items-center gap-4 bg-white">
        <div className="w-16 h-16 bg-[#FF3B30] text-white flex items-center justify-center text-2xl font-black select-none">
          {user?.full_name?.[0] || "?"}
        </div>
        <div>
          <h1 className="text-2xl font-black uppercase">{user?.full_name || "Guest Account"}</h1>
          <p className="text-zinc-500 font-mono text-sm">{user?.email}</p>
          <div className="flex flex-wrap gap-2 mt-2">
            {user?.roles?.map((r) => <Badge key={r} className="text-xs uppercase font-bold">{r}</Badge>)}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-10">
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-black uppercase tracking-tight">Addresses</h2>
            <Btn variant="secondary" onClick={() => setShowForm((v) => !v)} className="!px-3 !py-2 text-sm" data-testid="add-address-btn">
              <Plus size={16} /> Add
            </Btn>
          </div>
          
          {showForm && (
            <form onSubmit={addAddress} className="border-2 border-black p-4 space-y-3 mb-4 bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
              <input required placeholder="Full name" value={form.full_name} onChange={set("full_name")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none" data-testid="addr-name" />
              <input required placeholder="Street address" value={form.line1} onChange={set("line1")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none" data-testid="addr-line1" />
              <div className="grid grid-cols-2 gap-3">
                <input required placeholder="City" value={form.city} onChange={set("city")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none" data-testid="addr-city" />
                <input required placeholder="Postal code" value={form.postal_code} onChange={set("postal_code")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none" data-testid="addr-postal" />
              </div>
              <Btn type="submit" className="w-full uppercase text-xs tracking-wider">Save address</Btn>
            </form>
          )}

          {addresses.length === 0 ? (
            <p className="text-zinc-500 text-sm italic">No saved addresses.</p>
          ) : (
            <div className="space-y-3">
              {addresses.map((a) => (
                <div key={a.id} className="border-2 border-black bg-white p-4 shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  <p className="font-black uppercase text-xs tracking-wide text-zinc-400 mb-1">{a.label || "Address"}</p>
                  <p className="font-bold text-sm text-zinc-900">{a.full_name}</p>
                  <p className="text-sm text-zinc-600 font-mono mt-0.5">{a.line1}, {a.city} {a.postal_code}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <h2 className="text-2xl font-black uppercase mb-4 flex items-center gap-2 tracking-tight">
            <Heart className="text-[#FF3B30] fill-[#FF3B30]" size={24} /> Wishlist
          </h2>
          {wishlist.length === 0 ? (
            <EmptyState title="Empty wishlist" subtitle="Heart items to save them." />
          ) : (
            <div className="space-y-3">
              {wishlist.map((w) => (
                <div key={w.id} className="flex gap-3 border-2 border-black bg-white p-3 items-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  <img src={w.image ? imgUrl(w.image) : "/placeholder-product.jpg"} alt="" className="w-14 h-14 object-cover border border-zinc-200 bg-zinc-50" />
                  <div className="flex-1 min-w-0">
                    <Link to={`/${w.item_type === "listing" ? "listing" : "product"}/${w.item_id}`} className="font-bold hover:text-[#FF3B30] block truncate text-sm">
                      {w.title || "Saved Item"}
                    </Link>
                    <span className="font-mono text-xs text-zinc-400 uppercase tracking-tight">{w.item_type}</span>
                  </div>
                  <span className="font-black text-sm">${Number(w.price || 0).toFixed(2)}</span>
                  <button onClick={() => removeWish(w)} className="text-[#FF3B30] p-1" aria-label="Remove from wishlist">
                    <Heart size={18} className="fill-[#FF3B30]" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
