import { FormEvent, useRef, useState } from "react";
import { Send, Sparkles, Plus } from "lucide-react";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { ChatMessage as ChatMessageType } from "../types";
import ChatMessage from "../components/ChatMessage";

const PROMPTS: Record<string, string[]> = {
  employee: [
    "How many annual leaves do I have left?",
    "What is our reimbursement policy?",
    "Who is my reporting manager?",
    "How do I apply for WFH?",
  ],
  manager: [
    "Who reports to me?",
    "Can I approve John's leave?",
    "Which employees are on leave next week?",
    "What is our reimbursement policy?",
  ],
  hr: [
    "Show employees whose probation ends this month.",
    "Which employees have not completed mandatory training?",
    "What is our leave policy for maternity leave?",
    "Who approves maternity leave?",
  ],
  admin: [
    "Show employees whose probation ends this month.",
    "What is our reimbursement policy?",
    "Who reports to me?",
    "How do I apply for WFH?",
  ],
};

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const suggestions = PROMPTS[user?.role || "employee"];

  async function send(text?: string) {
    const content = (text ?? input).trim();
    if (!content || loading) return;

    setInput("");
    setMessages((m) => [...m, { role: "user", content }]);
    setLoading(true);

    try {
      const res = await api.post("/chat", { message: content, conversation_id: conversationId });
      setConversationId(res.data.conversation_id);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.data.answer, citations: res.data.citations },
      ]);
    } catch (err: any) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "Sorry, something went wrong reaching the assistant. " +
            (err?.response?.data?.detail || ""),
        },
      ]);
    } finally {
      setLoading(false);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    send();
  }

  function regenerate() {
    const lastUser = [...messages].reverse().find((m) => m.role === "user");
    if (lastUser) send(lastUser.content);
  }

  function newChat() {
    setMessages([]);
    setConversationId(null);
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-slate-800">
        <div>
          <h1 className="text-sm font-semibold text-gray-800 dark:text-slate-100">Assistant</h1>
          <p className="text-xs text-gray-400">Grounded in your company's policies and HR data</p>
        </div>
        <button
          onClick={newChat}
          className="flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-800 dark:text-slate-400 dark:hover:text-white border border-gray-200 dark:border-slate-800 rounded-lg px-3 py-1.5"
        >
          <Plus size={13} /> New chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6">
        <div className="max-w-3xl mx-auto">
          {messages.length === 0 && (
            <div className="pt-16 text-center">
              <div className="h-12 w-12 rounded-2xl bg-brand-600 grid place-items-center mx-auto mb-4">
                <Sparkles size={22} className="text-white" />
              </div>
              <h2 className="text-lg font-semibold text-gray-800 dark:text-slate-100">
                Hi {user?.full_name?.split(" ")[0]}, what do you need to know?
              </h2>
              <p className="text-sm text-gray-400 mt-1">Try one of these to get started</p>

              <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl mx-auto">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="text-left text-sm bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 hover:border-brand-400 dark:hover:border-brand-600 rounded-xl px-4 py-3 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <ChatMessage
              key={i}
              message={m}
              isLast={i === messages.length - 1 && m.role === "assistant"}
              onRegenerate={regenerate}
            />
          ))}

          {loading && (
            <div className="flex gap-3 py-4">
              <div className="h-8 w-8 rounded-lg bg-brand-600 grid place-items-center shrink-0">
                <Sparkles size={16} className="text-white animate-pulse" />
              </div>
              <div className="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.3s]" />
                  <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:-0.15s]" />
                  <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce" />
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      <div className="px-6 py-4 border-t border-gray-200 dark:border-slate-800">
        <form onSubmit={onSubmit} className="max-w-3xl mx-auto flex items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            rows={1}
            placeholder="Ask about policies, leave, benefits, or anything company-related..."
            className="flex-1 resize-none bg-gray-100 dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-600 max-h-32"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="h-11 w-11 shrink-0 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-40 grid place-items-center transition-colors"
          >
            <Send size={16} className="text-white" />
          </button>
        </form>
      </div>
    </div>
  );
}
