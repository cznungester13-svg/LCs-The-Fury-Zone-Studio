import React from "react";
import { Star } from "lucide-react";
import { Badge as BadgePrimitive } from "./ui/badge";
import { Button } from "./ui/button";

export const CONDITION_LABEL = {
  new: "New",
  used: "Used",
  like_new: "Like New",
  excellent: "Excellent",
  good: "Good",
  fair: "Fair",
};

export function Btn({ children, className = "", variant = "default", size = "default", ...props }) {
  return (
    <Button variant={variant} size={size} className={className} {...props}>
      {children}
    </Button>
  );
}

export function Spinner({ className = "" }) {
  return (
    <div
      className={`inline-block h-6 w-6 animate-spin rounded-full border-2 border-zinc-300 border-t-zinc-900 ${className}`}
      aria-label="Loading"
      role="status"
    />
  );
}

export function EmptyState({ title = "Nothing here yet", subtitle, action }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-none border-2 border-dashed border-zinc-300 bg-zinc-50 px-6 py-12 text-center">
      <h3 className="text-lg font-black uppercase tracking-tight text-zinc-900">{title}</h3>
      {subtitle && <p className="mt-2 text-sm text-zinc-500">{subtitle}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function Badge(props) {
  return <BadgePrimitive {...props} />;
}

export function Stars({ value = 0, count = 0 }) {
  const safeValue = Number(value) || 0;
  const filled = Math.round(safeValue);

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1 text-amber-500">
        {Array.from({ length: 5 }).map((_, index) => (
          <Star
            key={`star-${index}`}
            size={14}
            className={index < filled ? "fill-amber-500" : "text-zinc-300 fill-transparent"}
          />
        ))}
      </div>
      {count > 0 && <span className="text-xs text-zinc-500">({count})</span>}
    </div>
  );
}
