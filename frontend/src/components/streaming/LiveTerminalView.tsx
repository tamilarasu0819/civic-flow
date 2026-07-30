import { useEffect, useRef, useState } from 'react';
import { useStreamStore } from '../../store/useStreamStore';
import { TokenStreamDisplay } from './TokenStreamDisplay';

export function LiveTerminalView() {
  const { rawTokens, autoScrollEnabled, setAutoScrollEnabled, logs } = useStreamStore();
  const containerRef = useRef<HTMLDivElement>(null);
  const [isUserScrolling, setIsUserScrolling] = useState(false);

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 10;
    if (!isAtBottom) {
      if (autoScrollEnabled) setAutoScrollEnabled(false);
      setIsUserScrolling(true);
    } else {
      if (!autoScrollEnabled) setAutoScrollEnabled(true);
      setIsUserScrolling(false);
    }
  };

  useEffect(() => {
    if (autoScrollEnabled && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [rawTokens, autoScrollEnabled]);

  return (
    <div className="relative h-full flex flex-col bg-obsidian border border-accent-cyan/30 rounded-xl overflow-hidden neon-pulse-cyan">
      <div className="bg-accent-cyan/10 p-2 text-xs text-accent-cyan font-mono border-b border-accent-cyan/30 flex justify-between">
        <span>sys.out // LIVE_FEED</span>
        {isUserScrolling && <span className="animate-pulse text-accent-pink">SCROLL PAUSED</span>}
      </div>
      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 p-4 overflow-y-auto scrollbar-thin scrollbar-thumb-accent-cyan scrollbar-track-transparent flex flex-col space-y-2"
      >
        {logs.map((log, i) => (
          <div key={i} className={`text-xs font-mono break-words ${log.startsWith('ERROR:') ? 'text-accent-pink font-bold' : 'text-white/60'}`}>
            {log}
          </div>
        ))}
        <TokenStreamDisplay tokens={rawTokens} />
      </div>
    </div>
  );
}
