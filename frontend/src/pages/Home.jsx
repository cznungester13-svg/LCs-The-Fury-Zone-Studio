import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Search, ArrowRight, Truck, ShieldCheck, RotateCcw, Store } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { ProductCard } from "../components/ProductCard";

const HERO_IMAGES = [
  "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
  "https://images.unsplash.com/photo-1608231387042-66d1773070a5?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
  "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
  "https://images.unsplash.com/photo-1649810617979-16001a60c89c?crop=entropy&cs=srgb&fm=jpg&q=85&w=600",
];

const TRUST = [
  { icon: Truck, title: "Free shipping", sub: "On orders over $75" },
  { icon: ShieldCheck, title: "Secure payment", sub: "256-bit encryption" },
  { icon: RotateCcw, title: "Easy returns", sub: "30-day guarantee" },
  { icon: Store, title: "10,000+ sellers", sub: "Brands & makers" },
];

export default function Home() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [q, setQ] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/products").then((r) => setProducts(r.data));
    api.get("/categories").then((r) => setCategories(r.data));
  }, []);

  const submit = (e) => {
    e.preventDefault();
    navigate(`/shop?search=${encodeURIComponent(q)}`);
  };

  const trending = products.slice(0, 5);
  const deals = products.filter((p) => p.original_price).slice(0, 5);

  return (
    <div data-testid="home-page">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border bg-secondary/40">
        <div className="mx-auto grid max-w-7xl items-center gap-10 px-4 py-16 md:grid-cols-2 md:px-8 md:py-24">
          <div>
            <motion.span
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-widest text-primary"
            >
              Summer Drop — Up to 40% off
            </motion.span>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="font-display mt-5 text-4xl font-extrabold leading-[1.05] tracking-tight text-foreground sm:text-5xl lg:text-6xl"
            >
              Everything you love,<br />
              <span className="text-primary">all in one Zone.</span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="mt-5 max-w-md text-base text-muted-foreground"
            >
              Shop millions of products from top brands and independent makers — electronics, fashion, handmade goods and more.
            </motion.p>

            <motion.form
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              onSubmit={submit}
              className="mt-8"
              data-testid="hero-search-form"
            >
              <div className="relative max-w-md">
                <Search className="pointer-events-none absolute left-5 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
                <input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="What are you looking for?"
                  data-testid="hero-search-input"
                  className="h-14 w-full rounded-full border-2 border-foreground bg-white pl-12 pr-32 text-base outline-none focus:ring-4 focus:ring-primary/15"
                />
                <button
                  type="submit"
                  className="absolute right-1.5 top-1.5 flex h-11 items-center gap-1 rounded-full bg-primary px-5 text-sm font-bold text-white transition-all hover:bg-primary/90 active:scale-95"
                >
                  Search
                </button>
              </div>
            </motion.form>

            <div className="mt-6 flex flex-wrap gap-2 text-sm">
              <span className="text-muted-foreground">Popular:</span>
              {["Headphones", "Sneakers", "Candles", "Serum"].map((t) => (
                <Link key={t} to={`/shop?search=${t}`} className="font-medium text-foreground underline-offset-4 hover:text-primary hover:underline">
                  {t}
                </Link>
              ))}
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="grid grid-cols-2 gap-4"
          >
            {HERO_IMAGES.map((src, i) => (
              <div
                key={i}
                className={`overflow-hidden rounded-2xl border border-border bg-white ${i % 2 ? "mt-8" : ""}`}
              >
                <img src={src} alt="Featured product" className="aspect-square w-full object-cover transition-transform duration-500 hover:scale-105" />
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Trust bar */}
      <section className="border-b border-border bg-white">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-6 px-4 py-6 md:grid-cols-4 md:px-8">
          {TRUST.map((t) => (
            <div key={t.title} className="flex items-center gap-3">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-secondary text-foreground">
                <t.icon className="h-5 w-5" />
              </span>
              <div>
                <p className="text-sm font-bold">{t.title}</p>
                <p className="text-xs text-muted-foreground">{t.sub}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Categories */}
      <section className="mx-auto max-w-7xl px-4 py-16 md:px-8">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground">Browse</p>
            <h2 className="font-display mt-1 text-3xl font-bold tracking-tight sm:text-4xl">Shop by category</h2>
          </div>
          <Link to="/shop" className="hidden items-center gap-1 text-sm font-semibold text-primary hover:gap-2 md:flex transition-all">
            View all <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          {categories.map((c, i) => (
            <Link
              key={c.id}
              to={`/shop?category=${c.id}`}
              data-testid={`category-${c.id}`}
              className="group relative aspect-[4/5] overflow-hidden rounded-2xl border border-border"
            >
              <img src={c.image} alt={c.name} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />
              <div className="absolute inset-x-0 bottom-0 p-4">
                <h3 className="font-display text-lg font-bold text-white">{c.name}</h3>
                <p className="text-xs text-white/70">{c.count} items</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Promo banner */}
      <section className="mx-auto max-w-7xl px-4 md:px-8">
        <div className="relative overflow-hidden rounded-3xl bg-foreground px-8 py-14 text-white md:px-16">
          <div className="relative z-10 max-w-lg">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary">Limited time</p>
            <h2 className="font-display mt-3 text-3xl font-extrabold sm:text-4xl">Mega Deals Week is live 🔥</h2>
            <p className="mt-3 text-white/70">Save big across every category. New markdowns dropping daily — grab them before they're gone.</p>
            <Link
              to="/shop?sort=price_asc"
              className="mt-6 inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3 text-sm font-bold transition-all hover:bg-primary/90 active:scale-95"
            >
              Shop the deals <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
          <div className="pointer-events-none absolute -right-10 top-1/2 hidden h-72 w-72 -translate-y-1/2 rounded-full bg-primary/30 blur-3xl md:block" />
        </div>
      </section>

      {/* Trending */}
      <section className="mx-auto max-w-7xl px-4 py-16 md:px-8">
        <div className="mb-8 flex items-end justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-muted-foreground">Hot right now</p>
            <h2 className="font-display mt-1 text-3xl font-bold tracking-tight sm:text-4xl">Trending products</h2>
          </div>
          <Link to="/shop" className="hidden items-center gap-1 text-sm font-semibold text-primary hover:gap-2 md:flex transition-all">
            View all <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-5">
          {trending.map((p, i) => (
            <ProductCard key={p.id} product={p} index={i} />
          ))}
        </div>
      </section>

      {/* Deals */}
      {deals.length > 0 && (
        <section className="mx-auto max-w-7xl px-4 pb-4 md:px-8">
          <div className="mb-8">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-primary">Save now</p>
            <h2 className="font-display mt-1 text-3xl font-bold tracking-tight sm:text-4xl">Today's best deals</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-5">
            {deals.map((p, i) => (
              <ProductCard key={p.id} product={p} index={i} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
