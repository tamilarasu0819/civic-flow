import { useRef, useEffect, useCallback } from 'react';
import { useStreamStore } from '../store/useStreamStore';
import { useTicketStore } from '../store/useTicketStore';
import type { StreamStage, VisionCompletePayload, TicketCompletePayload } from '../types/stream';

export function useAIStream() {
  const { 
    setStage, 
    setStatus, 
    appendTokenBatch, 
    addLog, 
    setVisionResult, 
    setTicketResult,
    setConfidenceScore,
    setError,
    addMessage
  } = useStreamStore();
  
  const { initTicket, resetTicketStore } = useTicketStore();

  const eventSourceRef = useRef<EventSource | null>(null);
  const tokenBufferRef = useRef<string>('');
  const rafIdRef = useRef<number | null>(null);

  // RAF loop to flush tokens in batches and prevent re-render thrashing
  const flushTokens = useCallback(() => {
    if (tokenBufferRef.current.length > 0) {
      appendTokenBatch(tokenBufferRef.current);
      tokenBufferRef.current = '';
    }
    rafIdRef.current = requestAnimationFrame(flushTokens);
  }, [appendTokenBatch]);

  useEffect(() => {
    rafIdRef.current = requestAnimationFrame(flushTokens);
    return () => {
      if (rafIdRef.current) cancelAnimationFrame(rafIdRef.current);
      if (eventSourceRef.current) eventSourceRef.current.close();
    };
  }, [flushTokens]);

  const uploadAndStartStream = async (file: File) => {
    try {
      // Clear all previous analysis and ticket data
      setVisionResult(null);
      setTicketResult(null);
      resetTicketStore();
      
      setStage('UPLOADING');
      setStatus('active');
      addLog(`[SYSTEM] Starting upload for ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
      
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/api/v1/upload-session', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed with status ${response.status}`);
      }

      const data = await response.json();
      const sessionId = data.sessionId;
      
      addLog(`[SYSTEM] Upload successful. Session ID: ${sessionId}`);
      connectSSE(sessionId);

    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Upload failed');
    }
  };

  const connectSSE = (sessionId: string) => {
    addLog(`[NETWORK] Connecting to SSE stream for session ${sessionId}...`);
    
    const es = new EventSource(`/api/v1/analyze-live?sessionId=${sessionId}`);
    eventSourceRef.current = es;

    es.addEventListener('stage_start', (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data);
        setStage(payload.stage as StreamStage);
        addLog(`[STAGE START] ${payload.stage}`);
      } catch(_err) {
        console.error('Failed to parse stage_start', _err);
      }
    });

    es.addEventListener('token', (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data);
        // Buffer tokens, RAF loop will flush them
        tokenBufferRef.current += payload.token;
      } catch(err) {
        console.error('Failed to parse token', err);
      }
    });

    es.addEventListener('vision_complete', (e: MessageEvent) => {
      try {
        const payload: VisionCompletePayload = JSON.parse(e.data);
        setVisionResult(payload.visionResult);
        if (payload.visionResult?.confidenceScore) {
          setConfidenceScore(payload.visionResult.confidenceScore);
        }
        addLog(`[SYSTEM] Vision analysis complete.`);
      } catch(err) {
        console.error('Failed to parse vision_complete', err);
      }
    });

    es.addEventListener('non_civic', (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data);
        setStage('COMPLETE');
        setStatus('success');
        addLog(`[SYSTEM] ${payload.message || 'Non-civic image detected.'}`);

        const desc = payload.description || payload.message || 'a non-infrastructure photo or document.';
        addMessage({
          id: `msg-${Date.now()}`,
          sender: 'ai',
          content: `Sorry, I couldn't find exactly what your problem is. All I see is: ${desc}`
        });

        es.close();
      } catch(err) {
        console.error('Failed to parse non_civic', err);
        es.close();
      }
    });

    es.addEventListener('ticket_complete', (e: MessageEvent) => {
      try {
        const payload: TicketCompletePayload = JSON.parse(e.data);
        setTicketResult(payload.ticketResult);
        addLog(`[SYSTEM] Ticket generation complete.`);
        
        // Sync stores when complete
        const { visionResult } = useStreamStore.getState();
        initTicket(payload.ticketResult, visionResult);
        
        setStage('COMPLETE');
        setStatus('success');
        es.close();
      } catch(err) {
        console.error('Failed to parse ticket_complete', err);
      }
    });

    es.addEventListener('error', (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data);
        setError(payload.message || 'Stream error');
        es.close();
      } catch(err) {
        setError('Unknown stream error');
        es.close();
      }
    });

    es.onerror = (_err) => {
      setError('SSE Connection lost');
      es.close();
    };
  };

  return {
    uploadAndStartStream
  };
}
