import { Paperclip, Send, Loader2 } from 'lucide-react';
import { useRef, useState } from 'react';
import { useAIStream } from '../../hooks/useAIStream';
import { useStreamStore } from '../../store/useStreamStore';
import { useTicketStore } from '../../store/useTicketStore';

const QUICK_ACTIONS = [
  "Change location to Jubilee Hills Road No. 36",
  "Set severity to Critical",
  "Route to Water Supply & Sewerage",
  "Generate Incident PDF"
];

export function ChatInputBox() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { uploadAndStartStream } = useAIStream();
  const { addMessage, updateMessage } = useStreamStore();
  const { activeTicket, updateActiveTicket, isCustomizing, setCustomizing } = useTicketStore();
  const [text, setText] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      uploadAndStartStream(e.target.files[0]);
    }
  };

  const handleSend = async () => {
    const userPrompt = text.trim();
    if (!userPrompt || isCustomizing) return;
    
    const userMsgId = `msg-${Date.now()}`;
    addMessage({ id: userMsgId, sender: 'user', content: userPrompt });
    setText('');

    const aiMsgId = `msg-${Date.now() + 1}`;
    addMessage({ id: aiMsgId, sender: 'ai', content: '', isTyping: true });

    if (activeTicket) {
      setCustomizing(true);
      try {
        const response = await fetch('/api/v1/customize-ticket', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ticket: activeTicket,
            user_prompt: userPrompt
          })
        });

        if (!response.ok) {
          throw new Error(`Customization failed: ${response.statusText}`);
        }

        const data = await response.json();
        
        if (data.updated_ticket) {
          updateActiveTicket(data.updated_ticket, data.changed_fields || []);
          
          const summaryText = data.summary_of_changes || "Updated document based on your request.";
          updateMessage(aiMsgId, {
            isTyping: false,
            content: `I've updated the report document for you! 📝\n\n**Changes applied:** ${summaryText}`
          });
        } else {
          updateMessage(aiMsgId, {
            isTyping: false,
            content: "I received your request, but was unable to apply modifications to the document."
          });
        }
      } catch (err: any) {
        console.error("Document customization error:", err);
        updateMessage(aiMsgId, {
          isTyping: false,
          content: `Failed to update document: ${err.message || 'Unknown error'}`
        });
      } finally {
        setCustomizing(false);
      }
    } else {
      setTimeout(() => {
        updateMessage(aiMsgId, { 
          isTyping: false, 
          content: "Acknowledged. Please attach an image of the civic issue first so I can analyze it and generate a document to customize." 
        });
      }, 1000);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSend();
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Quick Actions */}
        <div className="flex flex-wrap gap-2 mb-3 px-2">
          {QUICK_ACTIONS.map(action => (
            <button 
              key={action}
              disabled={isCustomizing}
              onClick={() => setText(action)}
              className="text-xs font-medium bg-white/5 hover:bg-accent-cyan/10 border border-white/10 hover:border-accent-cyan/30 text-white/70 hover:text-accent-cyan rounded-full px-3 py-1.5 transition-all disabled:opacity-50 disabled:pointer-events-none"
            >
              {action}
            </button>
          ))}
        </div>

        <div className={`relative flex items-center bg-card-glass backdrop-blur-xl border ${isCustomizing ? 'border-accent-purple/80 shadow-[0_0_20px_rgba(168,85,247,0.3)]' : 'border-white/20'} rounded-2xl shadow-2xl overflow-hidden focus-within:border-accent-cyan/50 transition-all`}>
          
          {/* Hidden file input */}
          <input 
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            className="hidden"
          />

          {/* Attachment Button */}
          <button 
            disabled={isCustomizing}
            onClick={() => fileInputRef.current?.click()}
            className="pl-4 pr-3 py-4 text-white/50 hover:text-accent-cyan transition-colors disabled:opacity-30"
            title="Attach infrastructure image"
          >
            <Paperclip className="w-5 h-5" />
          </button>
          
          {/* Text Input */}
          <input 
            type="text" 
            value={text}
            disabled={isCustomizing}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isCustomizing ? "Groq AI is updating your document..." : "Describe the civic issue or request document changes (e.g. 'Change location to...')..."} 
            className="flex-1 bg-transparent border-none outline-none text-white placeholder:text-white/40 text-sm py-4 disabled:opacity-60"
          />
          
          {/* Send Button */}
          <button 
            disabled={isCustomizing || !text.trim()}
            onClick={handleSend}
            className="mr-3 ml-2 p-2 bg-accent-cyan/10 hover:bg-accent-cyan text-accent-cyan hover:text-obsidian rounded-xl transition-all duration-300 group shadow-[0_0_15px_rgba(0,240,255,0.2)] hover:shadow-[0_0_20px_rgba(0,240,255,0.6)] disabled:opacity-40 disabled:pointer-events-none"
          >
            {isCustomizing ? (
              <Loader2 className="w-4 h-4 text-accent-purple animate-spin" />
            ) : (
              <Send className="w-4 h-4 transform group-hover:translate-x-0.5 transition-transform" />
            )}
          </button>
      </div>
    </div>
  );
}

