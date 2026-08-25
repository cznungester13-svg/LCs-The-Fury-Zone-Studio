import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Zap, Recycle, Tag } from "lucide-react";
import api from "../lib/api";
import Marquee from "../components/Marquee";
import ProductCard from "../components/ProductCard";

export default function Home() {
  const [departments, setDepartments] = useState([]);
  const [deals, setDeals] = useState([]);

  useEffect(() => {
    api.get("/departments").then((r) => setDepartments(r.data)).catch(() => {});
    api.get("/products/deals").then((r) => setDeals(r.data)).catch(() => {});
  }, []);

  const hero = departments[0];

  return (
    <div data-testid="home-page">
      {/* HERO BENTO */}
      <section className="mx-auto max-w-7xl px-4 pt-6 md:px-6">
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="relative flex flex-col justify-between overflow-hidden border-2 border-ink bg-orange p-8 text-white lg:col-span-2 lg:row-span-2" style={{ boxShadow: "6px 6px 0 #0A0A0A" }}>
            <div>
              <span className="tag bg-highlighter text-ink">RESALE MARKETPLACE</span>
              <h1 className="mt-4 font-display text-5xl uppercase leading-[0.9] tracking-tight md:text-7xl">
                One person's<br />junk. Your<br /><span className="text-highlighter">next flex.</span>
              </h1>
              <p className="mt-4 max-w-md font-body text-lg text-white/90">
                Six departments. 300+ pre-loved finds. Prices starting at <span className="font-bold">$0.99</span>. Hunt the bins, skip the retail markup.
              </p>
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/shop" className="brutal-btn brutal-btn-yellow" data-testid="hero-shop-btn">
                Start Digging <ArrowRight strokeWidth={2.5} size={18} />
              </Link>
              <Link to="/shop?sort=price_asc" className="brutal-btn bg-white text-ink" data-testid="hero-cheap-btn">
                Cheapest First
              </Link>
            </div>
          </div>

          <div className="flex flex-col justify-between border-2 border-ink bg-electric p-6 text-white" style={{ boxShadow: "4px 4px 0 #0A0A0A" }}>
            <Zap size={32} strokeWidth={2.5} className="text-highlighter" />
            <div>
              <div className="font-display text-4xl leading-none">300+</div>
              <div className="font-mono text-sm uppercase">items in stock</div>
            </div>
          </div>

          <div className="flex flex-col justify-between border-2 border-ink bg-highlighter p-6 text-ink" style={{ boxShadow: "4px 4px 0 #0A0A0A" }}>
            <Recycle size={32} strokeWidth={2.5} />
            <div>
              <div className="font-display text-4xl leading-none">50/dept</div>
              <div className="font-mono text-sm uppercase">packed shelves</div>
            </div>
          </div>
        </div>
      </section>

      <div className="mt-8">
        <Marquee />
      </div>

      {/* DEPARTMENTS */}
      <section className="mx-auto max-w-7xl px-4 py-12 md:px-6">
        <div className="mb-6 flex items-end justify-between">
          <h2 className="font-display text-4xl uppercase tracking-tight md:text-5xl">Departments</h2>
          <Link to="/shop" className="font-heading text-sm font-bold uppercase underline decoration-2 underline-offset-4 hover:text-orange">
            View all
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          {departments.map((d, i) => (
            <Link
              key={d.slug}
              to={`/department/${d.slug}`}
              className="brutal-card group relative overflow-hidden"
              data-testid={`dept-card-${d.slug}`}
            >
              <div className="relative aspect-[4/3] overflow-hidden border-b-2 border-ink">
                <img src={d.image} alt={d.name} className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" />
                <div className="absolute inset-0 bg-ink/30" />
                <span className="absolute left-0 top-0 border-b-2 border-r-2 border-ink bg-white px-2 py-1 font-mono text-xs font-bold">
                  {d.count} ITEMS
                </span>
              </div>
              <div className="flex items-center justify-between p-4">
                <div>
                  <h3 className="font-display text-xl uppercase leading-none tracking-tight">{d.name}</h3>
                  <p className="mt-1 font-mono text-xs text-ash">{d.tagline}</p>
                </div>
                <ArrowRight strokeWidth={2.5} className="shrink-0 transition-transform group-hover:translate-x-1" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* DEALS */}
      <section className="border-y-2 border-ink bg-white py-12">
        <div className="mx-auto max-w-7xl px-4 md:px-6">
          <div className="mb-6 flex items-center gap-3">
            <Tag size={28} strokeWidth={2.5} className="text-sale" />
            <h2 className="font-display text-4xl uppercase tracking-tight md:text-5xl">Rock Bottom Deals</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {deals.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
