import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { Spinner, EmptyState, Badge } from "@/components/common";
import { toast } from "sonner";

const STATUS_STEPS = ["pending", "paid", "shipped", "delivered"];
const STATUS_COLOR = {
  pending: "!bg-yellow-100 text-yellow-800", 
  paid: "!bg-blue-100 text-blue-800", 
  shipped: "!bg-purple-100 text-purple-800",
  delivered: "!bg-green-100 text-green-800", 
  refunded: "!bg-red-100 !text-[#FF3B30]", 
  cancelled: "!bg-zinc-200 text-zinc-800",
};

export default function Orders() {
  const [orders, setOrders] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/orders")
      .then(({ data }) => setOrders(data || []))
      .catch((err) => {
        console.error("Failed to load orders:", err);
        setError("Could not retrieve orders. Please try again.");
        toast.error("Failed to fetch order history");
      });
  }, []);

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <p className="text-[#FF3B30] font-bold uppercase tracking-wider">{error}</p>
      </div>
    );
  }

  if (!orders) return <Spinner />;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter border-b-2 border-black pb-4 mb-8">My Orders</h1>
      {orders.length === 0 ? (
        <EmptyState title="No orders yet" action={<Link to="/store"><span className="underline font-bold">Start shopping</span></Link>} />
      ) : (
        <div className="space-y-6">
          {orders.map((o) => (
            <div key={o.id} className="border-2 border-black bg-white" data-testid={`order-${o.id}`}>
              <div className="flex justify-between items-center px-5 py-3 border-b-2 border-black bg-zinc-50">
                <div>
                  <p className="font-black uppercase">Order #{String(o.id || "").slice(0, 8)}</p>
                  <p className="text-xs font-mono text-zinc-500">
                    {o.created_at ? new Date(o.created_at).toLocaleString() : "Date Unknown"}
                  </p>
                </div>
                <Badge className={STATUS_COLOR[o.status] || "!bg-zinc-100 text-zinc-800"}>{o.status}</Badge>
              </div>
              <div className="p-5">
                {!["refunded", "cancelled"].includes(o.status) && (
                  <div className="flex flex-wrap items-center gap-y-4 mb-6 border-b border-zinc-100 pb-5">
                    {STATUS_STEPS.map((s, i) => {
                      const done = STATUS_STEPS.indexOf(o.status) >= i;
                      return (
                        <div key={s} className="flex items-center flex-1 last:flex-none">
                          <div className={`w-8 h-8 flex items-center justify-center border-2 border-black text-xs font-bold ${done ? "bg-[#FF3B30] text-white" : "bg-white text-black"}`}>{i + 1}</div>
                          <span className="ml-2 text-xs font-bold uppercase hidden sm:block">{s}</span>
                          {i < STATUS_STEPS.length - 1 && <div className={`flex-1 h-1 mx-2 ${done ? "bg-[#FF3B30]" : "bg-zinc-200"}`} />}
                        </div>
                      );
                    })}
                  </div>
                )}
                <div className="space-y-3">
                  {(o.items || []).map((it, idx) => (
                    <div key={`${o.id}-item-${it.item_id || idx}`} className="flex items-center gap-3">
                      <img 
                        src={it.image ? imgUrl(it.image) : "/placeholder-product.jpg"} 
                        alt="" 
                        className="w-12 h-12 object-cover border border-zinc-200 bg-zinc-50" 
                      />
                      <span className="flex-1 text-sm font-bold">{it.title || "Unknown Item"} <span className="text-zinc-400">×{it.quantity || 1}</span></span>
                      <span className="font-mono text-sm">${(Number(it.price || 0) * (it.quantity || 1)).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between mt-4 pt-3 border-t-2 border-dashed border-zinc-200 font-black">
                  <span>Total</span><span>${Number(o.total || 0).toFixed(2)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
