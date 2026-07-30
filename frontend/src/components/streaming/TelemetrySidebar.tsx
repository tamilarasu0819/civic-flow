import { useEffect, useState } from 'react';
import { useStreamStore } from '../../store/useStreamStore';

export function TelemetrySidebar() {
  const { rawTokens, currentStage } = useStreamStore();
  const [tps, setTps] = useState(0); // Tokens per second
  const [latency, setLatency] = useState(0); // Mock latency

  useEffect(() => {
    let lastTokenCount = rawTokens.length;
    
    const interval = setInterval(() => {
      const currentTokenCount = rawTokens.length;
      const newTokens = currentTokenCount - lastTokenCount;
      setTps(newTokens * 2); // multiplied by 2 because interval is 500ms
      lastTokenCount = currentTokenCount;
      
      if (currentStage !== 'IDLE' && currentStage !== 'COMPLETE') {
        setLatency(Math.floor(Math.random() * 40) + 20); // 20-60ms random latency
      } else {
        setLatency(0);
        setTps(0);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [rawTokens.length, currentStage]);

  return (
    <div className="flex flex-col space-y-4 p-4 bg-card-glass backdrop-blur-md rounded-xl border border-white/10 font-mono text-xs text-white/70">
      <div className="border-b border-white/10 pb-2 mb-2">
        <h3 className="text-accent-cyan font-bold tracking-widest uppercase mb-1">Telemetry</h3>
        <p className="text-white/40">Real-time system vitals</p>
      </div>

      <div className="flex justify-between items-center">
        <span>Velocity:</span>
        <span className={`font-bold ${tps > 50 ? 'text-accent-cyan' : 'text-white'}`}>
          {tps} t/s
        </span>
      </div>

      <div className="flex justify-between items-center">
        <span>Latency:</span>
        <span className={`font-bold ${latency > 50 ? 'text-accent-pink' : 'text-accent-green'}`}>
          {latency} ms
        </span>
      </div>

      <div className="flex justify-between items-center">
        <span>Tokens Gen:</span>
        <span className="font-bold text-white">
          {rawTokens.length}
        </span>
      </div>
      
      <div className="mt-4 pt-4 border-t border-white/10">
         <div className="text-[10px] text-white/30 uppercase tracking-widest flex items-center justify-between">
           <span>Model</span>
           <span className="text-accent-purple">Civic-Vision-v2</span>
         </div>
         <div className="text-[10px] text-white/30 uppercase tracking-widest flex items-center justify-between mt-1">
           <span>Engine</span>
           <span className="text-accent-purple">G-Synth</span>
         </div>
      </div>
    </div>
  );
}
