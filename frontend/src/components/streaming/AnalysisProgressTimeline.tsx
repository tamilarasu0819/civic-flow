import { useStreamStore } from '../../store/useStreamStore';
import type { StreamStage } from '../../types/stream';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

const STAGES: { id: StreamStage; label: string }[] = [
  { id: 'UPLOADING', label: 'Image Upload' },
  { id: 'ANALYZING_VISION', label: 'Vision Analysis' },
  { id: 'MAPPING_DEPARTMENT', label: 'Department Mapping' },
  { id: 'SYNTHESIZING_TICKET', label: 'Ticket Synthesis' },
];

export function AnalysisProgressTimeline() {
  const { currentStage } = useStreamStore();

  const getStageStatus = (_stageId: StreamStage, currentIndex: number, targetIndex: number) => {
    if (currentIndex > targetIndex) return 'completed';
    if (currentIndex === targetIndex) return 'active';
    return 'pending';
  };

  const currentIndex = STAGES.findIndex(s => s.id === currentStage);
  const effectiveIndex = currentStage === 'COMPLETE' ? STAGES.length : currentIndex;

  return (
    <div className="flex flex-col space-y-4 p-4 bg-card-glass backdrop-blur-md rounded-xl border border-white/10">
      <h3 className="text-white/80 font-semibold text-sm uppercase tracking-wider mb-2">Analysis Pipeline</h3>
      {STAGES.map((stage, index) => {
        const status = getStageStatus(stage.id, effectiveIndex, index);
        
        return (
          <div key={stage.id} className="flex items-center space-x-3">
            <div className="relative flex items-center justify-center w-6 h-6">
              {status === 'completed' && <CheckCircle2 className="w-5 h-5 text-accent-green" />}
              {status === 'active' && (
                <>
                  <Loader2 className="w-5 h-5 text-accent-cyan animate-spin z-10" />
                  <div className="absolute inset-0 bg-accent-cyan/20 blur-md rounded-full animate-pulse" />
                </>
              )}
              {status === 'pending' && <Circle className="w-4 h-4 text-white/20" />}
            </div>
            
            <span className={`text-sm font-medium transition-colors duration-300 ${
              status === 'completed' ? 'text-accent-green/80' :
              status === 'active' ? 'text-accent-cyan text-shadow-glow' :
              'text-white/30'
            }`}>
              {stage.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
