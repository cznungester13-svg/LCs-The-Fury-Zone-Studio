import { useEffect, useState, useRef } from "react";
import { Link, useSearchParams } from "react-router-dom";
import api from "@/lib/api";
import { useCart } from "@/context/CartContext";
import { Btn } from "@/components/common";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";

export default function CheckoutSuccess() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const { refreshCart } = useCart();
  const [status, setStatus] = useState("checking"); // checking | paid | failed | timeout
  const [orderId, setOrderId] = useState(null);
  const attempts = useRef(0);
  const timeoutId = useRef(null);

  useEffect(() => {
    if (!sessionId) {
      setStatus("failed");
      return;
    }
    let cancelled = false;

    const poll = async () => {
      if (attempts.current >= 6) {
        if (!cancelled) setStatus("timeout");
        return;
      }
      attempts.current += 1;
      
      try {
        const { data } = await api.get(`/checkout/status/${sessionId}`);
        if (cancelled) return;

        if (data.payment_status === "paid") {
          setStatus("paid");
          setOrderId(data.order_id);
          refreshCart();
          return;
        }
        if (data.status === "expired") {
          setStatus("failed");
          return;
        }
        
        if (!cancelled) {
          timeoutId.current = setTimeout(poll, 2000);
        }
      } catch (err) {
        if (!cancelled) {
          timeoutId.current = setTimeout(poll, 2000);
        }
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (timeoutId.current) clearTimeout(timeoutId.current);
    };
  }, [sessionId]);

  return (
    <div className="max-w-lg mx-auto px-4 py-24 text-center">
      <div className="border-2 border-black brutal-shadow p-10 bg-white">
        {status === "checking" && (
          <>
            <Loader2 className="animate-spin mx-auto text-[#FF3B30]" size={56} />
            <h1 className="text-3xl font-black uppercase mt-6">Confirming payment</h1>
            <p className="text-zinc-500 mt-2">Hang tight, verifying with Stripe...</p>
          </>
        )}
        {status === "paid" && (
          <>
            <CheckCircle2 className="mx-auto text-green-500" size={56} />
            <h1 className="text-3xl font-black uppercase mt-6" data-testid="payment-success">Order confirmed!</h1>
            {orderId && <p className="font-mono text-xs text-zinc-400 mt-1">Order ID: {orderId}</p>}
            <p className="text-zinc-500 mt-2">Thanks for shopping the Zone.</p>
            <div className="flex gap-3 mt-8 justify-center">
              <Link to="/orders"><Btn data-testid="view-orders-btn">View orders</Btn></Link>
              <Link to="/store"><Btn variant="secondary">Keep shopping</Btn></Link>
            </div>
          </>
        )}
        {(status === "failed" || status === "timeout") && (
          <>
            <XCircle className="mx-auto text-[#FF3B30]" size={56} />
            <h1 className="text-3xl font-black uppercase mt-6">{status === "timeout" ? "Still processing" : "Payment issue"}</h1>
            <p className="text-zinc-500 mt-2">{status === "timeout" ? "Check your orders shortly." : "Something went wrong with the payment."}</p>
            <div className="flex gap-3 mt-8 justify-center">
              <Link to="/cart"><Btn>Back to cart</Btn></Link>
              <Link to="/orders"><Btn variant="secondary">My orders</Btn></Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
