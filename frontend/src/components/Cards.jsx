import { Link } from "react-router-dom";
// Fix: Use standard relative paths instead of @ alias paths
import { imgUrl } from "../lib/api";
import { Stars, Badge, CONDITION_LABEL } from "./common";

export function ProductCard({ product }) {
  return (
    <Link
      to={`/product/${product.id}`}
      className="group border-2 border-zinc-200 hover:border-black bg-white transition-all rounded-none overflow-hidden flex flex-col"
      data-testid={`product-card-${product.id}`}
    >
      <div className="aspect-square overflow-hidden bg-zinc-100 relative">
        <img src={imgUrl(product.images?.[0])} alt={product.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        {product.featured && <span className="absolute top-2 left-2"><Badge className="!bg-[#FF3B30] !text-white !border-[#FF3B30]">Featured</Badge></span>}
      </div>
      <div className="p-4 flex flex-col flex-1">
        {product.brand_name && <p className="text-xs font-mono uppercase tracking-widest text-zinc-500">{product.brand_name}</p>}
        <h3 className="font-bold leading-tight mt-1 line-clamp-2">{product.title}</h3>
        <div className="mt-2"><Stars value={product.rating} count={product.review_count} /></div>
        <div className="mt-auto pt-3 flex items-center justify-between">
          <span className="text-xl font-black">${product.price.toFixed(2)}</span>
          {product.stock <= 0 && <Badge className="!text-zinc-500">Sold out</Badge>}
        </div>
      </div>
    </Link>
  );
}

export function ListingCard({ listing }) {
  return (
    <Link
      to={`/listing/${listing.id}`}
      className="group border-2 border-zinc-200 hover:border-black bg-white transition-all rounded-none overflow-hidden flex flex-col"
      data-testid={`listing-card-${listing.id}`}
    >
      <div className="aspect-square overflow-hidden bg-zinc-100 relative">
        <img src={imgUrl(listing.images?.[0])} alt={listing.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        <span className="absolute top-2 left-2"><Badge className="!bg-black !text-white !border-black">Resale</Badge></span>
      </div>
      <div className="p-4 flex flex-col flex-1">
        <p className="text-xs font-mono uppercase tracking-widest text-zinc-500">{CONDITION_LABEL[listing.condition]} · {listing.seller_name}</p>
        <h3 className="font-bold leading-tight mt-1 line-clamp-2">{listing.title}</h3>
        <div className="mt-auto pt-3 flex items-center justify-between">
          <span className="text-xl font-black">${listing.price.toFixed(2)}</span>
        </div>
      </div>
    </Link>
  );
}
