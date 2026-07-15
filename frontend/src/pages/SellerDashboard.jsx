import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { Btn, Spinner, Badge, EmptyState, CONDITION_LABEL } from "@/components/common";
import { toast } from "sonner";
import { Wallet, Package, TrendingUp, Trash2, Plus } from "lucide-react";

export default function SellerDashboard() {
  const [stats, setStats] = useState(null);
  const [listings, setListings] = useState([]);
  const [payouts, setPayouts] = useState([]);
  const [amount, setAmount] = useState("");
  const [error, setError] = useState(null);

  const load = () => {
    Promise.all([
      api.get("/seller/stats"),
      api.get("/my/listings"),
      api.get("/seller/payouts")
    ])
      .then(([{ data: statsData }, { data: listingsData }, { data: payoutsData }]) => {
        setStats(statsData);
        setListings(listingsData || []);
        setPayouts(payoutsData || []);
      })
      .catch((err) => {
        console.error("Dashboard failed to sync:", err);
        setError("Unable to load seller analytics.");
        toast.error("Network error sync failed");
      });
  };

  useEffect(() => {
    load();
  }, []);

  const remove = async (id) => {
    try {
      await api.delete(`/listings/${id}`);
      toast.success("Listing removed");
      load();
    } catch (err) {
      toast.error("Failed to delete listing");
    }
  };

  const requestPayout = async (e) => {
    e.preventDefault();
    const numericAmount = Number(amount);

    if (!numericAmount || numericAmount <= 0) {
      return toast.error("Enter a valid payout amount");
    }
    if (numericAmount > (stats?.available || 0)) {
      return toast.error("Payout request exceeds available balance");
    }

    try {
      await api.post("/seller/payouts", { amount: numericAmount });
      toast.success("Payout requested");
      setAmount("");
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Payout failed");
    }
  };

  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <p className="text-[#FF3B30] font-bold uppercase tracking-wider">{error}</p>
      </div>
    );
  }

  if (!stats) return <Spinner />;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-wrap justify-between items-end border-b-2 border-black pb-4 mb-8 gap-4">
        <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter">Seller Dashboard</h1>
        <Link to="/sell"><Btn data-testid="new-listing-btn"><Plus size={18} /> New listing</Btn></Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <Stat icon={Package} label="Active" value={stats.active_listings} />
        <Stat icon={TrendingUp} label="Sold" value={stats.sold_listings} />
        <Stat icon={Wallet} label="Available" value={`$${Number(stats.available || 0).toFixed(2)}`} accent />
        <Stat icon={Wallet} label="Pending" value={`$${Number(stats.pending || 0).toFixed(2)}`} />
      </div>

      <div className="grid lg:grid-cols-[1fr_340px] gap-10">
        <div>
          <h2 className="text-2xl font-black uppercase mb-4">My Listings</h2>
          {listings.length === 0 ? (
            <EmptyState title="No listings" action={<Link to="/sell"><Btn>Sell an item</Btn></Link>} />
          ) : (
            <div className="space-y-3">
              {listings.map((l) => (
                <div key={l.id} className="flex gap-4 border-2 border-black p-3 items-center" data-testid={`seller-listing-${l.id}`}>
                  <img src={l.images?.[0] ? imgUrl(l.images[0]) : "/placeholder-product.jpg"} alt="" className="w-16 h-16 object-cover border border-zinc-200 bg-zinc-50" />
                  <div className="flex-1">
                    <Link to={`/listing/${l.id}`} className="font-bold hover:text-[#FF3B30]">{l.title}</Link>
                    <div className="flex gap-2 mt-1">
                      <Badge className={l.status === "sold" ? "!bg-green-100 text-green-800" : l.status === "removed" ? "!bg-zinc-200 text-zinc-800" : ""}>{l.status}</Badge>
                      <Badge>{CONDITION_LABEL[l.condition] || "Unknown"}</Badge>
                    </div>
                  </div>
                  <span className="font-black">${Number(l.price || 0).toFixed(2)}</span>
                  {l.status === "active" && (
                    <button onClick={() => remove(l.id)} className="text-zinc-400 hover:text-[#FF3B30]" data-testid={`delete-listing-${l.id}`} aria-label="Delete listing"><Trash2 size={18} /></button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="border-2 border-black brutal-shadow p-5 bg-white">
            <h3 className="font-black uppercase mb-1">Total earned</h3>
            <p className="text-3xl font-black text-[#FF3B30]">${Number(stats.total_earned || 0).toFixed(2)}</p>
            <form onSubmit={requestPayout} className="mt-4">
              <label className="block text-sm font-bold uppercase mb-2">Request payout</label>
              <div className="flex gap-2">
                <input type="number" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="$" className="flex-1 border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none font-mono" data-testid="payout-amount" />
                <Btn type="submit" className="!px-4 !py-2" data-testid="request-payout-btn">Request</Btn>
              </div>
              <p className="text-xs text-zinc-400 mt-1 font-mono">Available: ${Number(stats.available || 0).toFixed(2)}</p>
            </form>
          </div>

          <div>
            <h3 className="font-black uppercase mb-3">Payout history</h3>
            {payouts.length === 0 ? <p className="text-zinc-500 text-sm">No payouts yet.</p> : (
              <div className="space-y-2">
                {payouts.map((p) => (
                  <div key={p.id} className="flex justify-between items-center border-2 border-zinc-200 bg-white px-3 py-2">
                    <span className="font-mono text-sm font-black">${Number(p.amount || 0).toFixed(2)}</span>
                    <Badge className={p.status === "paid" ? "!bg-green-100 text-green-800" : "!bg-yellow-100 text-yellow-800"}>{p.status}</Badge>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ icon: Icon, label, value, accent }) {
  return (
    <div className={`border-2 border-black p-4 ${accent ? "bg-[#FF3B30] text-white" : "bg-white text-black"}`}>
      <Icon size={20} className={accent ? "text-white" : "text-[#FF3B30]"} />
      <p className="text-2xl font-black mt-2">{value}</p>
      <p className="text-xs font-bold uppercase tracking-wider opacity-70">{label}</p>
    </div>
  );
}
