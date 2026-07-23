import { FormEvent, useEffect, useState } from "react";
import { UploadCloud, FileText, Trash2 } from "lucide-react";
import { api } from "../lib/api";
import { DocumentOut } from "../types";

const DOC_TYPES = [
  "handbook", "hr_policy", "it_policy", "travel_policy", "leave_policy",
  "payroll_policy", "insurance", "benefits", "security_policy", "sop",
  "training_manual", "other",
];

export default function PolicyUpload() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [title, setTitle] = useState("");
  const [docType, setDocType] = useState("hr_policy");
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  function load() {
    api.get("/documents").then((r) => setDocuments(r.data));
  }

  useEffect(load, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setMessage(null);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("title", title);
      form.append("doc_type", docType);
      await api.post("/documents/upload", form, { headers: { "Content-Type": "multipart/form-data" } });
      setMessage("Uploaded. Processing in the background — it will show as Ready shortly.");
      setTitle("");
      setFile(null);
      load();
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function remove(id: string) {
    await api.delete(`/documents/${id}`);
    load();
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-xl font-semibold text-gray-800 dark:text-slate-100">Policies & Documents</h1>
      <p className="text-sm text-gray-400 mt-1">Upload handbooks, SOPs, and policies for the assistant to reference</p>

      <form onSubmit={onSubmit} className="mt-6 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl p-5 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label className="block">
            <span className="text-xs font-medium text-gray-500">Title</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="e.g. Leave Policy v3"
              className="mt-1 w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 rounded-lg px-3 py-2 text-sm"
            />
          </label>
          <label className="block">
            <span className="text-xs font-medium text-gray-500">Document type</span>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="mt-1 w-full bg-gray-50 dark:bg-slate-950 border border-gray-200 dark:border-slate-800 rounded-lg px-3 py-2 text-sm"
            >
              {DOC_TYPES.map((t) => (
                <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
              ))}
            </select>
          </label>
        </div>

        <label className="flex items-center gap-3 border border-dashed border-gray-300 dark:border-slate-700 rounded-lg px-4 py-6 cursor-pointer hover:border-brand-400">
          <UploadCloud size={20} className="text-gray-400" />
          <span className="text-sm text-gray-500">
            {file ? file.name : "Click to choose a PDF, DOCX, TXT, MD, or PPTX file"}
          </span>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.md,.pptx"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </label>

        {message && <p className="text-sm text-brand-600">{message}</p>}

        <button
          disabled={uploading || !file}
          className="bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg"
        >
          {uploading ? "Uploading..." : "Upload document"}
        </button>
      </form>

      <div className="mt-8 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 dark:bg-slate-950 text-gray-500 text-xs">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Title</th>
              <th className="text-left px-4 py-3 font-medium">Type</th>
              <th className="text-left px-4 py-3 font-medium">Version</th>
              <th className="text-left px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {documents.map((d) => (
              <tr key={d.id} className="border-t border-gray-100 dark:border-slate-800">
                <td className="px-4 py-3 font-medium text-gray-800 dark:text-slate-100 flex items-center gap-2">
                  <FileText size={14} className="text-gray-400" /> {d.title}
                </td>
                <td className="px-4 py-3 text-gray-500 capitalize">{d.doc_type.replace(/_/g, " ")}</td>
                <td className="px-4 py-3 text-gray-500">v{d.version}</td>
                <td className="px-4 py-3">
                  <StatusPill status={d.status} />
                </td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => remove(d.id)} className="text-gray-400 hover:text-red-500">
                    <Trash2 size={14} />
                  </button>
                </td>
              </tr>
            ))}
            {documents.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-400">No documents uploaded yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatusPill({ status }: { status: string }) {
  const styles: Record<string, string> = {
    ready: "bg-green-50 text-green-700",
    processing: "bg-amber-50 text-amber-700",
    failed: "bg-red-50 text-red-700",
    archived: "bg-gray-100 text-gray-500",
  };
  return <span className={`text-xs px-2 py-0.5 rounded-full ${styles[status] || "bg-gray-100 text-gray-500"}`}>{status}</span>;
}
