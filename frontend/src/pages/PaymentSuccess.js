import React, { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { CheckCircle2, Loader2, XCircle, Ticket } from "lucide-react";
import api from "../lib/api";
import { useCart } from "../context/CartContext";

const MAX_POLLS = 8;

export default function PaymentSuccess() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const { refresh } = useCart();
  const [state, setState] = useState("checking"); // checking | paid | pending | error
  const polls = useRef(0);

  useEffect(() => {
    if (!sessionId) {
      setState("error");
      return;
    }
    let timer;
    const poll = async () => {
      try {
        const { data } = await api.get(`/payments/status/${sessionId}`);
        if (data.payment_status === "paid") {
          setState("paid");
          refresh();
          return;
        }
        if (data.status === "expired" || data.payment_status === "failed") {
          setState("error");
          return;
        }
      } catch {
        setState("error");
        return;
      }
      polls.current += 1;
      if (polls.current >= MAX_POLLS) {
        setState("pending");
        return;
      }
      timer = setTimeout(poll, 2000);
    };
    poll();
    return () => clearTimeout(timer);
  }, [sessionId, refresh]);

  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center" data-testid="payment-success-page">
      {state === "checking" && (
        <>
          <Loader2 size={64} className="mx-auto mb-4 animate-spin text-electric" />
          <h1 className="font-display text-4xl uppercase">Confirming payment...</h1>
          <p className="mt-2 font-mono text-sm text-ash">Hang tight, talking to Stripe.</p>
        </>
      )}
      {state === "paid" && (
        <div data-testid="payment-confirmed">
          <CheckCircle2 size={64} className="mx-auto mb-4 text-electric" />
          <h1 className="font-display text-5xl uppercase">Order Locked In!</h1>
          <p className="mt-3 font-mono text-sm text-ash">Payment confirmed. Your treasure is on the way.</p>
          <div className="mx-auto mt-4 flex max-w-xs items-center justify-center gap-2 border-2 border-ink bg-highlighter px-4 py-2 font-mono text-xs font-bold">
            <Ticket size={16} strokeWidth={2.5} /> Raffle tickets updated!
          </div>
          <div className="mt-6 flex justify-center gap-3">
            <Link to="/orders" className="brutal-btn brutal-btn-primary" data-testid="view-orders-btn">View Orders</Link>
            <Link to="/shop" className="brutal-btn">Keep Digging</Link>
          </div>
        </div>
      )}
      {state === "pending" && (
        <>
          <Loader2 size={64} className="mx-auto mb-4 text-orange" />
          <h1 className="font-display text-4xl uppercase">Still processing</h1>
          <p className="mt-2 font-mono text-sm text-ash">Your payment is taking a moment. Check your orders shortly.</p>
          <Link to="/orders" className="brutal-btn brutal-btn-primary mt-6">Go to Orders</Link>
        </>
      )}
      {state === "error" && (
        <>
          <XCircle size={64} className="mx-auto mb-4 text-sale" />
          <h1 className="font-display text-4xl uppercase">Something went sideways</h1>
          <p className="mt-2 font-mono text-sm text-ash">We couldn't confirm this payment.</p>
          <Link to="/cart" className="brutal-btn brutal-btn-primary mt-6">Back to Cart</Link>
        </>
      )}
    </div>
  );
}
