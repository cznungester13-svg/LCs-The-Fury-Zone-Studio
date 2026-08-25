import React from "react";
import { Link } from "react-router-dom";
import { Plus, Star } from "lucide-react";
import { useCart } from "../context/CartContext";

const CONDITION_COLORS = {
  "Like New": "bg-highlighter",
  "Gently Used": "bg-electric text-white",
  "Well Loved": "bg-orange text-white",
  Vintage: "bg-sale text-white",
  Refurbished: "bg-white",
};

export default function ProductCard({ product }) {
  const { addItem } = useCart();
  const discount = Math.round((1 - product.price / product.original_price) * 100);

  return (
    <div className="brutal-card group flex flex-col overflow-hidden" data-testid={`product-card-${product.id}`}>
      <Link to={`/product/${product.id}`} className="relative block">
        <div className="relative aspect-square overflow-hidden border-b-2 border-ink bg-paper">
          <img
            src={product.image}
            alt={product.name}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <span className="absolute left-0 top-0 border-b-2 border-r-2 border-ink bg-sale px-2 py-1 font-display text-lg leading-none text-white">
            ${product.price.toFixed(2)}
          </span>
          {discount > 0 && (
            <span className="absolute right-2 top-2 border-2 border-ink bg-highlighter px-1.5 py-0.5 font-mono text-xs font-bold text-ink">
              -{discount}%
            </span>
          )}
        </div>
      </Link>

      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-center justify-between">
          <span className={`tag ${CONDITION_COLORS[product.condition] || "bg-white"}`}>{product.condition}</span>
          <span className="flex items-center gap-1 font-mono text-xs text-ash">
            <Star size={12} className="fill-orange text-orange" strokeWidth={2.5} /> {product.rating}
          </span>
        </div>
        <Link to={`/product/${product.id}`}>
          <h3 className="font-heading text-sm font-bold leading-tight text-ink line-clamp-2 hover:text-orange">
            {product.name}
          </h3>
        </Link>
        <span className="font-mono text-[10px] uppercase text-ash">{product.category}</span>

        <div className="mt-auto flex items-end justify-between gap-2 pt-2">
          <div>
            <span className="font-display text-2xl leading-none text-ink">${product.price.toFixed(2)}</span>
            <span className="ml-1 font-mono text-xs text-ash line-through">${product.original_price.toFixed(2)}</span>
          </div>
          <button
            onClick={() => addItem(product)}
            className="brutal-btn brutal-btn-primary p-2"
            data-testid={`add-to-cart-${product.id}`}
            aria-label="Add to cart"
          >
            <Plus size={18} strokeWidth={3} />
          </button>
        </div>
      </div>
    </div>
  );
}
