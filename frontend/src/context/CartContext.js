import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { toast } from "sonner";
import api, { formatApiErrorDetail } from "../lib/api";
import { useAuth } from "./AuthContext";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState({ items: [], total: 0 });

  const refresh = useCallback(async () => {
    if (!user) {
      setCart({ items: [], total: 0 });
      return;
    }
    try {
      const { data } = await api.get("/cart");
      setCart(data);
    } catch {
      setCart({ items: [], total: 0 });
    }
  }, [user]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addItem = async (product, quantity = 1) => {
    if (!user) {
      toast.error("Please sign in to add items to your cart");
      return { needAuth: true };
    }
    try {
      const { data } = await api.post("/cart", { product_id: product.id, quantity });
      setCart(data);
      toast.success(`Added "${product.name}" to cart`);
      return { ok: true };
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail));
      return { ok: false };
    }
  };

  const updateItem = async (productId, quantity) => {
    try {
      const { data } = await api.put("/cart", { product_id: productId, quantity });
      setCart(data);
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail));
    }
  };

  const removeItem = async (productId) => {
    try {
      const { data } = await api.delete(`/cart/${productId}`);
      setCart(data);
    } catch (e) {
      toast.error(formatApiErrorDetail(e.response?.data?.detail));
    }
  };

  const count = cart.items.reduce((n, i) => n + i.quantity, 0);

  return (
    <CartContext.Provider value={{ cart, count, addItem, updateItem, removeItem, refresh }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
