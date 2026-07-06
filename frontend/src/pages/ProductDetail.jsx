import React, { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Star, Minus, Plus, ShoppingCart, ArrowLeft, Truck, ShieldCheck, RotateCcw } from "lucide-react";
import { api, currency } from "../lib/api";
import { useCart } from "../context/CartContext";
import { ProductCard } from "../components/ProductCard";

export default function ProductDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { addItem } = useCart();
  const [product, setProduct] = useState(null);
  const [related, setRelated] = useState([]);
  const [qty, setQty] = useState(1);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    setQty(1);
    window.scrollTo(0, 0);
    api
      .get(`/products/${id}`)
      .then((r) => {
        setProduct(r.data);
        return api.get("/products", { params: { category: r.data.category } });
      })
      .then((r) => setRelated(r.data.filter((p) => p.id !== id).slice(0, 5)))
      .catch(() => setNotFound(true));
  }, [id]);

  if (notFound) {
    return (
      <div className="py-32 text-center" data-testid="product-not-found">
        <p className="font-display text-2xl font-bold">Product not found</p>
        <Link to="/shop" className="mt-4 inline-block text-primary hover:underline">Back to shop</Link>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-10 md:px-8">
        <div className="grid gap-10 md:grid-cols-2">
          <div className="aspect-square animate-pulse rounded-3xl bg-secondary" />
          <div className="space-y-4">
            <div className="h-8 w-3/4 animate-pulse rounded bg-secondary" />
            <div className="h-6 w-1/2 animate-pulse rounded bg-secondary" />
            <div className="h-24 animate-pulse rounded bg-secondary" />
          </div>
        </div>
      </div>
    );
  }

  const discount = product.original_price
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
    : 0;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-8" data-testid="product-detail-page">
      <button onClick={() => navigate(-1)} className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-foreground" data-testid="back-button">
        <ArrowLeft className="h-4 w-4" /> Back
      </button>

      <div className="grid gap-10 lg:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative overflow-hidden rounded-3xl border border-border bg-secondary"
        >
          <img src={product.image} alt={product.name} className="aspect-square w-full object-cover" data-testid="product-image" />
          {discount > 0 && (
            <span className="absolute left-4 top-4 rounded-md bg-primary px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-white">
              Save {discount}%
            </span>
          )}
        </motion.div>

        <div className="flex flex-col">
          <Link to={`/shop?category=${product.category}`} className="text-xs font-bold uppercase tracking-widest text-primary">
            {product.seller}
          </Link>
          <h1 className="font-display mt-2 text-3xl font-bold leading-tight tracking-tight sm:text-4xl" data-testid="product-name">
            {product.name}
          </h1>

          <div className="mt-3 flex items-center gap-3">
            <div className="flex items-center gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} className={`h-4 w-4 ${i < Math.round(product.rating) ? "fill-amber-400 text-amber-400" : "text-gray-300"}`} />
              ))}
            </div>
            <span className="text-sm font-semibold">{product.rating}</span>
            <span className="text-sm text-muted-foreground">({product.reviews.toLocaleString()} reviews)</span>
          </div>

          <div className="mt-5 flex items-baseline gap-3">
            <span className="font-display text-4xl font-extrabold" data-testid="product-price">{currency(product.price)}</span>
            {product.original_price && (
              <span className="text-lg text-muted-foreground line-through">{currency(product.original_price)}</span>
            )}
          </div>

          <p className="mt-5 leading-relaxed text-muted-foreground">{product.description}</p>

          <p className="mt-4 text-sm font-medium text-emerald-600">
            {product.stock > 0 ? `In stock — ${product.stock} available` : "Out of stock"}
          </p>

          <div className="mt-6 flex flex-wrap items-center gap-4">
            <div className="flex items-center rounded-full border border-border">
              <button onClick={() => setQty((q) => Math.max(1, q - 1))} className="flex h-11 w-11 items-center justify-center rounded-full hover:bg-secondary" data-testid="qty-decrease">
                <Minus className="h-4 w-4" />
              </button>
              <span className="w-10 text-center font-semibold" data-testid="qty-value">{qty}</span>
              <button onClick={() => setQty((q) => q + 1)} className="flex h-11 w-11 items-center justify-center rounded-full hover:bg-secondary" data-testid="qty-increase">
                <Plus className="h-4 w-4" />
              </button>
            </div>
            <button
              onClick={() => addItem(product, qty)}
              data-testid="add-to-cart-detail"
              className="flex h-12 flex-1 items-center justify-center gap-2 rounded-full bg-primary px-8 font-bold text-white transition-all hover:bg-primary/90 active:scale-95 min-w-[200px]"
            >
              <ShoppingCart className="h-5 w-5" /> Add to Cart
            </button>
          </div>

          <div className="mt-8 grid grid-cols-3 gap-4 border-t border-border pt-6 text-center">
            {[
              { icon: Truck, label: "Free shipping over $75" },
              { icon: ShieldCheck, label: "Secure checkout" },
              { icon: RotateCcw, label: "30-day returns" },
            ].map((f) => (
              <div key={f.label} className="flex flex-col items-center gap-2">
                <f.icon className="h-5 w-5 text-primary" />
                <span className="text-xs text-muted-foreground">{f.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {related.length > 0 && (
        <section className="mt-20">
          <h2 className="font-display mb-6 text-2xl font-bold tracking-tight">You might also like</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-5">
            {related.map((p, i) => (
              <ProductCard key={p.id} product={p} index={i} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
