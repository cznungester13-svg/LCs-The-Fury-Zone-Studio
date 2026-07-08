import { useEffect, useState } from "react";
import api, { imgUrl } from "@/lib/api";
import { Btn, Spinner, Badge } from "@/components/common";
import { toast } from "sonner";
import { BarChart3, ShoppingBag, Tag, Wallet, Ticket, Package } from "lucide-react";

const TABS = [
  ["overview", "Overview", BarChart3],
  ["orders", "Orders", ShoppingBag],
  ["listings", "Listings", Tag],
  ["products", "Products", Package],
  ["payouts", "Payouts", Wallet],
  ["coupons", "Coupons", Ticket],
];

export default function AdminDashboard() {
  const [tab, setTab] = useState("overview");
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter border-b-2 border-black pb-4 mb-6">Admin Control</h1>
      <div className="flex gap-2 flex-wrap mb-8">
        {TABS.map(([id, label, Icon]) => (
          <button key={id} onClick={() => setTab(id)} data-testid={`admin-tab-${id}`}
            className={`flex items-center gap-2 px-4 py-2 border-2 border-black font-bold uppercase text-sm transition-colors ${tab === id ? "bg-black text-white" : "bg-white hover:bg-zinc-100"}`}>
            <Icon size={16} /> {label}
          </button>
        ))}
      </div>
      <div className="bg-white min-h-[300px]">
        {tab === "overview" && <Overview />}
        {tab === "orders" && <Orders />}
        {tab === "listings" && <Listings />}
        {tab === "products" && <Products />}
        {tab === "payouts" && <Payouts />}
        {tab === "coupons" && <Coupons />}
      </div>
    </div>
  );
}

function Overview() {
  const [m, setM] = useState(null);
  
  useEffect(() => {
    let active = true;
    api.get("/admin/metrics")
      .then(({ data }) => { if (active) setM(data); })
      .catch(() => toast.error("Failed to load platform metrics"));
    return () => { active = false; };
  }, []);

  if (!m) return <Spinner />;

  const cards = [
    ["Revenue", `$${Number(m.revenue || 0).toFixed(2)}`, true], 
    ["Commission", `$${Number(m.commission_earned || 0).toFixed(2)}`],
    ["Orders", m.total_orders || 0], 
    ["Users", m.total_users || 0], 
    ["Products", m.total_products || 0],
    ["Active Listings", m.active_listings || 0], 
    ["Sold Listings", m.sold_listings || 0], 
    ["Pending Payouts", m.pending_payouts || 0],
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4" data-testid="admin-metrics">
      {cards.map(([l, v, accent]) => (
        <div key={l} className={`border-2 border-black p-5 ${accent ? "bg-[#FF3B30] text-white" : "bg-white text-black"}`}>
          <p className="text-3xl font-black">{v}</p>
          <p className="text-xs font-bold uppercase tracking-wider opacity-70 mt-1">{l}</p>
        </div>
      ))}
    </div>
  );
}

function Orders() {
  const [orders, setOrders] = useState(null);

  const load = (active = true) => {
    api.get("/admin/orders")
      .then(({ data }) => { if (active) setOrders(data || []); })
      .catch(() => toast.error("Failed to sync orders view"));
  };

  useEffect(() => {
    let active = true;
    load(active);
    return () => { active = false; };
  }, []);

  const setStatus = async (id, status) => {
    try {
      await api.post(`/admin/orders/${id}/status`, { status });
      toast.success("Status updated");
      load(true);
    } catch {
      toast.error("Failed to update status");
    }
  };

  const refund = async (id) => {
    try {
      await api.post(`/admin/orders/${id}/refund`, { reason: "admin refund" });
      toast.success("Order refunded");
      load(true);
    } catch {
      toast.error("Refund processing failed");
    }
  };

  if (!orders) return <Spinner />;

  return (
    <div className="space-y-3">
      {orders.length === 0 ? <p className="text-zinc-500 italic">No historical orders found.</p> : orders.map((o) => (
        <div key={o.id} className="border-2 border-black p-4 flex flex-wrap justify-between items-center gap-3 bg-white" data-testid={`admin-order-${o.id}`}>
          <div>
            <p className="font-black">#{String(o.id || "").slice(0, 8)} <span className="text-zinc-400 font-normal">— {o.buyer_email}</span></p>
            <p className="text-sm font-mono mt-0.5">${Number(o.total || 0).toFixed(2)} · {(o.items || []).length} items</p>
          </div>
          <div className="flex items-center gap-2">
            <Badge>{o.status}</Badge>
            <select onChange={(e) => e.target.value && setStatus(o.id, e.target.value)} defaultValue="" className="border-2 border-black px-2 py-1 text-sm font-bold uppercase outline-none bg-white" data-testid={`order-status-${o.id}`}>
              <option value="" disabled>Set status</option>
              {["paid", "shipped", "delivered", "cancelled"].map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            {o.status !== "refunded" && <Btn variant="outline" onClick={() => refund(o.id)} className="!px-3 !py-1 text-sm" data-testid={`refund-${o.id}`}>Refund</Btn>}
          </div>
        </div>
      ))}
    </div>
  );
}

function Listings() {
  const [listings, setListings] = useState(null);
  
  const load = (active = true) => {
    api.get("/admin/listings")
      .then(({ data }) => { if (active) setListings(data || []); })
      .catch(() => toast.error("Failed to fetch administrative listings"));
  };

  useEffect(() => {
    let active = true;
    load(active);
    return () => { active = false; };
  }, []);

  const remove = async (id) => {
    try {
      await api.delete(`/admin/listings/${id}`);
      toast.success("Listing removed");
      load(true);
    } catch {
      toast.error("Could not remove listing");
    }
  };

  if (!listings) return <Spinner />;

  return (
    <div className="space-y-3">
      {listings.length === 0 ? <p className="text-zinc-500 italic">No listings tracked.</p> : listings.map((l) => (
        <div key={l.id} className="border-2 border-black p-3 flex items-center gap-3 bg-white" data-testid={`admin-listing-${l.id}`}>
          <img src={l.images?.[0] ? imgUrl(l.images[0]) : "/placeholder-product.jpg"} alt="" className="w-12 h-12 object-cover border border-zinc-200 bg-zinc-50" />
          <div className="flex-1 min-w-0">
            <p className="font-bold truncate text-sm sm:text-base">{l.title}</p>
            <div className="flex gap-2 mt-1"><Badge>{l.status}</Badge><Badge>{l.condition}</Badge></div>
          </div>
          <span className="font-black text-sm sm:text-base">${Number(l.price || 0).toFixed(2)}</span>
          {l.status === "active" && <Btn variant="outline" onClick={() => remove(l.id)} className="!px-3 !py-1 text-sm" data-testid={`remove-listing-${l.id}`}>Remove</Btn>}
        </div>
      ))}
    </div>
  );
}

function Products() {
  const [products, setProducts] = useState(null);
  const [depts, setDepts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [form, setForm] = useState({ title: "", description: "", price: "", department_id: "", brand_id: "", stock: "", featured: false });
  const [imgUrls, setImgUrls] = useState("");

  const load = (active = true) => {
    api.get("/products?limit=100").then(({ data }) => { if (active) setProducts(data || []); });
  };

  useEffect(() => {
    let active = true;
    load(active);
    api.get("/departments").then(({ data }) => { if (active) setDepts(data || []); });
    api.get("/brands").then(({ data }) => { if (active) setBrands(data || []); });
    return () => { active = false; };
  }, []);

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const create = async (e) => {
    e.preventDefault();
    try {
      await api.post("/products", {
        title: form.title, 
        description: form.description, 
        price: Number(form.price),
        department_id: form.department_id || null, 
        brand_id: form.brand_id || null,
        stock: Number(form.stock) || 0, 
        featured: form.featured,
        images: imgUrls.split(",").map((s) => s.trim()).filter(Boolean),
      });
      toast.success("Product created successfully");
      setForm({ title: "", description: "", price: "", department_id: "", brand_id: "", stock: "", featured: false });
      setImgUrls("");
      load(true);
    } catch (err) { 
      toast.error("Failed to create unified item catalog entry"); 
    }
  };

  const del = async (id) => {
    try {
      await api.delete(`/products/${id}`);
      toast.success("Product deactivated");
      load(true);
    } catch {
      toast.error("Failed to deactivate product catalog slot");
    }
  };

  if (!products) return <Spinner />;

  return (
    <div className="grid lg:grid-cols-[360px_1fr] gap-8">
      <form onSubmit={create} className="border-2 border-black p-5 space-y-3 h-fit bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]" data-testid="product-form">
        <h3 className="font-black uppercase tracking-tight text-lg">New Product Entry</h3>
        <input required placeholder="Title" value={form.title} onChange={set("title")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none text-sm font-medium" data-testid="product-title" />
        <textarea placeholder="Description" value={form.description} onChange={set("description")} rows={2} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none text-sm font-medium" />
        <div className="grid grid-cols-2 gap-2">
          <input required type="number" step="0.01" placeholder="Price" value={form.price} onChange={set("price")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none font-mono text-sm" data-testid="product-price-input" />
          <input type="number" placeholder="Stock" value={form.stock} onChange={set("stock")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none font-mono text-sm" data-testid="product-stock" />
        </div>
        <select value={form.department_id} onChange={set("department_id")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none bg-white text-sm font-medium">
          <option value="">Select Department</option>{depts.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <select value={form.brand_id} onChange={set("brand_id")} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none bg-white text-sm font-medium">
          <option value="">Select Brand</option>{brands.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
        </select>
        <input placeholder="Image URLs (comma separated)" value={imgUrls} onChange={(e) => setImgUrls(e.target.value)} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none text-xs font-mono" data-testid="product-images" />
        <label className="flex items-center gap-2 text-xs font-black uppercase select-none"><input type="checkbox" checked={form.featured} onChange={(e) => setForm({ ...form, featured: e.target.checked })} className="w-4 h-4 accent-black" /> Promote to Featured</label>
        <Btn type="submit" className="w-full text-xs tracking-wider uppercase font-black mt-2">Create product</Btn>
      </form>
      <div className="space-y-3">
        {products.length === 0 ? <p className="text-zinc-500 italic">No platform inventory cataloged yet.</p> : products.map((p) => (
          <div key={p.id} className="border-2 border-black p-3 flex items-center gap-3 bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            <img src={p.images?.[0] ? imgUrl(p.images[0]) : "/placeholder-product.jpg"} alt="" className="w-12 h-12 object-cover border border-zinc-200 bg-zinc-50 shrink-0" />
            <div className="flex-1 min-w-0"><p className="font-bold truncate text-sm sm:text-base">{p.title}</p><p className="text-xs font-mono text-zinc-400 mt-0.5">Stock Context: {p.stock}</p></div>
            <span className="font-black font-mono text-sm sm:text-base">${Number(p.price || 0).toFixed(2)}</span>
            <Btn variant="outline" onClick={() => del(p.id)} className="!px-3 !py-1 text-sm shrink-0">Remove</Btn>
          </div>
        ))}
      </div>
    </div>
  );
}

function Payouts() {
  const [payouts, setPayouts] = useState(null);
  
  const load = (active = true) => {
    api.get("/admin/payouts")
      .then(({ data }) => { if (active) setPayouts(data || []); })
      .catch(() => toast.error("Could not sync settlement ledger"));
  };

  useEffect(() => {
    let active = true;
    load(active);
    return () => { active = false; };
  }, []);

  const approve = async (id) => {
    try {
      await api.post(`/admin/payouts/${id}/approve`);
      toast.success("Settlement request approved");
      load(true);
    } catch {
      toast.error("Failed to execute ledger approval handshake");
    }
  };

  if (!payouts) return <Spinner />;

  return (
    <div className="space-y-3">
      {payouts.length === 0 ? <p className="text-zinc-500 italic p-2">No active seller payout requests pending verification.</p> : payouts.map((p) => (
        <div key={p.id} className="border-2 border-black p-4 flex justify-between items-center bg-white" data-testid={`admin-payout-${p.id}`}>
          <div><p className="font-black text-base sm:text-lg font-mono">${Number(p.amount || 0).toFixed(2)}</p><p className="text-xs sm:text-sm text-zinc-500 font-mono mt-0.5">{p.seller_email}</p></div>
          <div className="flex items-center gap-3">
            <Badge className={p.status === "paid" ? "!bg-green-100 text-green-800" : "!bg-yellow-100 text-yellow-800"}>{p.status}</Badge>
            {p.status === "pending" && <Btn onClick={() => approve(p.id)} className="!px-3 !py-1 text-sm" data-testid={`approve-payout-${p.id}`}>Approve</Btn>}
          </div>
        </div>
      ))}
    </div>
  );
}

function Coupons() {
  const [coupons, setCoupons] = useState(null);
  const [form, setForm] = useState({ code: "", percent_off: "", description: "" });
  
  const load = (active = true) => {
    api.get("/admin/coupons")
      .then(({ data }) => { if (active) setCoupons(data || []); })
      .catch(() => toast.error("Could not load validation codes"));
  };

  useEffect(() => {
    let active = true;
    load(active);
    return () => { active = false; };
  }, []);

  const create = async (e) => {
    e.preventDefault();
    try {
      await api.post("/admin/coupons", { code: form.code.toUpperCase().trim(), percent_off: Number(form.percent_off), description: form.description });
      toast.success("Discount voucher token saved");
      setForm({ code: "", percent_off: "", description: "" });
      load(true);
    } catch { 
      toast.error("Voucher instantiation rejected"); 
    }
  };

  if (!coupons) return <Spinner />;

  return (
    <div className="grid lg:grid-cols-[320px_1fr] gap-8">
      <form onSubmit={create} className="border-2 border-black p-5 space-y-3 h-fit bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
        <h3 className="font-black uppercase tracking-tight text-lg">New Coupon</h3>
        <input required placeholder="PROMOCODE100" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none uppercase font-mono text-sm" data-testid="coupon-code" />
        <input required type="number" max="100" min="1" placeholder="Percent off (%)" value={form.percent_off} onChange={(e) => setForm({ ...form, percent_off: e.target.value })} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none font-mono text-sm" data-testid="coupon-percent" />
        <input placeholder="Internal Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none text-sm font-medium" />
        <Btn type="submit" className="w-full text-xs font-black uppercase tracking-wider mt-2">Create Coupon</Btn>
      </form>
      <div className="space-y-3">
        {coupons.length === 0 ? <p className="text-zinc-500 italic">No discount configurations available.</p> : coupons.map((c) => (
          <div key={c.id} className="border-2 border-black p-4 flex justify-between items-center bg-white shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
            <div className="min-w-0"><p className="font-black text-base sm:text-lg font-mono tracking-tight text-black truncate">{c.code}</p><p className="text-xs sm:text-sm text-zinc-500 truncate mt-0.5">{c.description || "No description set"}</p></div>
            <Badge className="!bg-[#FF3B30] !text-white !border-[#FF3B30] font-mono shrink-0 font-bold">{c.percent_off}% OFF</Badge>
          </div>
        ))}
      </div>
    </div>
  );
}
