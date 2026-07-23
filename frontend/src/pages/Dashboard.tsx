import { useEffect, useState } from "react";
import { CalendarDays, Users, GraduationCap, TrendingUp } from "lucide-react";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { LeaveBalance } from "../types";

export default function Dashboard() {
  const { user } = useAuth();
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [teamCount, setTeamCount] = useState<number | null>(null);
  const [overview, setOverview] = useState<any>(null);

  useEffect(() => {
    api.get("/leave/balance").then((r) => setBalances(r.data)).catch(() => {});

    if (user && ["manager", "hr", "admin"].includes(user.role)) {
      api.get("/employees/team").then((r) => setTeamCount(r.data.length)).catch(() => {});
    }
    if (user && ["hr", "admin"].includes(user.role)) {
      api.get("/analytics/overview").then((r) => setOverview(r.data)).catch(() => {});
    }
  }, [user]);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-800 dark:text-slate-100">
        Welcome back, {user?.full_name?.split(" ")[0]}
      </h1>
      <p className="text-sm text-gray-400 mt-1 capitalize">{user?.role} dashboard</p>

      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {balances.map((b) => (
          <Card
            key={b.leave_type}
            icon={CalendarDays}
            title={`${capitalize(b.leave_type)} leave`}
            value={`${b.remaining_days} / ${b.entitled_days}`}
            sub="days remaining"
          />
        ))}

        {teamCount !== null && (
          <Card icon={Users} title="Direct reports" value={String(teamCount)} sub="people on your team" />
        )}

        {overview && (
          <>
            <Card icon={Users} title="Total employees" value={String(overview.total_employees)} sub="company-wide" />
            <Card icon={TrendingUp} title="Pending leave requests" value={String(overview.pending_leave_requests)} sub="awaiting decision" />
            <Card icon={GraduationCap} title="Active documents" value={String(overview.total_active_documents)} sub="policies & SOPs" />
          </>
        )}
      </div>

      {balances.length === 0 && !overview && (
        <p className="text-sm text-gray-400 mt-6">No data yet — head to the Assistant tab to ask a question.</p>
      )}
    </div>
  );
}

function capitalize(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function Card({ icon: Icon, title, value, sub }: { icon: any; title: string; value: string; sub: string }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl p-5">
      <div className="flex items-center gap-2 text-gray-400">
        <Icon size={16} />
        <span className="text-xs font-medium">{title}</span>
      </div>
      <div className="mt-3 text-2xl font-semibold text-gray-800 dark:text-slate-100">{value}</div>
      <div className="text-xs text-gray-400 mt-0.5">{sub}</div>
    </div>
  );
}
