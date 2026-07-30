import { useStreamStore } from './store/useStreamStore';
import { useTicketStore } from './store/useTicketStore';
import { useAIStream } from './hooks/useAIStream';
import { ShieldAlert, RotateCcw } from 'lucide-react';

import { Sidebar } from './components/layout/Sidebar';
import { ImageUploader } from './components/ticket/ImageUploader';
import { ThoughtStreamHUD } from './components/streaming/ThoughtStreamHUD';
import { SeverityCard } from './components/ticket/SeverityCard';
import { IssueCategoryCard } from './components/ticket/IssueCategoryCard';
import { DepartmentCard } from './components/ticket/DepartmentCard';
import { ComplaintPreview } from './components/ticket/ComplaintPreview';
import { ExportActionPanel } from './components/ticket/ExportActionPanel';
import { ChatInputBox } from './components/streaming/ChatInputBox';
import { ChatStream } from './components/streaming/ChatStream';

function App() {
  const { currentStage, visionResult, resetStore } = useStreamStore();
  const { activeTicket, visionData, resetTicketStore } = useTicketStore();
  const { uploadAndStartStream } = useAIStream();

  const handleUploadStart = (file: File) => {
    uploadAndStartStream(file);
  };

  const handleReset = () => {
    resetStore();
    resetTicketStore();
  };

  return (
    <div className="h-screen w-screen flex overflow-hidden bg-[var(--color-bg-main,#090A0F)] text-white">
      {/* Fixed Sidebar */}
      <Sidebar />

      {/* Main Workspace */}
      <main className="flex-1 flex flex-col h-full min-w-0 overflow-hidden relative">
        {/* Background Decor */}
        <div className="absolute top-[-20%] left-[20%] w-[50%] h-[50%] rounded-full bg-accent-purple/10 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-accent-cyan/10 blur-[120px] pointer-events-none" />
        
        {/* Workspace Header */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-white/10 z-10 bg-obsidian/80 backdrop-blur-md">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse shadow-[0_0_8px_rgba(0,255,102,0.8)]" />
            <span className="text-sm font-medium text-white/80">Gemma 4 Vision Active</span>
          </div>
          <div className="flex items-center space-x-2 text-xs font-mono text-white/40">
            <span>SSE Connected</span>
            <span className="w-1.5 h-1.5 rounded-full bg-accent-cyan" />
          </div>
        </header>

        {/* Dynamic Center Stage */}
        <div className="flex-1 overflow-y-auto flex flex-col p-6 scroll-smooth z-10 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          <div className="flex-1 flex flex-col w-full max-w-7xl mx-auto">
            
            {currentStage === 'IDLE' && (
              <div className="flex flex-col w-full animate-in fade-in duration-500 my-auto">
                <ChatStream />
                <div className="mt-4 mb-8">
                  <ImageUploader onUploadStart={handleUploadStart} />
                </div>
              </div>
            )}

            {currentStage !== 'IDLE' && currentStage !== 'COMPLETE' && (
              <div className="flex flex-col w-full animate-in fade-in duration-500 mt-auto">
                <ChatStream />
                <div className="mt-4">
                  <ThoughtStreamHUD />
                </div>
              </div>
            )}

            {/* Non-Civic Image Detected view */}
            {currentStage === 'COMPLETE' && (!activeTicket || visionResult?.is_civic_issue === false) && (
              <div className="max-w-2xl mx-auto p-8 rounded-2xl bg-card-glass border border-accent-pink/40 shadow-[0_0_30px_rgba(255,0,128,0.15)] text-center animate-in fade-in zoom-in-95 duration-500 my-auto">
                <div className="w-16 h-16 rounded-full bg-accent-pink/20 border border-accent-pink/50 flex items-center justify-center mx-auto mb-4 text-accent-pink">
                  <ShieldAlert className="w-8 h-8" />
                </div>
                <h2 className="text-xl font-bold text-white mb-2">
                  No Civic Infrastructure Defect Found
                </h2>
                <div className="bg-obsidian/80 border border-accent-pink/30 p-5 rounded-xl text-left my-6">
                  <p className="text-base text-accent-pink font-semibold mb-2 font-sans">
                    Sorry, I couldn't find exactly what your problem is.
                  </p>
                  <p className="text-sm text-white/90 leading-relaxed font-sans">
                    All I see is: <span className="text-white font-medium">{visionResult?.description || 'a non-civic image or personal document with no municipal defect.'}</span>
                  </p>
                </div>
                <p className="text-xs text-white/50 mb-6 max-w-md mx-auto">
                  CivicFlow only generates municipal complaint tickets when a public infrastructure defect (e.g. pothole, broken streetlight, open manhole, garbage dump, water leakage) is identified.
                </p>
                <button
                  onClick={handleReset}
                  className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-accent-purple hover:bg-accent-purple/80 text-white font-medium text-sm transition-all shadow-lg hover:shadow-accent-purple/30"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Upload Another Image</span>
                </button>
              </div>
            )}

            {/* Complete Ticket Generation view */}
            {currentStage === 'COMPLETE' && activeTicket && visionResult?.is_civic_issue !== false && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
                <div className="flex justify-between items-end border-b border-white/10 pb-4 mb-6">
                  <div>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-accent-cyan to-accent-green">
                      Analysis Complete
                    </h2>
                    <p className="text-white/50 text-sm mt-1 font-mono">TICKET: {activeTicket.id}</p>
                  </div>
                  <ExportActionPanel />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Left Column: Metadata Cards */}
                  <div className="col-span-1 lg:col-span-4 flex flex-col space-y-6">
                    <SeverityCard 
                      severity={activeTicket.severity} 
                      confidence={visionData?.confidenceScore || 90} 
                    />
                    <IssueCategoryCard 
                      category={activeTicket.category} 
                      infrastructure={visionData?.infrastructureAffected || ['Roadway', 'Public Access']} 
                    />
                    <DepartmentCard 
                      department={activeTicket.department} 
                    />
                  </div>

                  {/* Right Column: Complaint Preview */}
                  <div className="col-span-1 lg:col-span-8">
                    <ComplaintPreview ticket={activeTicket} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Floating Chat Input */}
        <div className="z-20 w-full px-4 pt-4 shrink-0 bg-gradient-to-t from-obsidian via-obsidian/80 to-transparent">
          <ChatInputBox />
        </div>
      </main>
    </div>
  );
}

export default App;
