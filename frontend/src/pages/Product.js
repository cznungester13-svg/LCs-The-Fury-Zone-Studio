import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { ShoppingBag, Star, ArrowLeft, ShieldCheck, Truck, Minus, Plus } from "lucide-react";
import api from "../lib/api";
import ProductCard from "../components/ProductCard";
import { useCart } from "../context/CartContext";

export default function Product() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addItem } = useCart();
  const [data, setData] = useState(null);
  const [qty, setQty] = useState(1);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    window.scrollTo(0, 0);
    setData(null);
    setQty(1);
    api.get(`/products/${id}`)
      .then((r) => setData(r.data))
      .catch(() => setNotFound(true));
  }, [id]);

  if (notFound)
    return <div className="py-24 text-center font-display text-4xl uppercase" data-testid="product-not-found">Product not found</div>;
  if (!data) return <div className="py-24 text-center font-display text-3xl uppercase text-ash">Loading...</div>;

  const p = data.product;
  const discount = Math.round((1 - p.price / p.original_price) * 100);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-6" data-testid="product-page">
      <button onClick={() => navigate(-1)} className="mb-6 flex items-center gap-2 font-heading text-sm font-bold uppercase hover:text-orange" data-testid="back-btn">
        <ArrowLeft size={18} strokeWidth={2.5} /> Back
      </button>

      <div className="grid gap-8 lg:grid-cols-2">
        <div className="relative border-2 border-ink bg-white" style={{ boxShadow: "6px 6px 0 #0A0A0A" }}>
          <img src={p.image} alt={p.name} className="aspect-square w-full object-cover" data-testid="product-image" />
          {discount > 0 && (
            <span className="absolute right-3 top-3 border-2 border-ink bg-sale px-2 py-1 font-display text-xl text-white">-{discount}%</span>
          )}
        </div>

        <div className="flex flex-col">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="tag bg-highlighter text-ink">{p.condition}</span>
            <span className="tag bg-white">{p.department_name}</span>
            <span className="flex items-center gap-1 font-mono text-xs text-ash">
              <Star size={14} className="fill-orange text-orange" strokeWidth={2.5} /> {p.rating}
            </span>
          </div>

          <h1 className="font-display text-4xl uppercase leading-none tracking-tight md:text-5xl" data-testid="product-title">{p.name}</h1>
          <p className="mt-2 font-mono text-xs uppercase text-ash">SKU {p.sku} · {p.stock} in stock</p>

          <div className="mt-5 flex items-end gap-3">
            <span className="font-display text-6xl leading-none text-orange" data-testid="product-price">${p.price.toFixed(2)}</span>
            <span className="mb-1 font-mono text-lg text-ash line-through">${p.original_price.toFixed(2)}</span>
          </div>

          <p className="mt-5 font-body text-base leading-relaxed text-ash" data-testid="product-description">{p.description}</p>

          <div className="mt-6 flex items-center gap-4">
            <div className="flex items-center border-2 border-ink bg-white">
              <button onClick={() => setQty((q) => Math.max(1, q - 1))} className="border-r-2 border-ink p-3 hover:bg-highlighter" data-testid="qty-minus"><Minus size={18} strokeWidth={2.5} /></button>
              <span className="w-12 text-center font-display text-2xl" data-testid="qty-value">{qty}</span>
              <button onClick={() => setQty((q) => q + 1)} className="border-l-2 border-ink p-3 hover:bg-highlighter" data-testid="qty-plus"><Plus size={18} strokeWidth={2.5} /></button>
            </div>
            <button onClick={() => addItem(p, qty)} className="brutal-btn brutal-btn-primary flex-1 py-4 text-lg" data-testid="add-to-cart-detail">
              <ShoppingBag size={20} strokeWidth={2.5} /> Add to Cart
            </button>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3">
            <div className="flex items-center gap-2 border-2 border-ink bg-white p-3">
              <ShieldCheck size={22} strokeWidth={2.5} className="text-electric" />
              <span className="font-mono text-xs font-bold uppercase">Inspected & Verified</span>
            </div>
            <div className="flex items-center gap-2 border-2 border-ink bg-white p-3">
              <Truck size={22} strokeWidth={2.5} className="text-orange" />
              <span className="font-mono text-xs font-bold uppercase">Ships in 2-4 Days</span>
            </div>
          </div>
        </div>
      </div>

      {data.related?.length > 0 && (
        <section className="mt-16">
          <h2 className="mb-6 font-display text-3xl uppercase tracking-tight md:text-4xl">More from {p.department_name}</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {data.related.map((r) => (
              <ProductCard key={r.id} product={r} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
