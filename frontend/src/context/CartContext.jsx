import { createContext, useContext, useEffect, useState, useCallback } from "react";
// Fix: Resolve paths cleanly via relative file structure
import api from "../lib/api";
import { useAuth } from "./AuthContext";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState({ items: [], subtotal: 0 });

  const refreshCart = useCallback(async () => {
    if (!user) {
      setCart({ items: [], subtotal: 0 });
      return;
    }
    try {
      const { data } = await api.get("/cart");
      setCart(data);
    } catch {
      /* ignore */
    }
  }, [user]);

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  const addToCart = async (payload) => {
    const { data } = await api.post("/cart/add", payload);
    setCart(data);
    return data;
  };

  const updateItem = async (payload) => {
    const { data } = await api.post("/cart/update", payload);
    setCart(data);
  };

  const removeItem = async (itemId) => {
    const { data } = await api.delete(`/cart/item/${itemId}`);
    setCart(data);
  };

  const count = cart.items?.reduce((a, i) => a + i.quantity, 0) || 0;

  return (
    <CartContext.Provider value={{ cart, count, refreshCart, addToCart, updateItem, removeItem }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
