import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Star, Plus } from "lucide-react";
import { currency } from "../lib/api";
import { useCart } from "../context/CartContext";

export const ProductCard = ({ product, index = 0 }) => {
  const { addItem } = useCart();
  
  // Support both ID naming conventions (MongoDB uses item_id or id)
  const productId = product.id || product.item_id;
  
  // Support both image property names
  const productImage = product.image || product.image_url;

  // Support both sold count property names
  const soldText = product.soldCount || product.sold_count || "50+ sold";

  // Calculate raw savings amount for the "Save $X" badge
  const savings = product.original_price ? (product.original_price - product.price).toFixed(2) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.3, delay: (index % 5) * 0.05 }}
      className="group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white transition-all hover:shadow-lg"
      data-testid={`product-card-${productId}`}
    >
      <Link to={`/product/${productId}`} className="relative block aspect-square overflow-hidden bg-gray-100">
        <img
          src={productImage}
          alt={product.name}
          loading="lazy"
          className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        {/* Save Badge */}
        {savings > 0 && (
          <div className="absolute left-2 top-2 rounded bg-orange-500 px-1.5 py-0.5 text-[10px] font-bold text-white shadow">
            Save ${savings}
          </div>
        )}
      </Link>

      <div className="flex flex-1 flex-col p-2.5">
        <Link to={`/product/${productId}`}>
          <h3 className="line-clamp-2 text-xs font-medium text-gray-800 group-hover:text-orange-600">
            {product.name}
          </h3>
        </Link>

        {/* Rating & Sold Count */}
        <div className="mt-1.5 flex items-center gap-1 text-[10px] text-gray-500">
          <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
          <span className="font-bold text-gray-900">{product.rating || "4.8"}</span>
          <span className="ml-1">{soldText}</span>
        </div>

        {/* Price & Add to Cart */}
        <div className="mt-3 flex items-center justify-between">
          <div>
            <span className="text-sm font-bold text-red-600">{currency(product.price)}</span>
            {product.original_price && (
              <span className="ml-1.5 text-[10px] text-gray-400 line-through">
                {currency(product.original_price)}
              </span>
            )}
          </div>
          <button
            onClick={() => addItem(product)}
            aria-label="Add to cart"
            className="rounded-full bg-orange-500 p-2 text-white transition-transform hover:scale-105 active:scale-95 shadow-sm"
          >
            <Plus className="h-4 w-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};