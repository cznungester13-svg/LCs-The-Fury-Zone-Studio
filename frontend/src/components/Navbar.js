import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ShoppingBag, User, Search, Menu, X, LogOut, Package } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

const DEPTS = [
  { slug: "fashion", name: "Fashion" },
  { slug: "electronics", name: "Electronics" },
  { slug: "home", name: "Home" },
  { slug: "books", name: "Books" },
  { slug: "sports", name: "Sports" },
  { slug: "toys", name: "Toys" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const { count } = useCart();
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);

  const submitSearch = (e) => {
    e.preventDefault();
    if (q.trim()) navigate(`/shop?search=${encodeURIComponent(q.trim())}`);
  };

  return (
    <header className="sticky top-0 z-50 border-b-2 border-ink bg-paper" data-testid="navbar">
      <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3 md:px-6">
        <Link to="/" className="flex items-center gap-2 shrink-0" data-testid="logo-link">
          <span className="bg-ink px-2 py-1 font-display text-2xl leading-none text-highlighter">LC</span>
          <span className="hidden font-display text-2xl leading-none tracking-tight sm:block">
            FURY<span className="text-orange">ZONE</span>
          </span>
        </Link>

        <form onSubmit={submitSearch} className="relative hidden flex-1 md:block">
          <input
            data-testid="search-input"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Hunt for treasure..."
            className="brutal-input pr-12 font-body"
          />
          <button type="submit" data-testid="search-submit" className="absolute right-0 top-0 h-full border-l-2 border-ink bg-highlighter px-3">
            <Search strokeWidth={2.5} size={20} />
          </button>
        </form>

        <div className="ml-auto flex items-center gap-2">
          {user ? (
            <div className="hidden items-center gap-2 md:flex">
              <Link to="/orders" className="brutal-btn px-3 py-2 text-xs" data-testid="orders-link">
                <Package size={18} strokeWidth={2.5} /> Orders
              </Link>
              <button onClick={logout} className="brutal-btn px-3 py-2 text-xs" data-testid="logout-btn">
                <LogOut size={18} strokeWidth={2.5} /> Out
              </button>
            </div>
          ) : (
            <Link to="/login" className="hidden brutal-btn px-3 py-2 text-xs md:inline-flex" data-testid="login-link">
              <User size={18} strokeWidth={2.5} /> Sign In
            </Link>
          )}
          <Link to="/cart" className="relative brutal-btn brutal-btn-primary px-3 py-2" data-testid="cart-link">
            <ShoppingBag size={20} strokeWidth={2.5} />
            {count > 0 && (
              <span className="absolute -right-2 -top-2 flex h-6 min-w-6 items-center justify-center border-2 border-ink bg-highlighter px-1 font-mono text-xs font-bold text-ink" data-testid="cart-count">
                {count}
              </span>
            )}
          </Link>
          <button className="brutal-btn px-3 py-2 md:hidden" onClick={() => setOpen(!open)} data-testid="mobile-menu-btn">
            {open ? <X size={20} strokeWidth={2.5} /> : <Menu size={20} strokeWidth={2.5} />}
          </button>
        </div>
      </div>

      <nav className="hidden border-t-2 border-ink bg-white md:block">
        <div className="mx-auto flex max-w-7xl items-center gap-1 overflow-x-auto px-4 md:px-6">
          <Link to="/shop" className="whitespace-nowrap border-r-2 border-ink px-4 py-2 font-heading text-sm font-bold uppercase hover:bg-highlighter" data-testid="nav-all">
            All Depts
          </Link>
          {DEPTS.map((d) => (
            <Link key={d.slug} to={`/department/${d.slug}`} className="whitespace-nowrap px-4 py-2 font-heading text-sm font-bold uppercase hover:bg-highlighter" data-testid={`nav-${d.slug}`}>
              {d.name}
            </Link>
          ))}
        </div>
      </nav>

      {open && (
        <div className="border-t-2 border-ink bg-white md:hidden" data-testid="mobile-menu">
          <form onSubmit={submitSearch} className="border-b-2 border-ink p-3">
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search..." className="brutal-input" data-testid="mobile-search-input" />
          </form>
          {DEPTS.map((d) => (
            <Link key={d.slug} to={`/department/${d.slug}`} onClick={() => setOpen(false)} className="block border-b border-ink/20 px-4 py-3 font-heading font-bold uppercase">
              {d.name}
            </Link>
          ))}
          <Link to="/cart" onClick={() => setOpen(false)} className="block border-b border-ink/20 px-4 py-3 font-heading font-bold uppercase text-orange" data-testid="mobile-cart-link">My Cart</Link>
          {user ? (
            <>
              <Link to="/orders" onClick={() => setOpen(false)} className="block border-b border-ink/20 px-4 py-3 font-heading font-bold uppercase">Orders</Link>
              <button onClick={() => { logout(); setOpen(false); }} className="block w-full px-4 py-3 text-left font-heading font-bold uppercase text-sale">Sign Out</button>
            </>
          ) : (
            <Link to="/login" onClick={() => setOpen(false)} className="block px-4 py-3 font-heading font-bold uppercase">Sign In</Link>
          )}
        </div>
      )}
    </header>
  );
}
