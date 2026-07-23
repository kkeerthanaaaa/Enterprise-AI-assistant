import { Link } from "react-router-dom";
import { Building2, ShieldCheck, Database, Sparkles } from "lucide-react";

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="max-w-6xl mx-auto flex items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-md bg-brand-500 grid place-items-center">
            <Building2 size={18} />
          </div>
          <span className="font-semibold tracking-tight">Enterprise AI Assistant</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm text-slate-300 hover:text-white">Sign in</Link>
          <Link
            to="/register"
            className="text-sm bg-brand-600 hover:bg-brand-700 transition-colors px-4 py-2 rounded-lg font-medium"
          >
            Register your company
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 pt-20 pb-24">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 text-xs font-medium text-brand-300 bg-brand-500/10 border border-brand-500/20 px-3 py-1 rounded-full mb-6">
            <Sparkles size={12} /> Multi-tenant internal AI, not just a PDF chatbot
          </div>
          <h1 className="text-5xl font-bold tracking-tight leading-[1.05]">
            The one place your team asks anything about how work works here.
          </h1>
          <p className="mt-6 text-lg text-slate-400 leading-relaxed">
            Leave balances, approval chains, reimbursement policy, who reports to whom —
            answered instantly, scoped to each employee's role and permissions, grounded in
            your actual documents and HR data. Every company's data stays completely isolated.
          </p>
          <div className="mt-10 flex gap-4">
            <Link
              to="/register"
              className="bg-brand-600 hover:bg-brand-700 transition-colors px-6 py-3 rounded-lg font-medium"
            >
              Get started free
            </Link>
            <Link
              to="/login"
              className="border border-slate-700 hover:border-slate-500 transition-colors px-6 py-3 rounded-lg font-medium"
            >
              Sign in
            </Link>
          </div>
        </div>

        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Feature
            icon={Database}
            title="Structured + unstructured, combined"
            body="Answers blend your policy documents with live HR data — leave balances, org charts, training status — not just document search."
          />
          <Feature
            icon={ShieldCheck}
            title="Role-aware by design"
            body="Employees, managers, HR, and admins each see exactly what their role allows. Company A never sees Company B, ever."
          />
          <Feature
            icon={Sparkles}
            title="Reasons, doesn't just retrieve"
            body="Leave requests are checked against balance, notice period, and policy before the assistant answers — no hallucinated numbers."
          />
        </div>
      </main>
    </div>
  );
}

function Feature({ icon: Icon, title, body }: { icon: any; title: string; body: string }) {
  return (
    <div className="border border-slate-800 rounded-xl p-6 bg-slate-900/40">
      <Icon size={20} className="text-brand-400 mb-4" />
      <h3 className="font-semibold mb-2">{title}</h3>
      <p className="text-sm text-slate-400 leading-relaxed">{body}</p>
    </div>
  );
}
