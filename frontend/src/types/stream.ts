export type StreamStage =
  | 'IDLE'
  | 'UPLOADING'
  | 'ANALYZING_VISION'
  | 'MAPPING_DEPARTMENT'
  | 'SYNTHESIZING_TICKET'
  | 'COMPLETE'
  | 'ERROR';

export type StreamStatus = 'active' | 'success' | 'error' | 'pending';

export interface SSEPacket {
  type: 'stage_start' | 'token' | 'vision_complete' | 'ticket_complete' | 'error';
  data: any;
}

export interface TokenPayload {
  token: string;
}

export interface VisionCompletePayload {
  visionResult: any;
}

export interface TicketCompletePayload {
  ticketResult: any;
}

export interface StreamErrorDetails {
  message: string;
  code?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  isTyping?: boolean;
}

