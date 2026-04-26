import { ArrowUp } from "lucide-react";
import { useRef, useState, type KeyboardEvent } from "react";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export const ChatInput = ({ onSend, disabled }: ChatInputProps) => {
  const [value, setValue] = useState("");
  const taRef = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (taRef.current) taRef.current.style.height = "auto";
  };

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  const autoResize = (el: HTMLTextAreaElement) => {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  };

  return (
    <div className="sticky bottom-0 z-10 border-t border-border bg-gradient-to-t from-background via-background to-background/80 backdrop-blur">
      <div className="mx-auto max-w-4xl px-4 py-3 sm:px-6 sm:py-4">
        <div className="flex items-end gap-2 rounded-2xl border border-border bg-surface px-3 py-2 shadow-sm focus-within:border-primary/40 focus-within:ring-2 focus-within:ring-primary/15 transition">
          <textarea
            ref={taRef}
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              autoResize(e.target);
            }}
            onKeyDown={handleKey}
            rows={1}
            placeholder="Ask a question about LiDAR annotation rules..."
            className="flex-1 resize-none bg-transparent py-1.5 text-[15px] leading-relaxed text-foreground placeholder:text-muted-foreground focus:outline-none"
          />
          <button
            onClick={submit}
            disabled={disabled || !value.trim()}
            aria-label="Send message"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground transition hover:bg-[hsl(var(--primary-hover))] disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-2 text-center text-[11px] text-muted-foreground">
          Press Enter to send · Shift + Enter for new line
        </p>
      </div>
    </div>
  );
};