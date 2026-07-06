import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Star, Plus } from "lucide-react";
import { currency } from "../lib/api";
import { useCart } from "../context/CartContext";

export const ProductCard = ({ product, index = 0 }) => {
  const { addItem } = useCart();
  const discount = product.original_price
    ? Math.round(((product.original_price - product.price) / product.original_price) * 100)
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.4, delay: (index % 5) * 0.06 }}
      className="group relative flex flex-col overflow-hidden rounded-2xl border border-border bg-white transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-black/5"
      data-testid={`product-card-${product.id}`}
    >
      <Link to={`/product/${product.id}`} className="relative block aspect-square overflow-hidden bg-secondary">
        <img
          src={product.image}
          alt={product.name}
          loading="lazy"
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute left-3 top-3 flex flex-col gap-1.5">
          {product.badge && (
            <span className="rounded-md bg-black px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-white">
              {product.badge}
            </span>
          )}
          {discount > 0 && (
            <span className="rounded-md bg-primary px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-white">
              -{discount}%
            </span>
          )}
        </div>
      </Link>

      <div className="flex flex-1 flex-col p-4">
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{product.seller}</p>
        <Link to={`/product/${product.id}`}>
          <h3 className="mt-1 line-clamp-2 text-sm font-semibold leading-snug text-foreground transition-colors group-hover:text-primary">
            {product.name}
          </h3>
        </Link>

        <div className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
          <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
          <span className="font-semibold text-foreground">{product.rating}</span>
          <span>({product.reviews.toLocaleString()})</span>
        </div>

        <div className="mt-auto flex items-end justify-between pt-3">
          <div className="flex items-baseline gap-2">
            <span className="font-display text-lg font-bold text-foreground">{currency(product.price)}</span>
            {product.original_price && (
              <span className="text-xs text-muted-foreground line-through">{currency(product.original_price)}</span>
            )}
          </div>
          <button
            onClick={() => addItem(product)}
            aria-label="Add to cart"
            data-testid={`add-to-cart-${product.id}`}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-foreground text-white transition-all hover:bg-primary active:scale-90"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};
