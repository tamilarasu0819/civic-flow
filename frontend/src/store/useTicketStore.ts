import { create } from 'zustand';
import type { GeneratedTicket, VisionAnalysisResult } from '../types/ticket';

interface TicketState {
  activeTicket: GeneratedTicket | null;
  visionData: VisionAnalysisResult | null;
  imagePreviewUrl: string | null;
  isInspectorOpen: boolean;
  activeJsonTab: 'vision' | 'ticket';
  modifiedFields: string[];
  isCustomizing: boolean;
  
  initTicket: (ticketData: GeneratedTicket, visionData: VisionAnalysisResult) => void;
  updateActiveTicket: (updatedTicket: GeneratedTicket, changedFields: string[]) => void;
  setCustomizing: (isCustomizing: boolean) => void;
  setImagePreviewUrl: (url: string) => void;
  setInspectorOpen: (isOpen: boolean) => void;
  setActiveJsonTab: (tab: 'vision' | 'ticket') => void;
  resetTicketStore: () => void;
}

export const useTicketStore = create<TicketState>((set) => ({
  activeTicket: null,
  visionData: null,
  imagePreviewUrl: null,
  isInspectorOpen: false,
  activeJsonTab: 'ticket',
  modifiedFields: [],
  isCustomizing: false,
  
  initTicket: (ticketData, visionData) => set({ 
    activeTicket: ticketData, 
    visionData: visionData,
    modifiedFields: [],
    isCustomizing: false
  }),
  updateActiveTicket: (updatedTicket, changedFields) => set((state) => ({
    activeTicket: { ...state.activeTicket, ...updatedTicket },
    modifiedFields: Array.from(new Set([...state.modifiedFields, ...changedFields]))
  })),
  setCustomizing: (isCustomizing) => set({ isCustomizing }),
  setImagePreviewUrl: (url) => set({ imagePreviewUrl: url }),
  setInspectorOpen: (isOpen) => set({ isInspectorOpen: isOpen }),
  setActiveJsonTab: (tab) => set({ activeJsonTab: tab }),
  resetTicketStore: () => set({
    activeTicket: null,
    visionData: null,
    imagePreviewUrl: null,
    isInspectorOpen: false,
    activeJsonTab: 'ticket',
    modifiedFields: [],
    isCustomizing: false
  }),
}));
