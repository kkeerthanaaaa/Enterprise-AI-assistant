import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { EmployeeOut } from "../types";

export default function Team() {
  const [team, setTeam] = useState<EmployeeOut[]>([]);

  useEffect(() => {
    api.get("/employees/team").then((r) => setTeam(r.data));
  }, []);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-800 dark:text-slate-100">My Team</h1>
      <p className="text-sm text-gray-400 mt-1">Your direct reports</p>

      <div className="mt-6 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-slate-950 text-gray-500 text-xs">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Name</th>
              <th className="text-left px-4 py-3 font-medium">Designation</th>
              <th className="text-left px-4 py-3 font-medium">Code</th>
              <th className="text-left px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {team.map((t) => (
              <tr key={t.id} className="border-t border-gray-100 dark:border-slate-800">
                <td className="px-4 py-3 font-medium text-gray-800 dark:text-slate-100">{t.full_name}</td>
                <td className="px-4 py-3 text-gray-500">{t.designation || "—"}</td>
                <td className="px-4 py-3 text-gray-500">{t.employee_code}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${t.is_active ? "bg-green-50 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                    {t.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
              </tr>
            ))}
            {team.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-gray-400">No direct reports yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
