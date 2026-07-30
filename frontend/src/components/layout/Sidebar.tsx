import { Plus, MessageSquare, Settings, User } from 'lucide-react';
import { useState } from 'react';
import { SettingsModal } from './SettingsModal';
import { useStreamStore } from '../../store/useStreamStore';
import { useTicketStore } from '../../store/useTicketStore';

const MOCK_HISTORY = [
  { id: 1, title: 'Drainage Overflow #8942', date: 'Today' },
  { id: 2, title: 'Road Pothole #3102', date: 'Yesterday' },
  { id: 3, title: 'Streetlight Malfunction', date: 'Oct 24, 2026' },
  { id: 4, title: 'Graffiti on Main St', date: 'Oct 20, 2026' },
];

export function Sidebar() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const { resetStore: resetStreamStore } = useStreamStore();
  const { resetTicketStore } = useTicketStore();

  const handleNewAnalysis = () => {
    resetStreamStore();
    resetTicketStore();
  };

  return (
    <>
      <aside className="h-full w-64 flex-shrink-0 flex flex-col bg-obsidian border-r border-slate-800 z-20">
        {/* Header */}
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center space-x-2 mb-6">
            <div className="w-8 h-8 rounded bg-gradient-to-br from-accent-cyan to-accent-purple flex items-center justify-center font-bold text-white shadow-[0_0_15px_rgba(112,0,255,0.4)]">
              CF
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60 tracking-tight">
              CivicFlow AI
            </h1>
          </div>
          
          <button 
            onClick={handleNewAnalysis}
            className="w-full py-2.5 px-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg flex items-center justify-between group transition-colors"
          >
            <span className="text-sm font-medium text-white/80 group-hover:text-white">New Analysis</span>
            <Plus className="w-4 h-4 text-accent-cyan" />
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent p-4 space-y-4">
          <div className="text-xs font-semibold text-white/40 uppercase tracking-wider">
            Recent Reports
          </div>
          
          <div className="space-y-1">
            {MOCK_HISTORY.map((item) => (
              <button 
                key={item.id}
                className="w-full flex flex-col text-left p-2.5 rounded-lg hover:bg-white/5 transition-colors group"
              >
                <div className="flex items-center space-x-2 mb-1">
                  <MessageSquare className="w-3.5 h-3.5 text-white/40 group-hover:text-accent-cyan transition-colors" />
                  <span className="text-sm font-medium text-white/80 group-hover:text-white truncate">
                    {item.title}
                  </span>
                </div>
                <span className="text-[10px] text-white/30 ml-5.5">{item.date}</span>
              </button>
            ))}
          </div>
        </div>

        {/* User Profile & Settings */}
        <div className="p-4 border-t border-white/10 flex flex-col space-y-4 bg-black/20">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-accent-purple/20 border border-accent-purple/50 flex items-center justify-center">
                <User className="w-5 h-5 text-accent-purple" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-bold text-white truncate">Vikram</div>
                <div className="text-[10px] text-accent-cyan uppercase tracking-wider font-semibold border border-accent-cyan/30 bg-accent-cyan/10 rounded px-1.5 py-0.5 inline-block mt-0.5">Verified Citizen</div>
              </div>
            </div>
          </div>
          
          <button 
            onClick={() => setIsSettingsOpen(true)}
            className="w-full flex items-center justify-center space-x-2 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-white/70 transition-colors mt-auto"
          >
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </aside>

      {/* Settings Modal */}
      {isSettingsOpen && <SettingsModal onClose={() => setIsSettingsOpen(false)} />}
    </>
  );
}
