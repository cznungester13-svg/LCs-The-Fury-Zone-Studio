import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider } from "@/context/AuthContext";
import { CartProvider } from "@/context/CartContext";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { ProtectedRoute } from "@/components/ProtectedRoute";

import Home from "@/pages/Home";
import Store from "@/pages/Store";
import ProductDetail from "@/pages/ProductDetail";
import Marketplace from "@/pages/Marketplace";
import ListingDetail from "@/pages/ListingDetail";
import SellItem from "@/pages/SellItem";
import Cart from "@/pages/Cart";
import CheckoutSuccess from "@/pages/CheckoutSuccess";
import Orders from "@/pages/Orders";
import SellerDashboard from "@/pages/SellerDashboard";
import Profile from "@/pages/Profile";
import Notifications from "@/pages/Notifications";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import AdminDashboard from "@/pages/AdminDashboard";
import Community from "@/pages/Community";
function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <BrowserRouter>
          <Toaster 
            position="top-center" 
            toastOptions={{ 
              style: { 
                borderRadius: 0, 
                border: "2px solid #0A0A0A", 
                fontWeight: 600,
                fontFamily: "var(--font-mono, monospace)"
              } 
            }} 
          />
          <div className="min-h-screen flex flex-col bg-white">
            <Navbar />
            <main className="flex-1">
              <Routes>
                {/* Public Routing Entries */}
                <Route path="/" element={<Home />} />
                <Route path="/store" element={<Store />} />
                <Route path="/product/:id" element={<ProductDetail />} />
                <Route path="/marketplace" element={<Marketplace />} />
                <Route path="/listing/:id" element={<ListingDetail />} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/checkout/success" element={<CheckoutSuccess />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Secure Auth Protected Routes */}
                <Route path="/sell" element={<ProtectedRoute><SellItem /></ProtectedRoute>} />
                <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
                <Route path="/seller" element={<ProtectedRoute><SellerDashboard /></ProtectedRoute>} />
                <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
                <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
                
                {/* Admin Bound Control Spaces */}
                <Route path="/admin" element={<ProtectedRoute admin><AdminDashboard /></ProtectedRoute>} />

                {/* Catch-All 404 Redirect/Fallback Block */}
                <Route path="*" element={
                  <div className="max-w-md mx-auto px-4 py-20 text-center">
                    <h2 className="text-4xl font-black uppercase tracking-tight mb-2">404 - Not Found</h2>
                    <p className="text-zinc-500 text-sm mb-6">The page you are looking for does not exist.</p>
                    <Navigate to="/" replace />
                  </div>
                } />
              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
