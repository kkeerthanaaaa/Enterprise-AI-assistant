import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function Analytics() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api.get("/analytics/overview").then((r) => setData(r.data));
  }, []);

  if (!data) return <div className="p-8 text-sm text-gray-400">Loading...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-800 dark:text-slate-100">Organization Analytics</h1>
      <p className="text-sm text-gray-400 mt-1">Company-wide snapshot</p>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Stat label="Total employees" value={data.total_employees} />
        <Stat label="Pending leave requests" value={data.pending_leave_requests} />
        <Stat label="Active documents" value={data.total_active_documents} />
      </div>

      <div className="mt-8 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-gray-700 dark:text-slate-200 mb-4">Headcount by role</h2>
        <div className="space-y-3">
          {Object.entries(data.headcount_by_role || {}).map(([role, count]: any) => (
            <div key={role} className="flex items-center gap-3">
              <span className="w-20 text-xs capitalize text-gray-500">{role}</span>
              <div className="flex-1 h-2 bg-gray-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-brand-500"
                  style={{ width: `${Math.min(100, (count / data.total_employees) * 100)}%` }}
                />
              </div>
              <span className="text-xs text-gray-500 w-6 text-right">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl p-5">
      <div className="text-2xl font-semibold text-gray-800 dark:text-slate-100">{value}</div>
      <div className="text-xs text-gray-400 mt-1">{label}</div>
    </div>
  );
}
