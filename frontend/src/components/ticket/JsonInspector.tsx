import { Code, Terminal } from 'lucide-react';
import { useTicketStore } from '../../store/useTicketStore';

export function JsonInspector() {
  const { visionData, activeTicket, activeJsonTab, setActiveJsonTab } = useTicketStore();

  const dataToDisplay = activeJsonTab === 'vision' ? visionData : activeTicket;
  const jsonString = JSON.stringify(dataToDisplay, null, 2);

  // Simple regex-based syntax highlighting for JSON
  const highlightJson = (json: string) => {
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, (match) => {
      let cls = 'text-accent-cyan';
      if (/^"/.test(match)) {
        if (/:$/.test(match)) {
          cls = 'text-accent-purple'; // Key
        } else {
          cls = 'text-accent-green'; // String value
        }
      } else if (/true|false/.test(match)) {
        cls = 'text-accent-pink'; // Boolean
      } else if (/null/.test(match)) {
        cls = 'text-white/50'; // Null
      }
      return `<span class="${cls}">${match}</span>`;
    });
  };

  return (
    <div className="bg-obsidian border border-accent-cyan/30 rounded-xl overflow-hidden flex flex-col h-[500px]">
      <div className="flex border-b border-accent-cyan/30 bg-white/5">
        <button
          onClick={() => setActiveJsonTab('vision')}
          className={`flex-1 py-3 px-4 flex items-center justify-center space-x-2 text-sm font-medium transition-colors ${
            activeJsonTab === 'vision' ? 'text-accent-cyan border-b-2 border-accent-cyan bg-accent-cyan/10' : 'text-white/50 hover:text-white/80'
          }`}
        >
          <Terminal className="w-4 h-4" />
          <span>Stage 1: Vision JSON</span>
        </button>
        <button
          onClick={() => setActiveJsonTab('ticket')}
          className={`flex-1 py-3 px-4 flex items-center justify-center space-x-2 text-sm font-medium transition-colors ${
            activeJsonTab === 'ticket' ? 'text-accent-purple border-b-2 border-accent-purple bg-accent-purple/10' : 'text-white/50 hover:text-white/80'
          }`}
        >
          <Code className="w-4 h-4" />
          <span>Stage 2: Ticket JSON</span>
        </button>
      </div>
      <div className="flex-1 p-4 overflow-auto scrollbar-thin scrollbar-thumb-accent-cyan/50 scrollbar-track-transparent">
        <pre 
          className="font-mono text-sm whitespace-pre-wrap"
          dangerouslySetInnerHTML={{ __html: highlightJson(jsonString) }}
        />
      </div>
    </div>
  );
}
