import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../lib/api";
import { Btn } from "../components/common";

export default function Community() {
  const { user, isAdmin } = useAuth();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  // Poll for messages every 3 seconds
  useEffect(() => {
    const fetchMessages = () => {
      api.get("/chat/messages").then(({ data }) => setMessages(data)).catch(() => {});
    };
    fetchMessages();
    const interval = setInterval(fetchMessages, 3000);
    return () => clearInterval(interval);
  }, []);

  const postMessage = async () => {
    if (!text.trim()) return;
    await api.post("/chat/messages", { text });
    setText("");
  };

  const deleteMessage = async (id) => {
    if (!isAdmin) return;
    await api.delete(`/chat/messages/${id}`);
    setMessages(messages.filter((m) => m.id !== id));
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-black uppercase tracking-tighter mb-8">Chatting with my girls!</h1>
      
      {/* Message Feed */}
      <div className="space-y-4 mb-8">
        {messages.map((m) => (
          <div key={m.id} className="border-2 border-black p-4 flex justify-between items-start">
            <div>
              <p className="font-bold text-sm uppercase">{m.user_name}</p>
              <p className="text-zinc-700">{m.text}</p>
            </div>
            {isAdmin && (
              <button 
                onClick={() => deleteMessage(m.id)} 
                className="text-red-600 font-bold hover:underline uppercase text-xs"
              >
                Delete
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Input Area */}
      {user ? (
        <div className="flex gap-2">
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="flex-1 border-2 border-black p-2 outline-none"
            placeholder="Type your message..."
          />
          <Btn onClick={postMessage}>Send</Btn>
        </div>
      ) : (
        <div className="border-2 border-dashed border-black p-6 text-center">
          <p className="font-bold">Login to join the conversation!</p>
        </div>
      )}
    </div>
  );
}
