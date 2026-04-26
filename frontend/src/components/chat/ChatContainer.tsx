import { useState } from "react";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import type { Message } from "./types";
import { toast } from "@/hooks/use-toast";

const API_URL = "http://localhost:8000/query";

export const ChatContainer = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (question: string) => {
    const userMsg: Message = { role: "user", content: question };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const data = await res.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer ?? "No answer returned.",
        sources: Array.isArray(data.sources) ? data.sources : undefined,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unknown error";
      toast({
        title: "Could not reach the assistant",
        description: message,
        variant: "destructive",
      });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry — I couldn't reach the knowledge service. Please check that the backend is running and try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex-1 overflow-y-auto">
        <MessageList messages={messages} isLoading={isLoading} />
      </div>
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
};