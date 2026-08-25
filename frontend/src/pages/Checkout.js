import React, { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { ArrowLeft, CreditCard, ShieldCheck } from "lucide-react";
import api, { formatApiErrorDetail } from "../lib/api";
import { useCart } from "../context/CartContext";

export default function Checkout() {
  const { cart } = useCart();
  const [form, setForm] = useState({ full_name: "", address: "", city: "" });
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { data } = await api.post("/payments/checkout", {
        origin_url: window.location.origin,
        shipping: form,
      });
      window.location.href = data.checkout_url;
    } catch (err) {
      toast.error(formatApiErrorDetail(err.response?.data?.detail));
      setLoading(false);
    }
  };

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
          <button type="submit" disabled={loading} className="brutal-btn brutal-btn-primary w-full py-4 text-lg disabled:opacity-50" data-testid="place-order-btn">
            <CreditCard size={20} strokeWidth={2.5} /> {loading ? "Redirecting to Stripe..." : `Pay $${cart.total.toFixed(2)}`}
          </button>
          <p className="flex items-center justify-center gap-2 font-mono text-xs text-ash">
            <ShieldCheck size={14} strokeWidth={2.5} /> Secured by Stripe · Test card 4242 4242 4242 4242
          </p>
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
