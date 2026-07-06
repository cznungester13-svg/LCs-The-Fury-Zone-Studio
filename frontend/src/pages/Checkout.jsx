import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { CheckCircle2, Lock, ArrowRight } from "lucide-react";
import { useCart } from "../context/CartContext";
import { api, currency } from "../lib/api";
import { toast } from "sonner";

export default function Checkout() {
  const { items, subtotal, clearCart } = useCart();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [order, setOrder] = useState(null);
  const [form, setForm] = useState({ full_name: "", email: "", address: "", city: "", zip_code: "" });

  const shipping = subtotal >= 75 || subtotal === 0 ? 0 : 6.99;
  const total = subtotal + shipping;

  const update = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    if (Object.values(form).some((v) => !v.trim())) {
      toast.error("Please fill in all fields.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post("/orders", {
        items: items.map((i) => ({ id: i.id, name: i.name, price: i.price, quantity: i.quantity, image: i.image })),
        ...form,
      });
      setOrder(res.data);
      clearCart();
    } catch {
      toast.error("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (order) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center px-4 py-24 text-center" data-testid="order-confirmation">
        <span className="flex h-20 w-20 items-center justify-center rounded-full bg-emerald-100">
          <CheckCircle2 className="h-11 w-11 text-emerald-600" />
        </span>
        <h1 className="font-display mt-6 text-3xl font-bold">Order confirmed!</h1>
        <p className="mt-2 text-muted-foreground">
          Thanks, {order.full_name.split(" ")[0]}. Your order <span className="font-bold text-foreground" data-testid="order-id">#{order.id}</span> is on its way.
        </p>
        <div className="mt-6 w-full rounded-2xl border border-border bg-secondary/40 p-6 text-left text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground">Total paid</span><span className="font-display font-bold">{currency(order.total)}</span></div>
          <div className="mt-2 flex justify-between"><span className="text-muted-foreground">Confirmation sent to</span><span className="font-semibold">{order.email}</span></div>
        </div>
        <Link to="/shop" className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3 font-bold text-white transition-all hover:bg-primary/90 active:scale-95">
          Continue shopping <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-lg px-4 py-28 text-center">
        <h1 className="font-display text-2xl font-bold">Your cart is empty</h1>
        <Link to="/shop" className="mt-4 inline-block text-primary hover:underline">Go shopping</Link>
      </div>
    );
  }

  const field = (label, key, type = "text", full = false) => (
    <div className={full ? "sm:col-span-2" : ""}>
      <label className="mb-1.5 block text-sm font-medium">{label}</label>
      <input
        type={type}
        value={form[key]}
        onChange={update(key)}
        data-testid={`checkout-${key}`}
        className="h-11 w-full rounded-xl border border-input bg-white px-4 text-sm outline-none focus:border-foreground focus:ring-4 focus:ring-primary/10"
      />
    </div>
  );

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 md:px-8" data-testid="checkout-page">
      <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">Checkout</h1>
      <div className="mt-8 grid gap-8 lg:grid-cols-5">
        <form onSubmit={submit} className="lg:col-span-3" data-testid="checkout-form">
          <div className="rounded-2xl border border-border bg-white p-6">
            <h2 className="font-display text-lg font-bold">Shipping details</h2>
            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              {field("Full name", "full_name", "text", true)}
              {field("Email", "email", "email", true)}
              {field("Address", "address", "text", true)}
              {field("City", "city")}
              {field("ZIP / Postal code", "zip_code")}
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-border bg-white p-6">
            <h2 className="font-display flex items-center gap-2 text-lg font-bold">
              <Lock className="h-4 w-4 text-primary" /> Payment
            </h2>
            <p className="mt-2 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-800">
              Demo mode — this is a mock checkout. No real payment is processed and no card details are collected.
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            data-testid="place-order-button"
            className="mt-6 flex h-12 w-full items-center justify-center gap-2 rounded-full bg-primary font-bold text-white transition-all hover:bg-primary/90 active:scale-95 disabled:opacity-60"
          >
            {loading ? "Placing order…" : `Place order · ${currency(total)}`}
          </button>
        </form>

        <div className="h-fit rounded-2xl border border-border bg-secondary/40 p-6 lg:col-span-2" data-testid="checkout-summary">
          <h2 className="font-display text-lg font-bold">Your order</h2>
          <div className="mt-4 space-y-3">
            {items.map((i) => (
              <div key={i.id} className="flex items-center gap-3">
                <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-lg bg-white">
                  <img src={i.image} alt={i.name} className="h-full w-full object-cover" />
                  <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-foreground text-[10px] font-bold text-white">{i.quantity}</span>
                </div>
                <p className="line-clamp-2 flex-1 text-sm font-medium">{i.name}</p>
                <span className="text-sm font-semibold">{currency(i.price * i.quantity)}</span>
              </div>
            ))}
          </div>
          <div className="mt-5 space-y-2 border-t border-border pt-4 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Subtotal</span><span className="font-semibold">{currency(subtotal)}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Shipping</span><span className="font-semibold">{shipping === 0 ? "Free" : currency(shipping)}</span></div>
            <div className="flex justify-between border-t border-border pt-2 text-base"><span className="font-bold">Total</span><span className="font-display font-extrabold">{currency(total)}</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
