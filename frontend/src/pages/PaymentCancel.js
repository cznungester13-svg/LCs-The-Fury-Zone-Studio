import React from "react";
import { Link } from "react-router-dom";
import { XCircle } from "lucide-react";

export default function PaymentCancel() {
  return (
    <div className="mx-auto max-w-lg px-4 py-24 text-center" data-testid="payment-cancel-page">
      <XCircle size={64} className="mx-auto mb-4 text-orange" />
      <h1 className="font-display text-5xl uppercase">Payment cancelled</h1>
      <p className="mt-3 font-mono text-sm text-ash">No charge made. Your cart is exactly where you left it.</p>
      <div className="mt-6 flex justify-center gap-3">
        <Link to="/cart" className="brutal-btn brutal-btn-primary" data-testid="back-to-cart-btn">Back to Cart</Link>
        <Link to="/shop" className="brutal-btn">Keep Browsing</Link>
      </div>
    </div>
  );
}
