import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Flame, Instagram, Twitter, Facebook } from "lucide-react";
import { toast } from "sonner";
import { api } from "../lib/api";

export const Footer = () => {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const subscribe = async (e) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    try {
      await api.post("/newsletter", { email });
      toast.success("You're on the list! Welcome to the Zone.");
      setEmail("");
    } catch {
      toast.error("Please enter a valid email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <footer className="mt-20 border-t border-border bg-foreground text-white" data-testid="site-footer">
      <div className="mx-auto max-w-7xl px-4 py-16 md:px-8">
        <div className="grid gap-10 md:grid-cols-4">
          <div className="md:col-span-1">
            <div className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-white">
                <Flame className="h-5 w-5" />
              </span>
              <span className="font-display text-lg font-extrabold">LC's Fury Zone</span>
            </div>
            <p className="mt-4 text-sm text-white/60">
              The marketplace for everything you love — from top brands to independent makers.
            </p>
            <div className="mt-5 flex gap-3">
              {[Instagram, Twitter, Facebook].map((Icon, i) => (
                <a key={i} href="#" className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 transition-colors hover:bg-primary">
                  <Icon className="h-4 w-4" />
                </a>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-display text-sm font-bold uppercase tracking-wider">Shop</h4>
            <ul className="mt-4 space-y-2 text-sm text-white/60">
              <li><Link to="/shop?category=electronics" className="hover:text-white">Electronics</Link></li>
              <li><Link to="/shop?category=fashion" className="hover:text-white">Fashion</Link></li>
              <li><Link to="/shop?category=home" className="hover:text-white">Home & Living</Link></li>
              <li><Link to="/shop?category=handmade" className="hover:text-white">Handmade</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="font-display text-sm font-bold uppercase tracking-wider">Support</h4>
            <ul className="mt-4 space-y-2 text-sm text-white/60">
              <li><a href="#" className="hover:text-white">Help Center</a></li>
              <li><a href="#" className="hover:text-white">Track Order</a></li>
              <li><a href="#" className="hover:text-white">Returns</a></li>
              <li><a href="#" className="hover:text-white">Contact Us</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-display text-sm font-bold uppercase tracking-wider">Stay in the loop</h4>
            <p className="mt-4 text-sm text-white/60">Get drops, deals and new arrivals in your inbox.</p>
            <form onSubmit={subscribe} className="mt-4 flex gap-2" data-testid="newsletter-form">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Your email"
                data-testid="newsletter-input"
                className="h-11 flex-1 rounded-full border border-white/20 bg-white/5 px-4 text-sm text-white placeholder:text-white/40 outline-none focus:border-primary"
              />
              <button
                type="submit"
                disabled={loading}
                data-testid="newsletter-submit"
                className="rounded-full bg-primary px-5 text-sm font-bold transition-all hover:bg-primary/90 active:scale-95 disabled:opacity-60"
              >
                Join
              </button>
            </form>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-3 border-t border-white/10 pt-6 text-xs text-white/40 md:flex-row">
          <p>© {new Date().getFullYear()} LC's The Fury Zone. All rights reserved.</p>
          <div className="flex gap-5">
            <a href="#" className="hover:text-white">Privacy</a>
            <a href="#" className="hover:text-white">Terms</a>
            <a href="#" className="hover:text-white">Cookies</a>
          </div>
        </div>
      </div>
    </footer>
  );
};
