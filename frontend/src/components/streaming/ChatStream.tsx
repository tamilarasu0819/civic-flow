import { useStreamStore } from '../../store/useStreamStore';
import { User, ShieldAlert } from 'lucide-react';
import { useEffect, useRef } from 'react';

export function ChatStream() {
  const { messages } = useStreamStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-4 space-y-6">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
          <div className={`flex items-start max-w-[80%] space-x-3 ${msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
            
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border ${
              msg.sender === 'user' 
                ? 'bg-accent-purple/20 border-accent-purple/50' 
                : 'bg-accent-cyan/10 border-accent-cyan/30 shadow-[0_0_10px_rgba(0,240,255,0.2)]'
            }`}>
              {msg.sender === 'user' 
                ? <User className="w-4 h-4 text-accent-purple" /> 
                : <ShieldAlert className="w-4 h-4 text-accent-cyan" />}
            </div>

            {/* Bubble */}
            <div className={`p-4 rounded-2xl ${
              msg.sender === 'user'
                ? 'bg-accent-purple/10 border border-accent-purple/30 text-white rounded-tr-sm'
                : 'bg-card-glass border border-accent-cyan/20 text-white/90 rounded-tl-sm'
            }`}>
              {msg.isTyping ? (
                <div className="flex items-center space-x-1.5 h-6">
                  <span className="w-1.5 h-1.5 bg-accent-cyan rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-accent-cyan rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-accent-cyan rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              ) : (
                <p className="text-sm whitespace-pre-wrap leading-relaxed">
                  {msg.content}
                </p>
              )}
            </div>

          </div>
        </div>
      ))}
      <div ref={bottomRef} className="h-4" />
    </div>
  );
}
