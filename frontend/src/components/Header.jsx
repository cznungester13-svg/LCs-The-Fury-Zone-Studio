import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search, ShoppingCart, Menu, X, Flame } from "lucide-react";
import { useCart } from "../context/CartContext";

const CATS = [
  { id: "all", name: "All" },
  { id: "electronics", name: "Electronics" },
  { id: "fashion", name: "Fashion" },
  { id: "home", name: "Home & Living" },
  { id: "handmade", name: "Handmade" },
  { id: "beauty", name: "Beauty" },
];

export const Header = () => {
  const { count } = useCart();
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);

  const submit = (e) => {
    e.preventDefault();
    navigate(`/shop?search=${encodeURIComponent(q)}`);
    setOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-white/90 backdrop-blur-xl" data-testid="site-header">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 md:px-8">
        <Link to="/" className="flex shrink-0 items-center gap-2" data-testid="logo-link">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white">
            <Flame className="h-5 w-5" />
          </span>
          <span className="font-display text-lg font-extrabold leading-none tracking-tight">
            LC's <span className="text-primary">Fury Zone</span>
          </span>
        </Link>

        <form onSubmit={submit} className="hidden flex-1 md:block" data-testid="search-form">
          <div className="relative">
            <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search for anything…"
              data-testid="search-input"
              className="h-11 w-full rounded-full border border-input bg-secondary/60 pl-11 pr-4 text-sm outline-none transition-all focus:border-foreground focus:bg-white focus:ring-4 focus:ring-primary/10"
            />
          </div>
        </form>

        <div className="ml-auto flex items-center gap-1 md:ml-0">
          <Link
            to="/cart"
            data-testid="cart-link"
            className="relative flex h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-secondary"
          >
            <ShoppingCart className="h-5 w-5" />
            {count > 0 && (
              <span
                data-testid="cart-count"
                className="absolute -right-0.5 -top-0.5 flex h-5 min-w-[20px] items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-white"
              >
                {count}
              </span>
            )}
          </Link>
          <button
            className="flex h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-secondary md:hidden"
            onClick={() => setOpen((o) => !o)}
            data-testid="mobile-menu-toggle"
            aria-label="Menu"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      <nav className="hidden border-t border-border md:block">
        <div className="mx-auto flex max-w-7xl items-center gap-6 px-8 py-2.5 text-sm font-medium">
          {CATS.map((c) => (
            <Link
              key={c.id}
              to={c.id === "all" ? "/shop" : `/shop?category=${c.id}`}
              data-testid={`nav-cat-${c.id}`}
              className="text-muted-foreground transition-colors hover:text-primary"
            >
              {c.name}
            </Link>
          ))}
        </div>
      </nav>

      {open && (
        <div className="border-t border-border px-4 py-4 md:hidden" data-testid="mobile-menu">
          <form onSubmit={submit} className="mb-3">
            <div className="relative">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search…"
                className="h-11 w-full rounded-full border border-input bg-secondary/60 pl-11 pr-4 text-sm outline-none"
              />
            </div>
          </form>
          <div className="grid grid-cols-2 gap-2">
            {CATS.map((c) => (
              <Link
                key={c.id}
                to={c.id === "all" ? "/shop" : `/shop?category=${c.id}`}
                onClick={() => setOpen(false)}
                className="rounded-lg bg-secondary px-3 py-2 text-sm font-medium"
              >
                {c.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </header>
  );
};
