import { useStreamStore } from '../../store/useStreamStore';

export function ConfidenceMeter() {
  const { confidenceScore } = useStreamStore();

  const radius = 36;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (confidenceScore / 100) * circumference;

  let colorClass = 'text-accent-cyan';
  let shadowColor = 'drop-shadow-[0_0_8px_rgba(0,240,255,0.8)]';
  if (confidenceScore > 85) {
    colorClass = 'text-accent-green';
    shadowColor = 'drop-shadow-[0_0_8px_rgba(0,255,102,0.8)]';
  } else if (confidenceScore < 50) {
    colorClass = 'text-accent-pink';
    shadowColor = 'drop-shadow-[0_0_8px_rgba(255,0,85,0.8)]';
  }

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-card-glass backdrop-blur-md rounded-xl border border-white/10">
      <h3 className="text-white/80 font-semibold text-xs uppercase tracking-wider mb-4">AI Confidence</h3>
      
      <div className="relative flex items-center justify-center w-24 h-24">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            className="text-white/10 stroke-current"
            strokeWidth="8"
            cx="50"
            cy="50"
            r={radius}
            fill="transparent"
          />
          <circle
            className={`${colorClass} stroke-current transition-all duration-1000 ease-out`}
            strokeWidth="8"
            strokeLinecap="round"
            cx="50"
            cy="50"
            r={radius}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ filter: shadowColor.replace('drop-shadow', 'drop-shadow') }} // Custom inline style if needed, but Tailwind handles it via class
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center flex-col">
          <span className={`text-xl font-bold ${colorClass} ${shadowColor}`}>
            {confidenceScore.toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
}
