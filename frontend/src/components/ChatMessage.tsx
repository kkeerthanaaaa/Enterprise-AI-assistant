import ReactMarkdown from "react-markdown";
import { Bot, User, Copy, RotateCcw, FileText } from "lucide-react";
import { ChatMessage as ChatMessageType } from "../types";
import { useState } from "react";
import clsx from "clsx";

export default function ChatMessage({
  message,
  onRegenerate,
  isLast,
}: {
  message: ChatMessageType;
  onRegenerate?: () => void;
  isLast?: boolean;
}) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  function copy() {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className={clsx("flex gap-3 py-4", isUser && "justify-end")}>
      {!isUser && (
        <div className="h-8 w-8 rounded-lg bg-brand-600 grid place-items-center shrink-0 mt-0.5">
          <Bot size={16} className="text-white" />
        </div>
      )}

      <div className={clsx("max-w-2xl", isUser && "order-first")}>
        <div
          className={clsx(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-brand-600 text-white rounded-tr-sm"
              : "bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-800 text-gray-800 dark:text-slate-200 rounded-tl-sm"
          )}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="markdown">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          )}
        </div>

        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {message.citations.map((c, i) => (
              <div
                key={i}
                title={c.snippet}
                className="flex items-center gap-1.5 text-xs bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 border border-brand-100 dark:border-brand-800 rounded-full px-2.5 py-1 max-w-[220px] cursor-help"
              >
                <FileText size={11} className="shrink-0" />
                <span className="truncate">{c.title}</span>
              </div>
            ))}
          </div>
        )}

        {!isUser && (
          <div className="mt-1.5 flex items-center gap-3">
            <button
              onClick={copy}
              className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-slate-300"
            >
              <Copy size={12} /> {copied ? "Copied" : "Copy"}
            </button>
            {isLast && onRegenerate && (
              <button
                onClick={onRegenerate}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-slate-300"
              >
                <RotateCcw size={12} /> Regenerate
              </button>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="h-8 w-8 rounded-lg bg-gray-200 dark:bg-slate-800 grid place-items-center shrink-0 mt-0.5">
          <User size={16} className="text-gray-500" />
        </div>
      )}
    </div>
  );
}
