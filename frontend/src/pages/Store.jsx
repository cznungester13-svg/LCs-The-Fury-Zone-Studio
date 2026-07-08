import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
// Fix: Use traditional relative paths to ensure your build compiles correctly
import api from "../lib/api";
import { ProductCard } from "../components/cards";
import { Spinner, EmptyState, Btn } from "../components/common";
import { SlidersHorizontal } from "lucide-react";

export default function Store() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [brands, setBrands] = useState([]);
  const [sort, setSort] = useState("newest");
  const [dept, setDept] = useState("");
  const [brand, setBrand] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const search = searchParams.get("search") || "";

  useEffect(() => {
    api.get("/departments").then(({ data }) => setDepartments(data));
    api.get("/brands").then(({ data }) => setBrands(data));
  }, []);

  const load = useCallback(async () => {
    setProducts(null);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (dept) params.set("department_id", dept);
    if (brand) params.set("brand_id", brand);
    if (maxPrice) params.set("max_price", maxPrice);
    params.set("sort", sort);
    const { data } = await api.get(`/products?${params.toString()}`);
    setProducts(data);
  }, [search, dept, brand, maxPrice, sort]);

  useEffect(() => { load(); }, [load]);

  const clearFilters = () => { setDept(""); setBrand(""); setMaxPrice(""); setSort("newest"); setSearchParams({}); };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="border-b-2 border-black pb-4 mb-8">
        <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter">The Store</h1>
        <p className="text-zinc-500 mt-1">{search ? `Results for "${search}"` : "Brand new gear, straight from the source."}</p>
      </div>

      <div className="grid lg:grid-cols-[240px_1fr] gap-8">
        <aside className="space-y-6">
          <div className="flex items-center gap-2 font-black uppercase"><SlidersHorizontal size={18} /> Filters</div>
          <FilterGroup title="Department">
            <SelectFilter value={dept} onChange={setDept} options={[["", "All"], ...departments.map((d) => [d.id, d.name])]} testid="filter-department" />
          </FilterGroup>
          <FilterGroup title="Brand">
            <SelectFilter value={brand} onChange={setBrand} options={[["", "All"], ...brands.map((b) => [b.id, b.name])]} testid="filter-brand" />
          </FilterGroup>
          <FilterGroup title="Max price">
            <input type="number" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} placeholder="$" className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none" data-testid="filter-max-price" />
          </FilterGroup>
          <Btn variant="outline" onClick={clearFilters} className="w-full !px-3 !py-2 text-sm" data-testid="clear-filters">Clear filters</Btn>
        </aside>

        <div>
          <div className="flex justify-between items-center mb-6">
            <p className="font-mono text-sm text-zinc-500 uppercase">{products ? `${products.length} items` : ""}</p>
            <SelectFilter value={sort} onChange={setSort} options={[["newest", "Newest"], ["price_asc", "Price ↑"], ["price_desc", "Price ↓"]]} testid="sort-select" small />
          </div>
          {products === null ? <Spinner /> : products.length === 0 ? (
            <EmptyState title="No products found" subtitle="Try adjusting your filters." action={<Btn onClick={clearFilters}>Clear filters</Btn>} />
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
              {products.map((p) => <ProductCard key={p.id} product={p} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FilterGroup({ title, children }) {
  return (
    <div>
      <h4 className="text-sm font-bold uppercase tracking-wider mb-2">{title}</h4>
      {children}
    </div>
  );
}

export function SelectFilter({ value, onChange, options, testid, small }) {
  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} data-testid={testid}
      className={`border-2 border-zinc-200 focus:border-black outline-none font-bold uppercase text-sm ${small ? "px-3 py-2" : "w-full px-3 py-2"}`}>
      {options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
    </select>
  );
}
