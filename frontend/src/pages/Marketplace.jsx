import { useEffect, useState, useCallback } from "react";
import { useSearchParams, Link } from "react-router-dom";
// Fix: Convert path aliases to relative references to clear compilation crashes
import api from "../lib/api";
import { ListingCard } from "../components/cards";
import { Spinner, EmptyState, Btn } from "../components/common";
import { SelectFilter } from "./Store";
import { SlidersHorizontal } from "lucide-react";

const CONDITIONS = [["", "All conditions"], ["new", "New"], ["like_new", "Like New"], ["good", "Good"], ["fair", "Fair"]];

export default function Marketplace() {
  const [searchParams] = useSearchParams();
  const [listings, setListings] = useState(null);
  const [condition, setCondition] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [sort, setSort] = useState("newest");
  const search = searchParams.get("search") || "";

  const load = useCallback(async () => {
    setListings(null);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (condition) params.set("condition", condition);
    if (maxPrice) params.set("max_price", maxPrice);
    params.set("sort", sort);
    const { data } = await api.get(`/listings?${params.toString()}`);
    setListings(data);
  }, [search, condition, maxPrice, sort]);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="border-b-2 border-black pb-4 mb-8 flex flex-wrap justify-between items-end gap-4">
        <div>
          <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter">Resale Market</h1>
          <p className="text-zinc-500 mt-1">Used gear from real sellers. Live instantly.</p>
        </div>
        <Link to="/sell"><Btn data-testid="market-sell-btn">Sell your item</Btn></Link>
      </div>

      <div className="grid lg:grid-cols-[240px_1fr] gap-8">
        <aside className="space-y-6">
          <div className="flex items-center gap-2 font-black uppercase"><SlidersHorizontal size={18} /> Filters</div>
          <div>
            <h4 className="text-sm font-bold uppercase mb-2">Condition</h4>
            <SelectFilter value={condition} onChange={setCondition} options={CONDITIONS} testid="filter-condition" />
          </div>
          <div>
            <h4 className="text-sm font-bold uppercase mb-2">Max price</h4>
            <input type="number" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} placeholder="$" className="w-full border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none" data-testid="filter-max-price" />
          </div>
        </aside>
        <div>
          <div className="flex justify-between items-center mb-6">
            <p className="font-mono text-sm text-zinc-500 uppercase">{listings ? `${listings.length} listings` : ""}</p>
            <SelectFilter value={sort} onChange={setSort} options={[["newest", "Newest"], ["price_asc", "Price ↑"], ["price_desc", "Price ↓"]]} testid="sort-select" small />
          </div>
          {listings === null ? <Spinner /> : listings.length === 0 ? (
            <EmptyState title="No listings yet" subtitle="Be the first to sell something." action={<Link to="/sell"><Btn>Sell an item</Btn></Link>} />
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
              {listings.map((l) => <ListingCard key={l.id} listing={l} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
