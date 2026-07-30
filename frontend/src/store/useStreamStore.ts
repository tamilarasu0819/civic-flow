import { create } from 'zustand';
import type { StreamStage, StreamStatus, ChatMessage } from '../types/stream';

interface StreamState {
  currentStage: StreamStage;
  status: StreamStatus;
  rawTokens: string;
  logs: string[];
  confidenceScore: number;
  visionResult: any | null;
  ticketResult: any | null;
  autoScrollEnabled: boolean;
  messages: ChatMessage[];
  activeTheme: string;
  
  addMessage: (msg: ChatMessage) => void;
  updateMessage: (id: string, updates: Partial<ChatMessage>) => void;
  setTheme: (theme: string) => void;
  setStage: (stage: StreamStage) => void;
  setStatus: (status: StreamStatus) => void;
  appendTokenBatch: (tokens: string) => void;
  addLog: (log: string) => void;
  setVisionResult: (result: any) => void;
  setTicketResult: (result: any) => void;
  setConfidenceScore: (score: number) => void;
  setAutoScrollEnabled: (enabled: boolean) => void;
  setError: (errorMsg: string) => void;
  resetStore: () => void;
}

const initialState = {
  currentStage: 'IDLE' as StreamStage,
  status: 'pending' as StreamStatus,
  rawTokens: '',
  logs: [] as string[],
  confidenceScore: 0,
  visionResult: null,
  ticketResult: null,
  autoScrollEnabled: true,
  messages: [{
    id: 'msg-0',
    sender: 'ai',
    content: 'Welcome to CivicFlow Intelligence. Please upload an image or describe the civic issue to begin analysis.'
  }] as ChatMessage[],
  activeTheme: document.documentElement.getAttribute('data-theme') || 'cyan',
};

export const useStreamStore = create<StreamState>((set) => ({
  ...initialState,
  
  setStage: (stage) => set({ currentStage: stage }),
  setStatus: (status) => set({ status }),
  appendTokenBatch: (tokens) => set((state) => ({ rawTokens: state.rawTokens + tokens })),
  addLog: (log) => set((state) => ({ logs: [...state.logs, log] })),
  setVisionResult: (result) => set({ visionResult: result }),
  setTicketResult: (result) => set({ ticketResult: result }),
  setConfidenceScore: (score) => set({ confidenceScore: score }),
  setAutoScrollEnabled: (enabled) => set({ autoScrollEnabled: enabled }),
  setError: (errorMsg) => set({ 
    status: 'error', 
    currentStage: 'ERROR', 
    logs: [`ERROR: ${errorMsg}`] 
  }),
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  updateMessage: (id, updates) => set((state) => ({
    messages: state.messages.map(m => m.id === id ? { ...m, ...updates } : m)
  })),
  setTheme: (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    set({ activeTheme: theme });
  },
  resetStore: () => set((state) => ({
    ...initialState,
    messages: [...initialState.messages],
    activeTheme: state.activeTheme
  })),
}));
