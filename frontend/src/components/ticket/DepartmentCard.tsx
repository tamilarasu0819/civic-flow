import { Building2, Network, Sparkles } from 'lucide-react';
import type { DepartmentCardProps } from '../../types/ticket';
import { useTicketStore } from '../../store/useTicketStore';

export function DepartmentCard({ department }: DepartmentCardProps) {
  const { modifiedFields } = useTicketStore();
  const isModified = modifiedFields.includes('department');

  return (
    <div className={`p-4 rounded-xl border ${isModified ? 'border-accent-purple bg-accent-purple/10 shadow-[0_0_15px_rgba(168,85,247,0.3)]' : 'border-white/10 bg-card-glass'} backdrop-blur-md flex flex-col space-y-3 relative overflow-hidden group transition-all`}>
      <div className="absolute top-0 right-0 w-32 h-32 bg-accent-purple/10 rounded-full blur-3xl -mr-10 -mt-10 group-hover:bg-accent-purple/20 transition-colors" />
      
      <div className="flex items-center justify-between z-10">
        <div className="flex items-center space-x-2">
          <Building2 className="w-4 h-4 text-accent-purple" />
          <span className="font-semibold text-white/70 text-sm uppercase tracking-wider">Routed Department</span>
        </div>
        {isModified && (
          <span className="inline-flex items-center space-x-1 text-[10px] font-bold bg-accent-purple text-white px-2 py-0.5 rounded-full animate-pulse">
            <Sparkles className="w-2.5 h-2.5" />
            <span>Updated</span>
          </span>
        )}
      </div>
      
      <div className="text-xl font-bold text-white z-10">
        {department}
      </div>
      
      <div className="flex items-center space-x-2 text-xs text-accent-purple/80 z-10 bg-accent-purple/10 w-max px-2 py-1 rounded-md border border-accent-purple/20 mt-auto">
        <Network className="w-3 h-3" />
        <span>{isModified ? 'Updated via Groq AI Chat' : 'Auto-mapped via logic engine'}</span>
      </div>
    </div>
  );
}
