import { useEffect, useState } from "react";
import api, { imgUrl } from "@/lib/api";
import { Btn, Spinner, Badge } from "@/components/common";
import { toast } from "sonner";
import { BarChart3, ShoppingBag, Tag, Wallet, Ticket, Package } from "lucide-react";

const TABS = [
  ["overview", "Overview", BarChart3],
  ["orders", "Orders", ShoppingBag],
  ["listings", "Listings", Tag],
  ["products", "Products", Package],
  ["payouts", "Payouts", Wallet],
  ["coupons", "Coupons", Ticket],
];

export default function AdminDashboard() {
  const [tab, setTab] = useState("overview");
  // State for metrics
  const [metrics, setMetrics] = useState({ revenue: 0, commissions: 0 });

  // Fetch metrics when overview tab is active
  useEffect(() => {
    if (tab === "overview") {
      api.get("/api/admin/metrics")
        .then((res) => setMetrics(res.data))
        .catch((err) => console.error("Failed to load metrics", err));
    }
  }, [tab]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter border-b-2 border-black pb-4 mb-6">
        Admin Control
      </h1>
      
      {/* Metrics Section for Overview */}
      {tab === "overview" && (
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="p-6 border-2 border-zinc-900">
            <h3 className="font-bold uppercase tracking-tighter">Total Revenue</h3>
            <p className="text-3xl font-black">${metrics.revenue.toFixed(2)}</p>
          </div>
          <div className="p-6 border-2 border-zinc-900">
            <h3 className="font-bold uppercase tracking-tighter">Total Commissions</h3>
            <p className="text-3xl font-black">${metrics.commissions.toFixed(2)}</p>
          </div>
        </div>
      )}

      {/* Existing Tabs rendering logic goes below here */}
      <div className="flex gap-2 flex-wrap mb-8">
        {TABS.map(([id, label, Icon]) => (
          <button key={id} onClick={() => setTab(id)} className="...">
            <Icon size={16} /> {label}
          </button>
        ))}
      </div>
      
      {/* Rest of your dashboard content... */}
    </div>
  );
}
