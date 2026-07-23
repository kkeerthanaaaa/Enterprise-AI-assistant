import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Building2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [companySlug, setCompanySlug] = useState("acme");
  const [email, setEmail] = useState("john@acme.com");
  const [password, setPassword] = useState("Password123!");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(companySlug, email, password);
      navigate("/chat");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Invalid company, email, or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 justify-center mb-8">
          <div className="h-9 w-9 rounded-md bg-brand-500 grid place-items-center">
            <Building2 size={18} />
          </div>
          <span className="font-semibold tracking-tight">Enterprise AI Assistant</span>
        </div>

        <form onSubmit={onSubmit} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
          <h1 className="text-lg font-semibold mb-1">Sign in</h1>

          <Field label="Company slug" value={companySlug} onChange={setCompanySlug} placeholder="acme" />
          <Field label="Email" value={email} onChange={setEmail} placeholder="you@company.com" type="email" />
          <Field label="Password" value={password} onChange={setPassword} type="password" />

          {error && <p className="text-sm text-red-400">{error}</p>}

          <button
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 transition-colors py-2.5 rounded-lg font-medium text-sm"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>

          <p className="text-xs text-slate-500 text-center pt-2">
            Demo: acme / john@acme.com / Password123!
          </p>
        </form>

        <p className="text-sm text-slate-400 text-center mt-6">
          New company? <Link to="/register" className="text-brand-400 hover:text-brand-300">Register here</Link>
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
        className="mt-1 w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-600"
      />
    </label>
  );
}
