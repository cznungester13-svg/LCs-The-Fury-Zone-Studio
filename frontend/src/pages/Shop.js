import React, { useEffect, useState, useCallback } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { SlidersHorizontal } from "lucide-react";
import api from "../lib/api";
import ProductCard from "../components/ProductCard";

const SORTS = [
  { value: "featured", label: "Featured" },
  { value: "price_asc", label: "Price: Low to High" },
  { value: "price_desc", label: "Price: High to Low" },
  { value: "rating", label: "Top Rated" },
];

export default function Shop() {
  const { slug } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const search = searchParams.get("search") || "";
  const sortParam = searchParams.get("sort") || "featured";

  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 1 });
  const [dept, setDept] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setPage(1);
  }, [slug, search, sortParam]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = { sort: sortParam, page, limit: 24 };
      if (slug) params.department = slug;
      if (search) params.search = search;
      const { data } = await api.get("/products", { params });
      setData(data);
    } finally {
      setLoading(false);
    }
  }, [slug, search, sortParam, page]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (slug) {
      api.get("/departments").then((r) => setDept(r.data.find((d) => d.slug === slug))).catch(() => {});
    } else {
      setDept(null);
    }
  }, [slug]);

  const title = search ? `Results for "${search}"` : dept ? dept.name : "All Departments";

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-6" data-testid="shop-page">
      {/* header banner */}
      <div className="mb-6 border-2 border-ink bg-ink p-6 text-paper" style={{ boxShadow: "4px 4px 0 #FF5C00" }}>
        <span className="tag bg-highlighter text-ink">{data.total} ITEMS</span>
        <h1 className="mt-3 font-display text-4xl uppercase leading-none tracking-tight md:text-6xl" data-testid="shop-title">
          {title}
        </h1>
        {dept && <p className="mt-2 font-mono text-sm text-paper/70">{dept.tagline}</p>}
      </div>

      {/* sort bar */}
      <div className="mb-6 flex flex-wrap items-center gap-3 border-2 border-ink bg-white p-3">
        <span className="flex items-center gap-2 font-heading text-sm font-bold uppercase">
          <SlidersHorizontal size={16} strokeWidth={2.5} /> Sort
        </span>
        {SORTS.map((s) => (
          <button
            key={s.value}
            onClick={() => {
              const next = new URLSearchParams(searchParams);
              next.set("sort", s.value);
              setSearchParams(next);
            }}
            className={`border-2 border-ink px-3 py-1 font-mono text-xs font-bold uppercase transition-colors ${
              sortParam === s.value ? "bg-orange text-white" : "bg-white hover:bg-highlighter"
            }`}
            data-testid={`sort-${s.value}`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="py-20 text-center font-display text-3xl uppercase text-ash" data-testid="loading">Digging through the bins...</div>
      ) : data.items.length === 0 ? (
        <div className="py-20 text-center font-display text-3xl uppercase text-ash" data-testid="empty-state">No treasure found here.</div>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4" data-testid="product-grid">
          {data.items.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}

      {/* pagination */}
      {data.pages > 1 && (
        <div className="mt-8 flex items-center justify-center gap-2" data-testid="pagination">
          <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)} className="brutal-btn px-4 py-2 text-sm disabled:opacity-40" data-testid="prev-page">
            Prev
          </button>
          <span className="border-2 border-ink bg-highlighter px-4 py-2 font-mono text-sm font-bold">
            {page} / {data.pages}
          </span>
          <button disabled={page >= data.pages} onClick={() => setPage((p) => p + 1)} className="brutal-btn px-4 py-2 text-sm disabled:opacity-40" data-testid="next-page">
            Next
          </button>
        </div>
      )}
    </div>
  );
}
