import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Ticket, Trophy, Clock, Sparkles } from "lucide-react";
import api from "../lib/api";
import { useAuth } from "../context/AuthContext";

function useCountdown(end) {
  const [left, setLeft] = useState("");
  useEffect(() => {
    if (!end) return;
    const tick = () => {
      const diff = new Date(end) - new Date();
      if (diff <= 0) return setLeft("Drawing now...");
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000) / 60000);
      const s = Math.floor((diff % 60000) / 1000);
      setLeft(`${d}d ${h}h ${m}m ${s}s`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [end]);
  return left;
}

export default function Raffle() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const countdown = useCountdown(data?.period_end);

  useEffect(() => {
    api.get("/raffle").then((r) => setData(r.data)).catch(() => {});
  }, [user]);

  if (!data) return <div className="py-24 text-center font-display text-3xl uppercase text-ash">Loading raffle...</div>;

  const toNext = Math.max(0, data.next_ticket_at - data.my_spent);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 md:px-6" data-testid="raffle-page">
      <div className="mb-8 border-2 border-ink bg-sale p-8 text-white" style={{ boxShadow: "8px 8px 0 #0A0A0A" }}>
        <span className="tag bg-highlighter text-ink">WEEKLY RAFFLE</span>
        <h1 className="mt-3 font-display text-5xl uppercase leading-none tracking-tight md:text-6xl">Win {data.prize}</h1>
        <p className="mt-3 max-w-lg font-body text-lg text-white/90">
          Earn <span className="font-bold">1 raffle ticket for every ${data.ticket_per} you spend</span>. A winner is drawn automatically every week. More tickets, better odds.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="border-2 border-ink bg-highlighter p-6" style={{ boxShadow: "4px 4px 0 #0A0A0A" }} data-testid="my-tickets-card">
          <Ticket size={30} strokeWidth={2.5} />
          <div className="mt-3 font-display text-5xl leading-none">{data.my_tickets}</div>
          <div className="font-mono text-sm uppercase">your tickets</div>
          {user ? (
            <p className="mt-3 font-mono text-xs text-ink/70" data-testid="to-next-ticket">Spend ${toNext.toFixed(2)} more for your next ticket.</p>
          ) : (
            <Link to="/login" className="mt-3 inline-block font-mono text-xs font-bold underline">Sign in to collect tickets</Link>
          )}
        </div>

        <div className="border-2 border-ink bg-electric p-6 text-white" style={{ boxShadow: "4px 4px 0 #0A0A0A" }}>
          <Clock size={30} strokeWidth={2.5} className="text-highlighter" />
          <div className="mt-3 font-display text-3xl leading-none" data-testid="countdown">{countdown}</div>
          <div className="font-mono text-sm uppercase">until the draw</div>
        </div>

        <div className="border-2 border-ink bg-white p-6" style={{ boxShadow: "4px 4px 0 #0A0A0A" }}>
          <Sparkles size={30} strokeWidth={2.5} className="text-orange" />
          <div className="mt-3 font-display text-5xl leading-none">{data.total_tickets}</div>
          <div className="font-mono text-sm uppercase">tickets in the pot · {data.entrants} players</div>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/shop" className="brutal-btn brutal-btn-primary" data-testid="raffle-shop-btn">Shop to Earn Tickets</Link>
        <Link to="/sell" className="brutal-btn">Sell Your Stuff</Link>
      </div>

      <section className="mt-12">
        <div className="mb-4 flex items-center gap-3">
          <Trophy size={26} strokeWidth={2.5} className="text-orange" />
          <h2 className="font-display text-3xl uppercase tracking-tight">Past Winners</h2>
        </div>
        {data.past_winners.length === 0 ? (
          <div className="border-2 border-dashed border-ink/40 p-8 text-center font-mono text-sm text-ash" data-testid="no-winners">
            No winners yet — be the first. The next draw is automatic.
          </div>
        ) : (
          <div className="space-y-3" data-testid="past-winners">
            {data.past_winners.map((w) => (
              <div key={w.id} className="flex items-center justify-between border-2 border-ink bg-white p-4" style={{ boxShadow: "4px 4px 0 #0A0A0A" }}>
                <div className="flex items-center gap-3">
                  <Trophy size={22} className="text-highlighter" fill="#E5FF00" strokeWidth={2} />
                  <span className="font-heading font-bold uppercase">{w.winner_name}</span>
                </div>
                <div className="text-right">
                  <div className="font-display text-xl text-orange">{w.prize}</div>
                  <div className="font-mono text-xs text-ash">{new Date(w.drawn_at).toLocaleDateString()}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
