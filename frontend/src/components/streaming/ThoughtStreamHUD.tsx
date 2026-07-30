import { LiveTerminalView } from './LiveTerminalView';
import { AnalysisProgressTimeline } from './AnalysisProgressTimeline';
import { ConfidenceMeter } from './ConfidenceMeter';
import { TelemetrySidebar } from './TelemetrySidebar';
import { useStreamStore } from '../../store/useStreamStore';
import { BrainCircuit } from 'lucide-react';

export function ThoughtStreamHUD() {
  const { currentStage } = useStreamStore();

  if (currentStage === 'IDLE' || currentStage === 'COMPLETE') return null;

  return (
    <div className="w-full max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-12 gap-6 p-6 h-[80vh]">
      {/* Header spanning full width */}
      <div className="col-span-1 md:col-span-12 flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <BrainCircuit className="w-8 h-8 text-accent-purple animate-pulse" />
          <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-accent-cyan to-accent-purple">
            Civic Engine Stream
          </h2>
        </div>
        <div className="px-4 py-1.5 rounded-full border border-accent-cyan/50 bg-accent-cyan/10 text-accent-cyan text-xs font-mono uppercase tracking-widest animate-pulse">
          Live Analysis
        </div>
      </div>

      {/* Main Terminal Area */}
      <div className="col-span-1 md:col-span-8 h-full min-h-[400px]">
        <LiveTerminalView />
      </div>

      {/* Sidebar Area */}
      <div className="col-span-1 md:col-span-4 flex flex-col space-y-6">
        <AnalysisProgressTimeline />
        <div className="grid grid-cols-2 gap-4">
          <ConfidenceMeter />
          <TelemetrySidebar />
        </div>
      </div>
    </div>
  );
}
