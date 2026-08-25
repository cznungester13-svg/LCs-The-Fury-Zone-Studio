import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { toast } from "sonner";
import { ArrowLeft, CheckCircle2 } from "lucide-react";
import api, { formatApiErrorDetail } from "../lib/api";
import { useCart } from "../context/CartContext";

export default function Checkout() {
  const { cart, refresh } = useCart();
  const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", address: "", city: "" });
  const [placing, setPlacing] = useState(false);
  const [done, setDone] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setPlacing(true);
    try {
      const { data } = await api.post("/orders", form);
      await refresh();
      setDone(data);
      toast.success("Order confirmed!");
    } catch (err) {
      toast.error(formatApiErrorDetail(err.response?.data?.detail));
    } finally {
      setPlacing(false);
    }
  };

  if (done) {
    return (
      <div className="mx-auto max-w-lg px-4 py-24 text-center" data-testid="order-success">
        <CheckCircle2 size={64} strokeWidth={2} className="mx-auto mb-4 text-electric" />
        <h1 className="font-display text-5xl uppercase">Order Locked In!</h1>
        <p className="mt-3 font-mono text-sm text-ash">Order #{done.id.slice(0, 8).toUpperCase()} · ${done.total.toFixed(2)}</p>
        <div className="mt-6 flex justify-center gap-3">
          <Link to="/orders" className="brutal-btn brutal-btn-primary" data-testid="view-orders-btn">View Orders</Link>
          <Link to="/shop" className="brutal-btn" data-testid="keep-shopping-btn">Keep Digging</Link>
        </div>
      </div>
    );
  }

  if (cart.items.length === 0) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center" data-testid="checkout-empty">
        <h1 className="font-display text-4xl uppercase">Nothing to check out</h1>
        <Link to="/shop" className="brutal-btn brutal-btn-primary mt-6">Go Shopping</Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 md:px-6" data-testid="checkout-page">
      <Link to="/cart" className="mb-6 flex items-center gap-2 font-heading text-sm font-bold uppercase hover:text-orange">
        <ArrowLeft size={18} strokeWidth={2.5} /> Back to cart
      </Link>
      <h1 className="mb-6 font-display text-5xl uppercase tracking-tight">Checkout</h1>

      <div className="grid gap-8 lg:grid-cols-3">
        <form onSubmit={submit} className="space-y-4 border-2 border-ink bg-white p-6 lg:col-span-2" style={{ boxShadow: "4px 4px 0 #0A0A0A" }}>
          <h2 className="font-display text-2xl uppercase">Shipping Details</h2>
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Full Name</label>
            <input required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="brutal-input" data-testid="checkout-name" />
          </div>
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">Address</label>
            <input required value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} className="brutal-input" data-testid="checkout-address" />
          </div>
          <div>
            <label className="mb-1 block font-mono text-xs font-bold uppercase">City</label>
            <input required value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} className="brutal-input" data-testid="checkout-city" />
          </div>
          <button type="submit" disabled={placing} className="brutal-btn brutal-btn-primary w-full py-4 text-lg disabled:opacity-50" data-testid="place-order-btn">
            {placing ? "Placing..." : `Place Order · $${cart.total.toFixed(2)}`}
          </button>
        </form>

        <div className="h-fit border-2 border-ink bg-highlighter p-6" style={{ boxShadow: "6px 6px 0 #0A0A0A" }}>
          <h2 className="font-display text-2xl uppercase">Order</h2>
          <div className="mt-4 space-y-2">
            {cart.items.map(({ product, quantity, line_total }) => (
              <div key={product.id} className="flex justify-between gap-2 font-mono text-xs">
                <span className="line-clamp-1">{quantity}× {product.name}</span>
                <span className="font-bold">${line_total.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 flex justify-between border-t-2 border-ink pt-4 font-display text-3xl">
            <span>TOTAL</span><span>${cart.total.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
