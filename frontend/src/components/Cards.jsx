import React from "react";
import { Link } from "react-router-dom";
import { Star } from "lucide-react";
import { currency, imgUrl } from "../lib/api";

function pickImage(obj) {
  const raw = obj.image || obj.image_url || (Array.isArray(obj.images) ? obj.images[0] : "");
  return raw ? imgUrl(raw) : "/placeholder-product.jpg";
}

export function ProductCard({ product = {} }) {
  const id = product.id || product.item_id;
  const name = product.name || product.title || "Product";
  const img = pickImage(product);

  return (
    <Link
      to={`/product/${id}`}
      data-testid={`product-card-${id}`}
      className="group border-2 border-black bg-white brutal-shadow overflow-hidden flex flex-col transition-transform hover:-translate-y-0.5"
    >
      <div className="relative aspect-square overflow-hidden bg-zinc-100">
        <img
          src={img}
          alt={name}
          loading="lazy"
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {product.featured && (
          <span className="absolute left-2 top-2 bg-[#FF3B30] text-white text-[10px] font-black uppercase px-2 py-0.5 border border-black">
            Featured
          </span>
        )}
      </div>
      <div className="p-3 flex flex-col flex-1 border-t-2 border-black">
        <h3 className="font-bold uppercase text-sm leading-tight line-clamp-2 group-hover:text-[#FF3B30]">
          {name}
        </h3>
        <div className="mt-1 flex items-center gap-1 text-[11px] text-zinc-500">
          <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
          <span className="font-bold text-zinc-900">{product.rating || "5.0"}</span>
          {product.review_count ? <span>({product.review_count})</span> : null}
        </div>
        <div className="mt-auto pt-2 flex items-center justify-between">
          <span className="font-black text-lg">{currency(product.price)}</span>
          {product.original_price && (
            <span className="text-xs text-zinc-400 line-through">{currency(product.original_price)}</span>
          )}
        </div>
      </div>
    </Link>
  );
}

const CONDITION_LABEL = {
  new: "New",
  like_new: "Like New",
  good: "Good",
  fair: "Fair",
};

export function ListingCard({ listing = {} }) {
  const id = listing.id || listing.item_id;
  const name = listing.name || listing.title || "Listing";
  const img = pickImage(listing);

  return (
    <Link
      to={`/listing/${id}`}
      data-testid={`listing-card-${id}`}
      className="group border-2 border-black bg-white brutal-shadow overflow-hidden flex flex-col transition-transform hover:-translate-y-0.5"
    >
      <div className="relative aspect-square overflow-hidden bg-zinc-100">
        <img
          src={img}
          alt={name}
          loading="lazy"
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        {listing.condition && (
          <span className="absolute left-2 top-2 bg-black text-white text-[10px] font-black uppercase px-2 py-0.5">
            {CONDITION_LABEL[listing.condition] || listing.condition}
          </span>
        )}
      </div>
      <div className="p-3 flex flex-col flex-1 border-t-2 border-black">
        <h3 className="font-bold uppercase text-sm leading-tight line-clamp-2 group-hover:text-[#FF3B30]">
          {name}
        </h3>
        {listing.seller_name && (
          <p className="mt-1 font-mono text-[11px] text-zinc-500 truncate">by {listing.seller_name}</p>
        )}
        <div className="mt-auto pt-2">
          <span className="font-black text-lg">{currency(listing.price)}</span>
        </div>
      </div>
    </Link>
  );
}

export default ProductCard;
