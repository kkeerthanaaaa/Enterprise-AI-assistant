import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Building2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { registerCompany } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    company_name: "",
    company_slug: "",
    admin_full_name: "",
    admin_email: "",
    admin_password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function set(key: keyof typeof form, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await registerCompany(form);
      navigate("/chat");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not register company");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <div className="h-9 w-9 rounded-md bg-brand-500 grid place-items-center">
            <Building2 size={18} />
          </div>
          <span className="font-semibold tracking-tight">Enterprise AI Assistant</span>
        </div>

        <form onSubmit={onSubmit} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
          <h1 className="text-lg font-semibold mb-1">Register your company</h1>
          <p className="text-xs text-slate-500 mb-2">
            This creates an isolated tenant and your first Admin account.
          </p>

          <Field label="Company name" value={form.company_name} onChange={(v) => set("company_name", v)} placeholder="Acme Corp" />
          <Field
            label="Company slug (URL-safe, unique)"
            value={form.company_slug}
            onChange={(v) => set("company_slug", v.toLowerCase().replace(/[^a-z0-9-]/g, ""))}
            placeholder="acme"
          />
          <Field label="Your full name" value={form.admin_full_name} onChange={(v) => set("admin_full_name", v)} placeholder="Alex Admin" />
          <Field label="Your email" value={form.admin_email} onChange={(v) => set("admin_email", v)} type="email" placeholder="admin@acme.com" />
          <Field label="Password" value={form.admin_password} onChange={(v) => set("admin_password", v)} type="password" />

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 transition-colors py-2.5 rounded-lg font-medium text-sm"
          >
            {loading ? "Creating..." : "Create company"}
          </button>
        </form>

        <p className="text-sm text-slate-400 text-center mt-6">
          Already registered? <Link to="/login" className="text-brand-400 hover:text-brand-300">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <label className="block">
      <span className="text-xs font-medium text-slate-400">{label}</span>
      <input
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        required
        minLength={type === "password" ? 8 : undefined}
        className="mt-1 w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-600"
      />
    </label>
  );
}
