import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { ProductCard } from "../components/ProductCard";
import { SlidersHorizontal } from "lucide-react";

const CATS = [
  { id: "all", name: "All" },
  { id: "electronics", name: "Electronics" },
  { id: "fashion", name: "Fashion" },
  { id: "home", name: "Home & Living" },
  { id: "handmade", name: "Handmade" },
  { id: "beauty", name: "Beauty" },
];

export default function Shop() {
  const [params, setParams] = useSearchParams();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  const category = params.get("category") || "all";
  const search = params.get("search") || "";
  const sort = params.get("sort") || "";

  useEffect(() => {
    setLoading(true);

    const query = {};

    if (category !== "all") query.category = category;
    if (search) query.search = search;
    if (sort) query.sort = sort;

    api
      .get("/products", { params: query })
      .then((r) => {
        setProducts(r.data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, [category, search, sort]);

  const setParam = (key, value) => {
    const next = new URLSearchParams(params);

    if (value) next.set(key, value);
    else next.delete(key);

    setParams(next);
  };

  return (
    <div
      className="mx-auto max-w-7xl px-4 py-10 md:px-8"
      data-testid="shop-page"
    >

      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
          {search
            ? `Results for "${search}"`
            : CATS.find((c) => c.id === category)?.name || "Shop"}
        </h1>

        <p
          className="mt-1 text-sm text-muted-foreground"
          data-testid="results-count"
        >
          {loading ? "Loading…" : `${products.length} products`}
        </p>
      </div>


      <div className="mb-8 flex flex-wrap items-center gap-2">

        {CATS.map((c) => (
          <button
            key={c.id}
            onClick={() =>
              setParam("category", c.id === "all" ? "" : c.id)
            }
            data-testid={`filter-${c.id}`}
            className={`rounded-full px-4 py-2 text-sm font-medium transition-all ${
              category === c.id
                ? "bg-foreground text-white"
                : "border border-border bg-white text-muted-foreground hover:border-foreground hover:text-foreground"
            }`}
          >
            {c.name}
          </button>
        ))}


        <div className="ml-auto flex items-center gap-2">

          <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />

          <select
            value={sort}
            onChange={(e) => setParam("sort", e.target.value)}
            data-testid="sort-select"
            className="rounded-full border border-border bg-white px-3 py-2 text-sm font-medium outline-none focus:border-foreground"
          >
            <option value="">Featured</option>
            <option value="price_asc">
              Price: Low to High
            </option>
            <option value="price_desc">
              Price: High to Low
            </option>
            <option value="rating">
              Top Rated
            </option>
          </select>

        </div>

      </div>



      {loading ? (

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">

          {Array.from({ length: 12 }).map((_, i) => (

            <div
              key={i}
              className="aspect-[3/4] animate-pulse rounded-2xl bg-secondary"
            />

          ))}

        </div>


      ) : products.length === 0 ? (

        <div
          className="py-24 text-center"
          data-testid="empty-state"
        >

          <p className="font-display text-2xl font-bold">
            No products found
          </p>

          <p className="mt-2 text-muted-foreground">
            Try a different category or search term.
          </p>

        </div>


      ) : (


        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">

          {products.map((p, i) => (

            <ProductCard
              key={p.id}
              product={p}
              index={i}
            />

          ))}

        </div>


      )}

    </div>
  );
}