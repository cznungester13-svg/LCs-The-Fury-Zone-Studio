import React from "react";

export default function Marquee({ text = "SUPER LOW PRICES", items }) {
  const list = items || [
    "SUPER LOW PRICES",
    "THRIFT FINDS DAILY",
    "SUSTAINABLE SHOPPING",
    "NEW ARRIVALS DAILY",
    "50 ITEMS PER DEPT",
    "PRICED TO MOVE",
  ];
  const strip = [...list, ...list];
  return (
    <div className="w-full overflow-hidden border-y-2 border-ink bg-highlighter" data-testid="marquee-bar">
      <div className="flex w-max animate-marquee whitespace-nowrap py-2">
        {strip.map((t, i) => (
          <span key={i} className="mx-6 font-mono text-sm font-bold uppercase tracking-tight text-ink">
            {t} <span className="mx-3">✳</span>
          </span>
        ))}
      </div>
    </div>
  );
}
