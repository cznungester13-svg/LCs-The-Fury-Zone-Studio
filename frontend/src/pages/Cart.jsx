import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { useCart } from "@/context/CartContext";
import { useAuth } from "@/context/AuthContext";
import { Btn, EmptyState, Spinner } from "@/components/common";
import { toast } from "sonner";
import { Trash2, Tag } from "lucide-react";

export default function Cart() {
  const { cart, refreshCart, updateItem, removeItem } = useCart();
  const { user, ready } = useAuth();
  const navigate = useNavigate();
  const [coupon, setCoupon] = useState("");
  const [applied, setApplied] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [addressId, setAddressId] = useState("");
  const [checkingOut, setCheckingOut] = useState(false);

  useEffect(() => {
    if (user) {
      refreshCart();
      api.get("/addresses")
        .then(({ data }) => {
          setAddresses(data);
          if (data && data[0]) setAddressId(data[0].id);
        })
        .catch((err) => console.error("Error loading shipping addresses:", err));
    }
  }, [user]);

  if (ready && !user) {
    return (
      <div className="py-24 text-center">
        <EmptyState 
          title="Login to view cart" 
          action={<Link to="/login"><Btn>Login</Btn></Link>} 
        />
      </div>
    );
  }

  if (!cart) return <Spinner />;

  // Derived state calculations (resilient to API delay variations)
  const subtotal = cart.items?.reduce((acc, it) => acc + (Number(it.price || 0) * (it.quantity || 1)), 0) || 0;
  const discount = applied ? (subtotal * applied.percent_off) / 100 : 0;
  const total = Math.max(subtotal - discount, 0);

  const applyCoupon = async () => {
    if (!coupon.trim()) return toast.error("Please enter a coupon code");
    try {
      const { data } = await api.post("/coupons/validate", { code: coupon.trim() });
      setApplied(data);
      toast.success(`${data.percent_off}% off applied`);
    } catch {
      toast.error("Invalid coupon");
      setApplied(null);
    }
  };

  const checkout = async () => {
    setCheckingOut(true);
    try {
      const { data } = await api.post("/checkout/session", {
        origin_url: window.location.origin,
        coupon_code: applied ? applied.code : null,
        address_id: addressId || null,
      });
      if (data?.url) {
        window.location.href = data.url;
      } else {
        throw new Error("No checkout URL returned");
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || "Checkout failed. Please try again.");
      setCheckingOut(false);
    }
  };

  if (!cart.items?.length) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16">
        <EmptyState 
          title="Your cart is empty" 
          subtitle="Add some items to get started." 
          action={<Link to="/store"><Btn>Shop the store</Btn></Link>} 
        />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-4xl sm:text-5xl font-black uppercase tracking-tighter border-b-2 border-black pb-4 mb-8">Cart</h1>
      <div className="grid lg:grid-cols-[1fr_360px] gap-10">
        <div className="space-y-4">
          {cart.items.map((it) => (
            <div key={`${it.item_id}-${it.variant_id || 'default'}`} className="flex gap-4 border-2 border-black p-4" data-testid={`cart-item-${it.item_id}`}>
              <img src={it.image ? imgUrl(it.image) : "/placeholder-product.jpg"} alt={it.title} className="w-24 h-24 object-cover border-2 border-zinc-200" />
              <div className="flex-1">
                <div className="flex justify-between">
                  <div>
                    <p className="font-mono text-xs uppercase text-zinc-500">{it.item_type === "listing" ? "Resale" : "Store"}</p>
                    <h3 className="font-bold">{it.title}</h3>
                  </div>
                  <button onClick={() => removeItem(it.item_id)} className="text-zinc-400 hover:text-[#FF3B30]" data-testid={`remove-${it.item_id}`} aria-label="Remove item">
                    <Trash2 size={18} />
                  </button>
                </div>
                <div className="flex justify-between items-center mt-3">
                  {it.item_type === "product" ? (
                    <div className="flex items-center border-2 border-black bg-white">
                      <button 
                        type="button"
                        onClick={() => updateItem({ item_type: it.item_type, item_id: it.item_id, quantity: Math.max(1, it.quantity - 1), variant_id: it.variant_id || null })} 
                        className="px-3 py-1 hover:bg-black hover:text-white font-bold"
                      >
                        −
                      </button>
                      <span className="px-3 font-bold select-none">{it.quantity}</span>
                      <button 
                        type="button"
                        onClick={() => updateItem({ item_type: it.item_type, item_id: it.item_id, quantity: it.quantity + 1, variant_id: it.variant_id || null })} 
                        className="px-3 py-1 hover:bg-black hover:text-white font-bold"
                      >
                        +
                      </button>
                    </div>
                  ) : (
                    <span className="font-mono text-sm text-zinc-500">Qty 1</span>
                  )}
                  <span className="font-black text-lg">${(Number(it.price || 0) * (it.quantity || 1)).toFixed(2)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="border-2 border-black brutal-shadow p-6 h-fit space-y-4 bg-white">
          <h2 className="text-2xl font-black uppercase">Summary</h2>
          {addresses.length > 0 && (
            <div>
              <label className="block text-sm font-bold uppercase mb-2">Ship to</label>
              <select value={addressId} onChange={(e) => setAddressId(e.target.value)} className="w-full border-2 border-zinc-200 px-3 py-2 outline-none focus:border-black bg-white font-mono text-xs" data-testid="cart-address">
                {addresses.map((a) => <option key={a.id} value={a.id}>{a.label} — {a.line1}, {a.city}</option>)}
              </select>
            </div>
          )}
          <div className="flex gap-2">
            <input value={coupon} onChange={(e) => setCoupon(e.target.value)} placeholder="Coupon code" className="flex-1 border-2 border-zinc-200 focus:border-black px-3 py-2 outline-none uppercase font-mono text-sm" data-testid="coupon-input" />
            <Btn variant="secondary" onClick={applyCoupon} className="!px-4 !py-2" data-testid="apply-coupon" aria-label="Apply Coupon"><Tag size={16} /></Btn>
          </div>
          <div className="space-y-2 border-t-2 border-black pt-4 font-mono text-sm">
            <Row label="Subtotal" value={`$${subtotal.toFixed(2)}`} />
            {applied && <Row label={`Discount (${applied.percent_off}%)`} value={`-$${discount.toFixed(2)}`} accent />}
            <div className="flex justify-between text-xl font-black pt-2 border-t border-zinc-200"><span>Total</span><span data-testid="cart-total">${total.toFixed(2)}</span></div>
          </div>
          <Btn onClick={checkout} disabled={checkingOut} className="w-full" data-testid="checkout-btn">{checkingOut ? "Redirecting..." : "Checkout with Stripe"}</Btn>
          <p className="text-xs text-zinc-400 font-mono text-center">Test card: 4242 4242 4242 4242</p>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value, accent }) {
  return <div className={`flex justify-between ${accent ? "text-[#FF3B30]" : ""}`}><span>{label}</span><span>{value}</span></div>;
}
