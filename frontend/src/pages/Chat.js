import React, { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Send, Users, Wifi, WifiOff } from "lucide-react";
import api from "../lib/api";
import { useAuth } from "../context/AuthContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const WS_URL = `${BACKEND_URL.replace(/^http/, "ws")}/api/ws/chat`;

export default function Chat() {
  const { user, ready } = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const bottomRef = useRef(null);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (!ready || !user) return;
    api.get("/chat/messages").then((r) => setMessages(r.data)).catch(() => {});

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      setMessages((prev) => [...prev, msg]);
    };
    return () => ws.close();
  }, [ready, user]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = (e) => {
    e.preventDefault();
    const t = text.trim();
    if (!t || wsRef.current?.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(JSON.stringify({ text: t }));
    setText("");
  };

  if (ready && !user) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center" data-testid="chat-guest">
        <Users size={56} strokeWidth={2} className="mx-auto mb-4 text-ash" />
        <h1 className="font-display text-4xl uppercase">Join the crew</h1>
        <p className="mt-3 font-body text-ash">Sign in to chat with your peeps in real time.</p>
        <Link to="/login" className="brutal-btn brutal-btn-primary mt-6" data-testid="chat-login-btn">Sign In</Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 md:px-6" data-testid="chat-page">
      <div className="mb-4 flex items-center justify-between border-2 border-ink bg-ink p-5 text-paper" style={{ boxShadow: "6px 6px 0 #FF5C00" }}>
        <div>
          <span className="tag bg-highlighter text-ink">LIVE CHATROOM</span>
          <h1 className="mt-2 font-display text-4xl uppercase leading-none tracking-tight">Chatting With My Peeps</h1>
        </div>
        <span className={`flex items-center gap-2 border-2 border-paper px-3 py-1 font-mono text-xs font-bold ${connected ? "text-highlighter" : "text-sale"}`} data-testid="chat-status">
          {connected ? <Wifi size={16} strokeWidth={2.5} /> : <WifiOff size={16} strokeWidth={2.5} />}
          {connected ? "LIVE" : "OFFLINE"}
        </span>
      </div>

      <div ref={scrollRef} className="h-[55vh] space-y-3 overflow-y-auto border-2 border-ink bg-white p-4" data-testid="chat-messages">
        {messages.length === 0 && (
          <p className="py-10 text-center font-mono text-sm text-ash">No messages yet. Say hey! 👋</p>
        )}
        {messages.map((m, i) => {
          if (m.type === "system") {
            return <div key={i} className="text-center font-mono text-xs uppercase text-ash">— {m.text} —</div>;
          }
          const mine = m.user_id === user?.id;
          return (
            <div key={m.id || i} className={`flex ${mine ? "justify-end" : "justify-start"}`} data-testid="chat-message">
              <div className={`max-w-[75%] border-2 border-ink p-3 ${mine ? "bg-orange text-white" : "bg-paper"}`} style={{ boxShadow: "3px 3px 0 #0A0A0A" }}>
                {!mine && <div className="mb-1 font-heading text-xs font-extrabold uppercase text-electric">{m.name}</div>}
                <div className="font-body text-sm leading-snug">{m.text}</div>
                <div className={`mt-1 font-mono text-[10px] ${mine ? "text-white/70" : "text-ash"}`}>
                  {new Date(m.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={send} className="mt-3 flex gap-3">
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a message..."
          maxLength={500}
          className="brutal-input flex-1"
          data-testid="chat-input"
        />
        <button type="submit" disabled={!connected} className="brutal-btn brutal-btn-primary px-5 disabled:opacity-50" data-testid="chat-send">
          <Send size={18} strokeWidth={2.5} />
        </button>
      </form>
    </div>
  );
}
