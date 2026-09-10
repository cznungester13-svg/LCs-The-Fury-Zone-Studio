import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../lib/api";
import { ProductCard } from "../components/Cards";
import { Spinner } from "../components/common";

export default function Store() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState(null);
  const [categories, setCategories] = useState([]);
  const [departments, setDepartments] = useState([]);

  const category = searchParams.get("category") || "";
  const department = searchParams.get("department") || "";
  const search = searchParams.get("search") || "";
  const sort = searchParams.get("sort") || "newest";

  useEffect(() => {
    let url = `/products?sort=${sort}`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    if (department) url += `&department=${encodeURIComponent(department)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    api.get(url)
      .then(({ data }) => setProducts(Array.isArray(data) ? data : data?.products || []))
      .catch(() => setProducts([]));
  }, [category, department, search, sort]);

  useEffect(() => {
    api.get("/categories")
      .then(({ data }) => setCategories(Array.isArray(data) ? data : data?.categories || []))
      .catch(() => setCategories([]));

    api.get("/departments")
      .then(({ data }) => setDepartments(Array.isArray(data) ? data : data?.departments || []))
      .catch(() => setDepartments([]));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="border-b-2 border-black pb-4 mb-8">
        <h1 className="text-4xl font-black uppercase tracking-tighter">Store Drops</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Filters */}
        <div className="space-y-6">
          <div>
            <h3 className="font-mono text-xs uppercase tracking-widest text-zinc-500 mb-3">Departments</h3>
            <div className="space-y-1">
              <button
                onClick={() => { searchParams.delete("department"); setSearchParams(searchParams); }}
                className={`block text-sm font-bold uppercase ${!department ? "text-[#FF3B30]" : "text-zinc-600 hover:text-black"}`}
              >
                All Departments
              </button>
              {Array.isArray(departments) && departments.map((d) => (
                <button
                  key={d.id || d.slug}
                  onClick={() => { searchParams.set("department", d.slug); setSearchParams(searchParams); }}
                  className={`block text-sm font-bold uppercase ${department === d.slug ? "text-[#FF3B30]" : "text-zinc-600 hover:text-black"}`}
                >
                  {d.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Product Grid */}
        <div className="md:col-span-3">
          {products === null ? (
            <Spinner />
          ) : Array.isArray(products) && products.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 sm:gap-6">
              {products.map((p) => (
                <ProductCard key={p.id} product={p} />
              ))}
            </div>
          ) : (
            <div className="border-2 border-black p-12 text-center font-mono text-sm uppercase">
              No products found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}