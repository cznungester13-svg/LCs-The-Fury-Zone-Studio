import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Package, ArrowRight } from "lucide-react";
import api from "../lib/api";

export default function Orders() {
  const [orders, setOrders] = useState(null);

  useEffect(() => {
    api.get("/orders").then((r) => setOrders(r.data)).catch(() => setOrders([]));
  }, []);

  if (orders === null) return <div className="py-24 text-center font-display text-3xl uppercase text-ash">Loading orders...</div>;

  if (orders.length === 0) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center" data-testid="orders-empty">
        <Package size={56} strokeWidth={2} className="mx-auto mb-4 text-ash" />
        <h1 className="font-display text-4xl uppercase">No orders yet</h1>
        <Link to="/shop" className="brutal-btn brutal-btn-primary mt-6">Start Digging <ArrowRight size={18} strokeWidth={2.5} /></Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 md:px-6" data-testid="orders-page">
      <h1 className="mb-6 font-display text-5xl uppercase tracking-tight">Your Orders</h1>
      <div className="space-y-4">
        {orders.map((o) => (
          <div key={o.id} className="border-2 border-ink bg-white p-5" style={{ boxShadow: "4px 4px 0 #0A0A0A" }} data-testid={`order-${o.id}`}>
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b-2 border-ink pb-3">
              <div>
                <span className="font-mono text-xs uppercase text-ash">Order #{o.id.slice(0, 8).toUpperCase()}</span>
                <div className="font-mono text-xs text-ash">{new Date(o.created_at).toLocaleString()}</div>
              </div>
              <span className="tag bg-electric text-white">{o.status}</span>
              <span className="font-display text-2xl text-orange">${o.total.toFixed(2)}</span>
            </div>
            <div className="flex flex-wrap gap-3">
              {o.items.map((it) => (
                <div key={it.product_id} className="flex items-center gap-2">
                  <img src={it.image} alt={it.name} className="h-12 w-12 border-2 border-ink object-cover" />
                  <span className="font-mono text-xs">{it.quantity}× {it.name}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
