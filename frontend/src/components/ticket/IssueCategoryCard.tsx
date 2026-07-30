import { Hash, ServerCrash } from 'lucide-react';
import type { IssueCategoryCardProps } from '../../types/ticket';

export function IssueCategoryCard({ category, infrastructure }: IssueCategoryCardProps) {
  return (
    <div className="p-4 rounded-xl border border-white/10 bg-card-glass backdrop-blur-md flex flex-col space-y-3 relative overflow-hidden group hover:border-accent-cyan/50 transition-colors">
      <div className="absolute top-0 right-0 w-32 h-32 bg-accent-cyan/10 rounded-full blur-3xl -mr-10 -mt-10 group-hover:bg-accent-cyan/20 transition-colors" />
      
      <div className="flex items-center space-x-2 z-10">
        <Hash className="w-4 h-4 text-accent-cyan" />
        <span className="font-semibold text-white/70 text-sm uppercase tracking-wider">Category</span>
      </div>
      
      <div className="text-xl font-bold text-white z-10">
        {category}
      </div>
      
      <div className="flex flex-wrap gap-2 mt-2 z-10">
        {infrastructure.map((item, idx) => (
          <div key={idx} className="flex items-center space-x-1 px-2.5 py-1 bg-white/5 border border-white/10 rounded-md text-xs text-white/60">
            <ServerCrash className="w-3 h-3 text-accent-cyan" />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
