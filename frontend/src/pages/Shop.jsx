import React from "react";

const CATS = ["All", "Apparel", "Collectibles", "Accessories", "Digital"];

export default function Shop({ products = [] }) {
  const safeProducts = Array.isArray(products) ? products : [];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Category Pills */}
      <div className="flex space-x-2 mb-8">
        {CATS.map((c) => (
          <button
            key={c}
            className="px-4 py-2 text-sm font-bold uppercase border-2 border-black hover:bg-black hover:text-white transition"
          >
            {c}
          </button>
        ))}
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {safeProducts.length > 0 ? (
          safeProducts.map((p, i) => (
            <div key={p.id || p._id || i} className="border-2 border-black p-4 relative">
              <div className="h-48 bg-zinc-100 flex items-center justify-center mb-4">
                {p.image ? (
                  <img src={p.image} alt={p.name} className="h-full w-full object-cover" />
                ) : (
                  <span className="text-zinc-400 text-xs font-mono">NO IMAGE</span>
                )}
              </div>
              <h2 className="font-black uppercase text-base truncate">{p.name || "Item"}</h2>
              <p className="font-mono text-sm text-zinc-700 font-bold mt-1">
                ${typeof p.price === "number" ? p.price.toFixed(2) : p.price || "0.00"}
              </p>
            </div>
          ))
        ) : (
          Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="border-2 border-dashed border-zinc-200 p-4 h-64 flex items-center justify-center text-zinc-400 text-xs font-mono">
              LOADING / NO DATA
            </div>
          ))
        )}
      </div>
    </div>
  );
}