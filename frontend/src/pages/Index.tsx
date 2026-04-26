import { Header } from "@/components/chat/Header";
import { ChatContainer } from "@/components/chat/ChatContainer";

const Index = () => {
  return (
    <div className="flex h-screen flex-col bg-background">
      <Header />
      <main className="flex flex-1 flex-col overflow-hidden">
        <ChatContainer />
      </main>
    </div>
  );
};

export default Index;
