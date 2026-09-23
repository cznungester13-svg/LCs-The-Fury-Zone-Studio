import { useEffect, useState, useCallback } from "react";
import { useSearchParams, Link } from "react-router-dom";
import api from "../lib/api";
import { ProductCard } from "../components/Cards";
import { Spinner, EmptyState, Btn } from "../components/common";
import { SlidersHorizontal } from "lucide-react";

// Shared select filter. Options may be [value, label] pairs, {value,label}/{id,name}
// objects, or plain strings. Calls onChange(value).
export function SelectFilter({ options = [], value, onChange, placeholder, small }) {
  const safe = Array.isArray(options) ? options : [];
  const norm = safe.map((opt) => {
    if (Array.isArray(opt)) return { value: opt[0], label: opt[1] };
    if (opt && typeof opt === "object") return { value: opt.value ?? opt.id, label: opt.label ?? opt.name };
    return { value: opt, label: opt };
  });
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`w-full border-2 border-black px-3 ${small ? "py-1.5" : "py-2"} text-sm font-bold uppercase outline-none bg-white`}
    >
      {placeholder && <option value="">{placeholder}</option>}
      {norm.map((o) => (
        <option key={String(o.value)} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

const SORTS = [["newest", "Newest"], ["price_asc", "Price ↑"], ["price_desc", "Price ↓"]];

export default function Store() {
  const [searchParams] = useSearchParams();
  const search = searchParams.get("search") || "";
  const deptSlug = searchParams.get("department") || "";

  const [departments, setDepartments] = useState([]);
  const [products, setProducts] = useState(null);
  const [departmentId, setDepartmentId] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [sort, setSort] = useState("newest");

  // Load departments once (for the filter dropdown + slug resolution)
  useEffect(() => {
    api.get("/departments").then(({ data }) => setDepartments(Array.isArray(data) ? data : [])).catch(() => setDepartments([]));
  }, []);

  // Resolve ?department=<slug> to an id when departments arrive
  useEffect(() => {
    if (deptSlug && departments.length) {
      const match = departments.find((d) => d.slug === deptSlug || d.id === deptSlug);
      if (match) setDepartmentId(match.id);
    }
  }, [deptSlug, departments]);

  const load = useCallback(async () => {
    setProducts(null);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (departmentId) params.set("department_id", departmentId);
    if (maxPrice) params.set("max_price", maxPrice);
    params.set("sort", sort);
    try {
      const { data } = await api.get(`/products?${params.toString()}`);
      setProducts(Array.isArray(data) ? data : []);
    } catch {
      setProducts([]);
    }
  }, [search, departmentId, maxPrice, sort]);

  useEffect(() => { load(); }, [load]);

  const deptOptions = [["", "All departments"], ...departments.map((d) => [d.id, d.name])];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="border-b-2 border-black pb-4 mb-8 flex flex-wrap justify-between items-end gap-4">
        <div>
          <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter">The Store</h1>
          <p className="text-zinc-500 mt-1">{search ? `Results for "${search}"` : "Fresh gear, new drops weekly."}</p>
        </div>
        <Link to="/marketplace"><Btn variant="secondary" data-testid="store-resale-btn">Shop resale</Btn></Link>
      </div>

      <div className="grid lg:grid-cols-[240px_1fr] gap-8">
        <aside className="space-y-6">
          <div className="flex items-center gap-2 font-black uppercase"><SlidersHorizontal size={18} /> Filters</div>
          <div>
            <h4 className="text-sm font-bold uppercase mb-2">Department</h4>
            <SelectFilter value={departmentId} onChange={setDepartmentId} options={deptOptions} />
          </div>
          <div>
            <h4 className="text-sm font-bold uppercase mb-2">Max price</h4>
            <input
              type="number"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="$"
              className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none"
              data-testid="store-max-price"
            />
          </div>
        </aside>

        <div>
          <div className="flex justify-between items-center mb-6">
            <p className="font-mono text-sm text-zinc-500 uppercase">{products ? `${products.length} products` : ""}</p>
            <div className="w-40">
              <SelectFilter value={sort} onChange={setSort} options={SORTS} small />
            </div>
          </div>
          {products === null ? (
            <Spinner />
          ) : products.length === 0 ? (
            <EmptyState title="No products found" subtitle="Try a different search or filter." action={<Link to="/store"><Btn>Reset</Btn></Link>} />
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6" data-testid="store-grid">
              {products.map((p) => <ProductCard key={p.id} product={p} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
