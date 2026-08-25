import React from "react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="mt-16 border-t-2 border-ink bg-ink text-paper" data-testid="footer">
      <div className="mx-auto grid max-w-7xl gap-8 px-6 py-12 md:grid-cols-4">
        <div>
          <div className="mb-3 flex items-center gap-2">
            <span className="bg-highlighter px-2 py-1 font-display text-2xl leading-none text-ink">LC</span>
            <span className="font-display text-2xl leading-none tracking-tight">FURY<span className="text-orange">ZONE</span></span>
          </div>
          <p className="font-mono text-xs text-paper/70">
            Multi-department resale marketplace. Treasure hunting since always. Everything cheap, nothing boring.
          </p>
        </div>
        <div>
          <h4 className="mb-3 font-heading text-sm font-extrabold uppercase text-highlighter">Departments</h4>
          <ul className="space-y-1 font-body text-sm text-paper/80">
            <li><Link to="/department/fashion" className="hover:text-highlighter">Fashion & Apparel</Link></li>
            <li><Link to="/department/electronics" className="hover:text-highlighter">Electronics</Link></li>
            <li><Link to="/department/home" className="hover:text-highlighter">Home & Decor</Link></li>
            <li><Link to="/department/books" className="hover:text-highlighter">Books & Media</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="mb-3 font-heading text-sm font-extrabold uppercase text-highlighter">Shop</h4>
          <ul className="space-y-1 font-body text-sm text-paper/80">
            <li><Link to="/shop" className="hover:text-highlighter">All Products</Link></li>
            <li><Link to="/shop?sort=price_asc" className="hover:text-highlighter">Cheapest First</Link></li>
            <li><Link to="/cart" className="hover:text-highlighter">My Cart</Link></li>
            <li><Link to="/orders" className="hover:text-highlighter">My Orders</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="mb-3 font-heading text-sm font-extrabold uppercase text-highlighter">Deal Alert</h4>
          <p className="mb-3 font-mono text-xs text-paper/70">Prices this low won't last. Or will they? They will.</p>
          <div className="inline-block border-2 border-highlighter px-3 py-1 font-mono text-xs font-bold text-highlighter">
            FROM $0.99
          </div>
        </div>
      </div>
      <div className="border-t border-paper/20 py-4 text-center font-mono text-xs text-paper/50">
        © {new Date().getFullYear()} LC Fury Zone — Fix first, refactor second.
      </div>
    </footer>
  );
}
