import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { ShoppingCart, Bell, User, Menu, X, Search, LogOut, LayoutDashboard, Package, Heart, Store as StoreIcon } from "lucide-react";
// Fix: Use standard relative paths instead of @ alias paths
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import api from "../lib/api";
import { Btn } from "./common";

export function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const { count } = useCart();
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [userMenu, setUserMenu] = useState(false);

  useEffect(() => {
    if (!user) return setUnread(0);
    api.get("/notifications").then(({ data }) => setUnread(data.unread)).catch(() => {});
  }, [user]);

  const submitSearch = (e) => {
    e.preventDefault();
    navigate(`/store?search=${encodeURIComponent(q)}`);
    setMenuOpen(false);
  };

  const navLinks = [
    { to: "/store", label: "Store" },
    { to: "/marketplace", label: "Resale" },
    { to: "/sell", label: "Sell an Item" },
    { to: "/community", label: "Community" },
  ];

  // Clean string definition for the infinite ticker line
  const tickerText = "⚡ NEW DROPS WEEKLY • RESALE LISTINGS GO LIVE INSTANTLY • 10% OFF WITH CODE FURY10 • FREE VIBES ONLY • ";

  return (
    <>
      {/* Fix: Structural wrapper fix ensuring infinite marquee loops correctly */}
      <div className="bg-black text-white overflow-hidden py-2 border-b-2 border-black selection:bg-white selection:text-black">
        <div className="marquee font-mono text-xs uppercase tracking-[0.25em] flex select-none">
          <span className="shrink-0 pr-4">{tickerText.repeat(2)}</span>
          <span className="shrink-0 pr-4">{tickerText.repeat(2)}</span>
        </div>
      </div>
      <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-xl border-b-2 border-black" data-testid="navbar">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 gap-4">
            <Link to="/" className="shrink-0" data-testid="logo-link">
              <span className="font-head font-black text-xl sm:text-2xl tracking-tighter uppercase leading-none">
                LCs<span className=\"text-[#FF3B30]\"> Fury</span>Zone
              </span>
            </Link>

            <form onSubmit={submitSearch} className="hidden md:flex flex-1 max-w-md items-center border-2 border-black">
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search the zone..."
                className="flex-1 px-4 py-2 outline-none text-sm"
                data-testid="nav-search-input"
              />
              <button type="submit" className="bg-black text-white px-4 py-2.5" data-testid="nav-search-btn">
                <Search size={16} />
              </button>
            </form>

            <div className="hidden lg:flex items-center gap-1">
              {navLinks.map((l) => (
                <Link key={l.to} to={l.to} className="px-3 py-2 font-bold uppercase text-sm tracking-wide hover:text-[#FF3B30]" data-testid={`nav-${l.label.split(" ")[0].toLowerCase()}`}>
                  {l.label}
                </Link>
              ))}
            </div>

            <div className="flex items-center gap-2">
              {user && (
                <Link to="/notifications" className="relative p-2 hover:text-[#FF3B30]" data-testid="nav-notifications">
                  <Bell size={20} />
                  {unread > 0 && <span className="absolute -top-0.5 -right-0.5 bg-[#FF3B30] text-white text-[10px] font-bold w-4 h-4 flex items-center justify-center rounded-full">{unread}</span>}
                </Link>
              )}
              <Link to="/cart" className="relative p-2 hover:text-[#FF3B30]" data-testid="nav-cart">
                <ShoppingCart size={20} />
                {count > 0 && <span className="absolute -top-0.5 -right-0.5 bg-[#FF3B30] text-white text-[10px] font-bold w-4 h-4 flex items-center justify-center rounded-full" data-testid="cart-count">{count}</span>}
              </Link>

              {user ? (
                <div className="relative hidden sm:block">
                  <button onClick={() => setUserMenu((v) => !v)} className="p-2 border-2 border-black" data-testid="user-menu-btn">
                    <User size={18} />
                  </button>
                  {userMenu && (
                    <div className="absolute right-0 mt-2 w-56 bg-white border-2 border-black brutal-shadow z-50\" onMouseLeave={() => setUserMenu(false)}>
                      <div className="px-4 py-3 border-b-2 border-black">
                        <p className="font-bold truncate">{user.full_name}</p>
                        <p className="text-xs text-zinc-500 truncate">{user.email}</p>
                      </div>
                      <MenuItem to="/orders" icon={Package} label="My Orders" close={() => setUserMenu(false)} />
                      <MenuItem to="/seller" icon={LayoutDashboard} label="Seller Dashboard" close={() => setUserMenu(false)} />
                      <MenuItem to="/profile" icon={Heart} label="Profile & Wishlist" close={() => setUserMenu(false)} />
                      {isAdmin && <MenuItem to="/admin" icon={StoreIcon} label="Admin Panel" close={() => setUserMenu(false)} />}
                      <button onClick={() => { logout(); setUserMenu(false); navigate("/"); }} className="w-full text-left flex items-center gap-2 px-4 py-3 hover:bg-[#FF3B30] hover:text-white font-bold uppercase text-sm border-t-2 border-black" data-testid="logout-btn">
                        <LogOut size={16} /> Logout
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <Link to="/login" className="hidden sm:block">
                  <Btn variant="dark" className="!px-4 !py-2 text-sm" data-testid="nav-login">Login</Btn>
                </Link>
              )}

              <button className="lg:hidden p-2" onClick={() => setMenuOpen((v) => !v)} data-testid="mobile-menu-btn">
                {menuOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            </div>
          </div>
        </div>

        {menuOpen && (
          <div className="lg:hidden border-t-2 border-black bg-white px-4 py-4 space-y-2">
            <form onSubmit={submitSearch} className="flex items-center border-2 border-black mb-3">
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search..." className="flex-1 px-3 py-2 outline-none text-sm" />
              <button type="submit" className="bg-black text-white px-3 py-2.5"><Search size={16} /></button>
            </form>
            {navLinks.map((l) => (
              <Link key={l.to} to={l.to} onClick={() => setMenuOpen(false)} className="block font-bold uppercase py-2">{l.label}</Link>
            ))}
            {user ? (
              <>
                <Link to="/orders" onClick={() => setMenuOpen(false)} className="block font-bold uppercase py-2">My Orders</Link>
                <Link to="/seller" onClick={() => setMenuOpen(false)} className="block font-bold uppercase py-2">Seller Dashboard</Link>
                <Link to="/profile" onClick={() => setMenuOpen(false)} className="block font-bold uppercase py-2">Profile</Link>
                {isAdmin && <Link to="/admin" onClick={() => setMenuOpen(false)} className="block font-bold uppercase py-2">Admin</Link>}
                <button onClick={() => { logout(); setMenuOpen(false); navigate("/"); }} className="block font-bold uppercase py-2 text-[#FF3B30]">Logout</button>
              </>
            ) : (
              <Link to="/login" onClick={() => setMenuOpen(false)} className="block font-bold uppercase py-2 text-[#FF3B30]">Login</Link>
            )}
          </div>
        )}
      </nav>
    </>
  );
}

function MenuItem({ to, icon: Icon, label, close }) {
  return (
    <Link to={to} onClick={close} className="flex items-center gap-2 px-4 py-3 hover:bg-zinc-100 font-bold uppercase text-sm">
      <Icon size={16} /> {label}
    </Link>
  );
}
