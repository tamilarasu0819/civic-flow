import { AlertTriangle, Info, AlertCircle, ShieldAlert, Sparkles } from 'lucide-react';
import type { SeverityCardProps } from '../../types/ticket';
import { useTicketStore } from '../../store/useTicketStore';

export function SeverityCard({ severity, confidence }: SeverityCardProps) {
  const { modifiedFields } = useTicketStore();
  const isModified = modifiedFields.includes('severity');

  let colorClass = 'text-white border-white/20 bg-white/5';
  let Icon = Info;
  let shadowClass = '';

  switch (severity) {
    case 'Critical':
      colorClass = 'text-accent-pink border-accent-pink bg-accent-pink/10';
      shadowClass = 'drop-shadow-[0_0_8px_rgba(255,0,85,0.6)]';
      Icon = ShieldAlert;
      break;
    case 'High':
      colorClass = 'text-accent-purple border-accent-purple bg-accent-purple/10';
      shadowClass = 'drop-shadow-[0_0_8px_rgba(112,0,255,0.6)]';
      Icon = AlertTriangle;
      break;
    case 'Medium':
      colorClass = 'text-accent-cyan border-accent-cyan bg-accent-cyan/10';
      shadowClass = 'drop-shadow-[0_0_8px_rgba(0,240,255,0.6)]';
      Icon = AlertCircle;
      break;
    case 'Low':
      colorClass = 'text-accent-green border-accent-green bg-accent-green/10';
      shadowClass = 'drop-shadow-[0_0_8px_rgba(0,255,102,0.6)]';
      Icon = Info;
      break;
  }

  return (
    <div className={`p-4 rounded-xl border flex flex-col space-y-3 ${colorClass} ${shadowClass} backdrop-blur-md transition-all ${isModified ? 'ring-2 ring-current' : ''}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className="w-5 h-5" />
          <span className="font-bold tracking-wider uppercase text-sm">Severity</span>
          {isModified && (
            <span className="inline-flex items-center space-x-1 text-[10px] font-bold bg-current text-obsidian px-2 py-0.5 rounded-full animate-pulse">
              <Sparkles className="w-2.5 h-2.5" />
              <span>Customized</span>
            </span>
          )}
        </div>
        <span className="text-xs font-mono opacity-80">AI Confidence: {confidence.toFixed(1)}%</span>
      </div>
      
      <div className="text-2xl font-black uppercase tracking-widest">
        {severity}
      </div>
      
      <div className="w-full h-1.5 bg-black/40 rounded-full overflow-hidden">
        <div 
          className="h-full bg-current transition-all duration-1000"
          style={{ width: `${confidence}%` }}
        />
      </div>
    </div>
  );
}
