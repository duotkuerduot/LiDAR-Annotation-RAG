export const TypingIndicator = () => {
  return (
    <div className="flex animate-message-in justify-start">
      <div className="flex items-center gap-2 rounded-2xl rounded-bl-md bg-assistant-bubble px-4 py-3">
        <span className="text-sm text-muted-foreground">Thinking</span>
        <span className="flex gap-1">
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
        </span>
      </div>
    </div>
  );
};