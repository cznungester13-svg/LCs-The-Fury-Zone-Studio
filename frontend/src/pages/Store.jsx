import React from "react";

export default function Store({ departments = [], products = [], options = [] }) {
  const safeDepartments = Array.isArray(departments) ? departments : [];
  const safeProducts = Array.isArray(products) ? products : [];
  const safeOptions = Array.isArray(options) ? options : [];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Departments Navigation */}
      <div className="flex gap-4 mb-8 overflow-x-auto pb-2">
        {safeDepartments.map((d) => (
          <button
            key={d.id || d}
            className="px-4 py-2 bg-zinc-100 hover:bg-zinc-200 rounded-full font-semibold text-sm"
          >
            {d.name || d}
          </button>
        ))}
      </div>

      {/* Filter Options */}
      {safeOptions.length > 0 && (
        <div className="flex gap-2 mb-6">
          {safeOptions.map((opt) => (
            <span key={opt.id || opt} className="text-xs bg-zinc-200 px-2 py-1 rounded">
              {opt.label || opt}
            </span>
          ))}
        </div>
      )}

      {/* Products Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {safeProducts.length > 0 ? (
          safeProducts.map((p) => (
            <div key={p.id || p._id} className="border rounded-lg p-4 shadow-sm hover:shadow-md transition">
              {p.image && (
                <img
                  src={p.image}
                  alt={p.name}
                  className="w-full h-48 object-cover rounded-md mb-4"
                />
              )}
              <h3 className="font-bold text-lg mb-1">{p.name || "Product"}</h3>
              <p className="text-zinc-600 font-semibold mb-2">
                ${typeof p.price === "number" ? p.price.toFixed(2) : p.price || "0.00"}
              </p>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12 text-zinc-500">
            No products found or endpoint failed to return an array.
          </div>
        )}
      </div>
    </div>
  );
}