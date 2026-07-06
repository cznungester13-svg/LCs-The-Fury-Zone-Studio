import React from "react";
import { Link } from "react-router-dom";
import { Minus, Plus, Trash2, ShoppingBag, ArrowRight } from "lucide-react";
import { useCart } from "../context/CartContext";
import { currency } from "../lib/api";

export default function Cart() {
  const { items, updateQuantity, removeItem, subtotal } = useCart();
  const shipping = subtotal >= 75 || subtotal === 0 ? 0 : 6.99;
  const total = subtotal + shipping;

  if (items.length === 0) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center px-4 py-28 text-center" data-testid="cart-empty">
        <span className="flex h-20 w-20 items-center justify-center rounded-full bg-secondary">
          <ShoppingBag className="h-9 w-9 text-muted-foreground" />
        </span>
        <h1 className="font-display mt-6 text-3xl font-bold">Your cart is empty</h1>
        <p className="mt-2 text-muted-foreground">Looks like you haven't added anything yet.</p>
        <Link to="/shop" className="mt-6 inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3 font-bold text-white transition-all hover:bg-primary/90 active:scale-95">
          Start shopping <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-8" data-testid="cart-page">
      <h1 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">Your Cart</h1>

      <div className="mt-8 grid gap-8 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          {items.map((item) => (
            <div key={item.id} className="flex gap-4 rounded-2xl border border-border bg-white p-4" data-testid={`cart-item-${item.id}`}>
              <Link to={`/product/${item.id}`} className="h-24 w-24 shrink-0 overflow-hidden rounded-xl bg-secondary">
                <img src={item.image} alt={item.name} className="h-full w-full object-cover" />
              </Link>
              <div className="flex flex-1 flex-col">
                <div className="flex justify-between gap-2">
                  <Link to={`/product/${item.id}`} className="font-semibold leading-snug hover:text-primary">{item.name}</Link>
                  <button onClick={() => removeItem(item.id)} className="text-muted-foreground hover:text-primary" data-testid={`remove-${item.id}`} aria-label="Remove">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{currency(item.price)} each</p>
                <div className="mt-auto flex items-center justify-between pt-2">
                  <div className="flex items-center rounded-full border border-border">
                    <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-secondary" data-testid={`decrease-${item.id}`}>
                      <Minus className="h-3.5 w-3.5" />
                    </button>
                    <span className="w-8 text-center text-sm font-semibold">{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="flex h-8 w-8 items-center justify-center rounded-full hover:bg-secondary" data-testid={`increase-${item.id}`}>
                      <Plus className="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <span className="font-display font-bold">{currency(item.price * item.quantity)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="h-fit rounded-2xl border border-border bg-secondary/40 p-6 lg:sticky lg:top-28" data-testid="order-summary">
          <h2 className="font-display text-lg font-bold">Order Summary</h2>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Subtotal</span>
              <span className="font-semibold" data-testid="summary-subtotal">{currency(subtotal)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Shipping</span>
              <span className="font-semibold">{shipping === 0 ? "Free" : currency(shipping)}</span>
            </div>
            {shipping > 0 && (
              <p className="text-xs text-muted-foreground">Add {currency(75 - subtotal)} more for free shipping.</p>
            )}
            <div className="flex justify-between border-t border-border pt-3 text-base">
              <span className="font-bold">Total</span>
              <span className="font-display font-extrabold" data-testid="summary-total">{currency(total)}</span>
            </div>
          </div>
          <Link
            to="/checkout"
            data-testid="checkout-button"
            className="mt-6 flex h-12 w-full items-center justify-center gap-2 rounded-full bg-primary font-bold text-white transition-all hover:bg-primary/90 active:scale-95"
          >
            Checkout <ArrowRight className="h-4 w-4" />
          </Link>
          <Link to="/shop" className="mt-3 block text-center text-sm font-medium text-muted-foreground hover:text-foreground">
            Continue shopping
          </Link>
        </div>
      </div>
    </div>
  );
}
