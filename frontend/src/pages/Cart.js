import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Trash2, Minus, Plus, ShoppingBag, ArrowRight } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";

export default function Cart() {
  const { cart, updateItem, removeItem } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center" data-testid="cart-guest">
        <h1 className="font-display text-4xl uppercase">Sign in to shop</h1>
        <p className="mt-3 font-body text-ash">Your cart lives with your account. Log in to start hauling.</p>
        <Link to="/login" className="brutal-btn brutal-btn-primary mt-6" data-testid="cart-login-btn">Sign In <ArrowRight size={18} strokeWidth={2.5} /></Link>
      </div>
    );
  }

  if (cart.items.length === 0) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center" data-testid="cart-empty">
        <ShoppingBag size={56} strokeWidth={2} className="mx-auto mb-4 text-ash" />
        <h1 className="font-display text-4xl uppercase">Cart's empty</h1>
        <p className="mt-3 font-body text-ash">No treasure yet. The bins are calling.</p>
        <Link to="/shop" className="brutal-btn brutal-btn-primary mt-6" data-testid="cart-shop-btn">Start Digging <ArrowRight size={18} strokeWidth={2.5} /></Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 md:px-6" data-testid="cart-page">
      <h1 className="mb-6 font-display text-5xl uppercase tracking-tight">Your Cart</h1>
      <div className="grid gap-8 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          {cart.items.map(({ product, quantity, line_total }) => (
            <div key={product.id} className="flex gap-4 border-2 border-ink bg-white p-4" style={{ boxShadow: "4px 4px 0 #0A0A0A" }} data-testid={`cart-item-${product.id}`}>
              <Link to={`/product/${product.id}`} className="shrink-0">
                <img src={product.image} alt={product.name} className="h-24 w-24 border-2 border-ink object-cover" />
              </Link>
              <div className="flex flex-1 flex-col">
                <Link to={`/product/${product.id}`} className="font-heading text-sm font-bold leading-tight hover:text-orange line-clamp-2">{product.name}</Link>
                <span className="font-mono text-xs text-ash">{product.condition} · ${product.price.toFixed(2)} ea</span>
                <div className="mt-auto flex items-center gap-3 pt-2">
                  <div className="flex items-center border-2 border-ink">
                    <button onClick={() => updateItem(product.id, Math.max(1, quantity - 1))} className="border-r-2 border-ink p-1.5 hover:bg-highlighter" data-testid={`cart-minus-${product.id}`}><Minus size={14} strokeWidth={2.5} /></button>
                    <span className="w-8 text-center font-mono text-sm font-bold">{quantity}</span>
                    <button onClick={() => updateItem(product.id, quantity + 1)} className="border-l-2 border-ink p-1.5 hover:bg-highlighter" data-testid={`cart-plus-${product.id}`}><Plus size={14} strokeWidth={2.5} /></button>
                  </div>
                  <button onClick={() => removeItem(product.id)} className="flex items-center gap-1 font-mono text-xs font-bold uppercase text-sale hover:underline" data-testid={`cart-remove-${product.id}`}>
                    <Trash2 size={14} strokeWidth={2.5} /> Remove
                  </button>
                </div>
              </div>
              <div className="font-display text-2xl leading-none text-orange">${line_total.toFixed(2)}</div>
            </div>
          ))}
        </div>

        <div className="h-fit border-2 border-ink bg-highlighter p-6 lg:sticky lg:top-32" style={{ boxShadow: "6px 6px 0 #0A0A0A" }} data-testid="cart-summary">
          <h2 className="font-display text-2xl uppercase">Summary</h2>
          <div className="mt-4 space-y-2 font-mono text-sm">
            <div className="flex justify-between"><span>Subtotal</span><span data-testid="cart-subtotal">${cart.total.toFixed(2)}</span></div>
            <div className="flex justify-between"><span>Shipping</span><span>FREE</span></div>
          </div>
          <div className="mt-4 flex justify-between border-t-2 border-ink pt-4 font-display text-3xl">
            <span>TOTAL</span><span data-testid="cart-total">${cart.total.toFixed(2)}</span>
          </div>
          <button onClick={() => navigate("/checkout")} className="brutal-btn brutal-btn-primary mt-6 w-full py-4 text-lg" data-testid="checkout-btn">
            Checkout <ArrowRight size={18} strokeWidth={2.5} />
          </button>
        </div>
      </div>
    </div>
  );
}
