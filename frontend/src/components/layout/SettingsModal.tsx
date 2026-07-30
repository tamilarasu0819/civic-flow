import { X, Server, Activity, Info, Palette } from 'lucide-react';
import { useEffect } from 'react';
import { useStreamStore } from '../../store/useStreamStore';

interface SettingsModalProps {
  onClose: () => void;
}

const THEMES = [
  { id: 'cyan', name: 'Cyber Obsidian' },
  { id: 'amber', name: 'Solar Ember' },
  { id: 'emerald', name: 'Emerald Grid' },
  { id: 'midnight', name: 'Deep Midnight' },
  { id: 'minimal', name: 'Monochrome Minimal' }
];

export function SettingsModal({ onClose }: SettingsModalProps) {
  const { autoScrollEnabled, setAutoScrollEnabled, activeTheme, setTheme } = useStreamStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="bg-obsidian border border-white/10 rounded-xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5">
          <h2 className="text-lg font-bold text-white">System Settings</h2>
          <button 
            onClick={onClose}
            className="p-1 text-white/50 hover:text-white rounded-md hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-8 flex-1 overflow-y-auto">
          {/* Section: API */}
          <section className="space-y-4">
            <div className="flex items-center space-x-2 text-accent-cyan">
              <Server className="w-4 h-4" />
              <h3 className="font-semibold text-sm uppercase tracking-widest">API Configuration</h3>
            </div>
            <div className="space-y-2">
              <label className="block text-xs font-medium text-white/60">Live Stream Endpoint</label>
              <input 
                type="text" 
                defaultValue="/api/v1/analyze-live" 
                className="w-full bg-black/40 border border-white/10 rounded-md p-2 text-sm text-white/90 focus:border-accent-cyan outline-none font-mono"
              />
            </div>
          </section>

          {/* Section: Stream Settings */}
          <section className="space-y-4">
            <div className="flex items-center space-x-2 text-accent-purple">
              <Activity className="w-4 h-4" />
              <h3 className="font-semibold text-sm uppercase tracking-widest">Stream Settings</h3>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-white/5 border border-white/5 rounded-lg">
              <div>
                <div className="text-sm font-medium text-white">Auto-scroll Terminal</div>
                <div className="text-xs text-white/50">Automatically pin to bottom during live inference</div>
              </div>
              <button 
                onClick={() => setAutoScrollEnabled(!autoScrollEnabled)}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${autoScrollEnabled ? 'bg-accent-purple' : 'bg-white/20'}`}
              >
                <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${autoScrollEnabled ? 'translate-x-5' : 'translate-x-1'}`} />
              </button>
            </div>
          </section>

          {/* Section: UI Themes */}
          <section className="space-y-4">
            <div className="flex items-center space-x-2 text-accent-cyan">
              <Palette className="w-4 h-4" />
              <h3 className="font-semibold text-sm uppercase tracking-widest">Interface Theme</h3>
            </div>
            
            <div className="grid grid-cols-1 gap-2">
              {THEMES.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => setTheme(theme.id)}
                  className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
                    activeTheme === theme.id 
                      ? 'bg-accent-cyan/10 border-accent-cyan text-white shadow-[0_0_10px_rgba(0,240,255,0.2)]' 
                      : 'bg-white/5 border-white/5 text-white/60 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <span className="text-sm font-medium">{theme.name}</span>
                  {activeTheme === theme.id && (
                    <span className="w-2 h-2 rounded-full bg-accent-cyan shadow-[0_0_8px_rgba(0,240,255,0.8)]" />
                  )}
                </button>
              ))}
            </div>
          </section>

          {/* Section: System Info */}
          <section className="space-y-4">
            <div className="flex items-center space-x-2 text-accent-green">
              <Info className="w-4 h-4" />
              <h3 className="font-semibold text-sm uppercase tracking-widest">System Info</h3>
            </div>
            <div className="p-4 bg-white/5 border border-white/5 rounded-lg space-y-2 text-sm text-white/70">
              <div className="flex justify-between">
                <span>Model Engine:</span>
                <span className="font-mono text-accent-green">Gemma 4 Vision</span>
              </div>
              <div className="flex justify-between">
                <span>UI Version:</span>
                <span className="font-mono">v1.0.0-beta</span>
              </div>
              <div className="flex justify-between">
                <span>Telemetry Status:</span>
                <span className="font-mono text-accent-green">Active</span>
              </div>
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 bg-white/5 flex justify-end">
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-accent-cyan text-obsidian font-semibold rounded-lg hover:bg-accent-cyan/90 transition-colors shadow-[0_0_15px_rgba(0,240,255,0.3)] hover:shadow-[0_0_25px_rgba(0,240,255,0.5)]"
          >
            Save & Close
          </button>
        </div>
      </div>
    </div>
  );
}
