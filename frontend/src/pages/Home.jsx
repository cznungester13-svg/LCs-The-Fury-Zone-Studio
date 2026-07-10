import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Zap, Tag, ShieldCheck } from "lucide-react";
// Fix: Correct path alias mapping by shifting to relative directory structures
import api from "../lib/api";
import { ProductCard, ListingCard } from "../components/cards";
import { Btn, Spinner } from "../components/common";

const HERO = "https://images.pexels.com/photos/29548609/pexels-photo-29548609.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940";
const SELL_IMG = "https://images.pexels.com/photos/11317811/pexels-photo-11317811.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940";

export default function Home() {
  const [featured, setFeatured] = useState(null);
  const [listings, setListings] = useState(null);

  useEffect(() => {
    api.get("/products?featured=true&limit=4").then(({ data }) => setFeatured(data)).catch(() => setFeatured([]));
    api.get("/listings?limit=4").then(({ data }) => setListings(data)).catch(() => setListings([]));
  }, []);

  return (
    <div>
      {/* Hero */}
      <section className="border-b-2 border-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid md:grid-cols-2 gap-8 items-center py-12 md:py-20">
          <div>
            <span className="font-mono uppercase text-xs tracking-[0.3em] text-[#FF3B30]">Shop new · Sell used · Instant</span>
            <h1 className="font-head text-5xl sm:text-6xl lg:text-7xl font-black tracking-tighter uppercase leading-[0.9] mt-4">
              Enter the<br /><span className="text-[#FF3B30]">Fury</span> Zone
            </h1>
            <p className="text-lg text-zinc-600 mt-6 max-w-md">
              A marketplace with attitude. Cop fresh gear from the store, or flip your used pieces — listings go live instantly.
            </p>
            <div className="flex flex-wrap gap-4 mt-8">
              <Link to="/store"><Btn data-testid="hero-shop-btn">Shop the store <ArrowRight size={18} /></Btn></Link>
              <Link to="/sell"><Btn variant="secondary" data-testid="hero-sell-btn">Sell an item</Btn></Link>
            </div>
          </div>
          <div className="relative">
            <div className="border-2 border-black brutal-shadow overflow-hidden">
              <img src={HERO} alt="Fury Zone" className="w-full h-[420px] object-cover" />
            </div>
            <div className="absolute -bottom-4 -left-4 bg-[#FF3B30] text-white border-2 border-black px-5 py-3 font-black uppercase tracking-tight">
              Drop 001 live
            </div>
          </div>
        </div>
      </section>

{/* Department Grid Navigation Tiles */}
      {departments.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 my-16">
          <div className="border-b-2 border-black pb-3 mb-8">
            <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tighter">Shop by Department</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {departments.map((d) => (
              <Link 
                key={d.id} 
                to={`/store?department=${d.slug}`}
                className="group relative border-2 border-black brutal-shadow bg-white overflow-hidden aspect-[4/3] block"
              >
                {d.image ? (
                  <img 
                    src={d.image} 
                    alt={d.name} 
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" 
                  />
                ) : (
                  <div className="w-full h-full bg-zinc-100 flex items-center justify-center font-mono text-zinc-400 text-xs">
                    NO IMAGE AVAILABLE
                  </div>
                )}
                <div className="absolute inset-x-0 bottom-0 border-t-2 border-black bg-white p-3 transform transition-transform group-hover:bg-[#FF3B30] group-hover:text-white">
                  <p className="font-black uppercase text-sm sm:text-base tracking-tight truncate flex items-center justify-between">
                    {d.name}
                    <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Featured products */}
      <Section title="Featured Store Drops" link="/store" linkLabel="All products">
        {featured === null ? <Spinner /> : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {featured.map((p) => <ProductCard key={p.id} product={p} />)}
          </div>
        )}
      </Section>

      {/* Sell CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 my-16">
        <div className="grid md:grid-cols-2 border-2 border-black brutal-shadow overflow-hidden">
          <div className="p-10 flex flex-col justify-center bg-[#FF3B30] text-white">
            <h2 className="text-4xl font-black uppercase tracking-tighter">Got stuff to flip?</h2>
            <p className="mt-3 text-white/90 max-w-sm">Turn your closet into cash. Snap photos, set a price, and your listing hits the marketplace instantly.</p>
            <Link to="/sell" className="mt-6"><Btn variant="secondary" data-testid="cta-sell-btn">Start selling</Btn></Link>
          </div>
          <img src={SELL_IMG} alt="Sell" className="h-72 md:h-auto w-full object-cover" />
        </div>
      </section>

      {/* Resale listings */}
      <Section title="Fresh Resale Finds" link="/marketplace" linkLabel="All resale">
        {listings === null ? <Spinner /> : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {listings.map((l) => <ListingCard key={l.id} listing={l} />)}
          </div>
        )}
      </Section>
    </div>
  );
}

function Feature({ icon: Icon, title, text }) {
  return (
    <div className="py-8 px-6 flex gap-4">
      <Icon className="text-[#FF3B30] shrink-0" size={28} />
      <div>
        <h3 className="font-black uppercase tracking-tight">{title}</h3>
        <p className="text-zinc-400 text-sm mt-1">{text}</p>
      </div>
    </div>
  );
}

function Section({ title, link, linkLabel, children }) {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 my-16">
      <div className="flex items-end justify-between mb-8 border-b-2 border-black pb-3">
        <h2 className="text-3xl sm:text-4xl font-black uppercase tracking-tighter">{title}</h2>
        <Link to={link} className="font-bold uppercase text-sm hover:text-[#FF3B30] flex items-center gap-1">{linkLabel} <ArrowRight size={16} /></Link>
      </div>
      {children}
    </section>
  );
}
