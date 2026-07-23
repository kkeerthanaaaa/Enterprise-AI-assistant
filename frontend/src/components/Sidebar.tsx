import { NavLink } from "react-router-dom";
import { MessageSquare, LayoutDashboard, Users, FileUp, BarChart3, LogOut, Building2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import clsx from "clsx";

const linkBase =
  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors";

export default function Sidebar() {
  const { user, logout } = useAuth();
  if (!user) return null;

  const items = [
    { to: "/chat", label: "Assistant", icon: MessageSquare, roles: ["employee", "manager", "hr", "admin"] },
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["employee", "manager", "hr", "admin"] },
    { to: "/team", label: "My Team", icon: Users, roles: ["manager", "hr", "admin"] },
    { to: "/policies", label: "Policies", icon: FileUp, roles: ["hr", "admin"] },
    { to: "/analytics", label: "Analytics", icon: BarChart3, roles: ["hr", "admin"] },
  ];

  return (
    <aside className="w-64 shrink-0 h-full bg-slate-950 text-slate-200 flex flex-col border-r border-slate-800">
      <div className="px-5 py-5 flex items-center gap-2 border-b border-slate-800">
        <div className="h-8 w-8 rounded-md bg-brand-500 grid place-items-center">
          <Building2 size={18} className="text-white" />
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight text-white">Enterprise AI</div>
          <div className="text-[11px] text-slate-400 -mt-0.5">Knowledge Assistant</div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {items
          .filter((i) => i.roles.includes(user.role))
          .map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                clsx(
                  linkBase,
                  isActive
                    ? "bg-brand-600/20 text-white border border-brand-600/40"
                    : "text-slate-400 hover:text-white hover:bg-slate-900"
                )
              }
            >
              <item.icon size={17} />
              {item.label}
            </NavLink>
          ))}
      </nav>

      <div className="px-4 py-4 border-t border-slate-800">
        <div className="text-sm text-white font-medium truncate">{user.full_name}</div>
        <div className="text-xs text-slate-400 capitalize">{user.role}</div>
        <button
          onClick={logout}
          className="mt-3 flex items-center gap-2 text-xs text-slate-400 hover:text-red-400 transition-colors"
        >
          <LogOut size={14} /> Sign out
        </button>
      </div>
    </aside>
  );
}
