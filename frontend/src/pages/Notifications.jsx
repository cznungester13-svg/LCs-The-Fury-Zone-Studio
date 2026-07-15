import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "@/lib/api";
import { Spinner, EmptyState, Btn } from "@/components/common";
import { Bell, CheckCheck } from "lucide-react";
import { toast } from "sonner";

const KIND_COLOR = { 
  success: "border-green-500", 
  warning: "border-yellow-500", 
  info: "border-blue-500", 
  error: "border-[#FF3B30]" 
};

export default function Notifications() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(false);

  const load = () => {
    api.get("/notifications")
      .then(({ data }) => {
        setData(data || { items: [] });
      })
      .catch((err) => {
        console.error("Failed to load notifications:", err);
        setError(true);
        setData({ items: [] });
      });
  };

  useEffect(() => { 
    load(); 
  }, []);

  const markAll = async () => { 
    try {
      await api.post("/notifications/read-all"); 
      load(); 
    } catch {
      toast.error("Failed to clear notifications");
    }
  };

  const markOne = async (id) => { 
    try {
      await api.post(`/notifications/${id}/read`); 
      load(); 
    } catch {
      // Fail silently or handle quietly to keep UX clean
    }
  };

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <p className="text-[#FF3B30] font-bold uppercase tracking-wider">Could not retrieve alerts.</p>
      </div>
    );
  }

  if (!data) return <Spinner />;

  const notificationItems = data.items || [];

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex justify-between items-center border-b-2 border-black pb-4 mb-8">
        <h1 className="text-4xl font-black uppercase tracking-tighter flex items-center gap-3">
          <Bell /> Alerts
        </h1>
        {notificationItems.length > 0 && (
          <Btn variant="secondary" onClick={markAll} className="!px-3 !py-2 text-sm" data-testid="mark-all-read">
            <CheckCheck size={16} /> Mark all read
          </Btn>
        )}
      </div>

      {notificationItems.length === 0 ? (
        <EmptyState title="No notifications" subtitle="You're all caught up." />
      ) : (
        <div className="space-y-3">
          {notificationItems.map((n) => (
            <div 
              key={n.id} 
              onClick={() => !n.read && markOne(n.id)} 
              className={`border-l-4 ${KIND_COLOR[n.kind] || "border-zinc-400"} border-2 border-black p-4 transition-all duration-150 ${n.read ? "opacity-60 bg-white" : "bg-zinc-50 cursor-pointer shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-0.5"}`} 
              data-testid={`notification-${n.id}`}
            >
              <div className="flex justify-between items-start gap-4">
                <p className="font-bold text-sm sm:text-base">{n.title}</p>
                {!n.read && <span className="w-2.5 h-2.5 bg-[#FF3B30] rounded-full shrink-0 mt-1.5" aria-label="Unread indicator" />}
              </div>
              <p className="text-sm text-zinc-600 mt-1">{n.message}</p>
              {n.link && (
                <Link 
                  to={n.link} 
                  onClick={(e) => e.stopPropagation()} 
                  className="text-xs font-bold uppercase text-[#FF3B30] mt-3 inline-block hover:underline"
                >
                  View →
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
