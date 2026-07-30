import { memo } from 'react';

interface TokenStreamDisplayProps {
  tokens: string;
}

export const TokenStreamDisplay = memo(({ tokens }: TokenStreamDisplayProps) => {
  return (
    <div className="font-mono text-sm whitespace-pre-wrap text-accent-cyan break-words">
      {tokens}
      <span className="terminal-cursor inline-block w-2 h-4 bg-accent-cyan ml-1 align-middle"></span>
    </div>
  );
});

TokenStreamDisplay.displayName = 'TokenStreamDisplay';
