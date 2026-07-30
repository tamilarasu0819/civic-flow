import type { ComplaintPreviewProps } from '../../types/ticket';
import { MapPin, Calendar, CheckSquare, Sparkles, Loader2 } from 'lucide-react';
import { useTicketStore } from '../../store/useTicketStore';

export function ComplaintPreview({ ticket }: ComplaintPreviewProps) {
  const { modifiedFields, isCustomizing } = useTicketStore();

  const isFieldModified = (fieldName: string) => modifiedFields.includes(fieldName);

  return (
    <div id="complaint-preview" className={`bg-white text-black p-8 rounded-xl shadow-lg relative overflow-hidden transition-all ${isCustomizing ? 'ring-2 ring-purple-500 shadow-purple-500/20' : ''}`}>
      
      {/* Loading Overlay Bar during customization */}
      {isCustomizing && (
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-purple-100 overflow-hidden">
          <div className="h-full bg-gradient-to-r from-purple-600 via-accent-cyan to-purple-600 animate-pulse w-full" />
        </div>
      )}

      {/* Official Header */}
      <div className="border-b-2 border-black/80 pb-4 mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-serif font-bold uppercase tracking-tight flex items-center">
            Official Complaint Form
            {isCustomizing ? (
              <span className="ml-3 inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-sans font-semibold bg-purple-600 text-white shadow-md animate-pulse">
                <Loader2 className="w-3 h-3 animate-spin text-white" />
                <span>Updating via Groq AI...</span>
              </span>
            ) : modifiedFields.length > 0 ? (
              <span className="ml-3 inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-sans font-semibold bg-purple-100 text-purple-800 border border-purple-300 shadow-sm">
                <Sparkles className="w-3 h-3 text-purple-600" />
                <span>Customized via Chat</span>
              </span>
            ) : null}
          </h1>
          <p className="text-sm font-sans text-gray-600">CivicFlow AI Automated Generation</p>
        </div>
        <div className="text-right font-mono text-sm">
          <p>TICKET ID: <strong>{ticket.id}</strong></p>
          <p>DATE: {new Date(ticket.dateGenerated).toLocaleDateString()}</p>
        </div>
      </div>

      {/* Body */}
      <div className="space-y-6 font-serif text-gray-900 leading-relaxed">
        <div className={isFieldModified('department') ? 'p-2 bg-purple-50/80 rounded border border-purple-200 transition-all' : ''}>
          <p className="font-bold flex items-center">
            To:
            {isFieldModified('department') && (
              <span className="ml-2 text-[10px] bg-purple-600 text-white px-1.5 py-0.5 rounded font-sans font-bold">UPDATED</span>
            )}
          </p>
          <p className="font-semibold">{ticket.department}</p>
          <p>Municipal Infrastructure Division</p>
        </div>

        <div className={isFieldModified('title') ? 'p-2 bg-purple-50/80 rounded border border-purple-200 transition-all' : ''}>
          <p className="font-bold flex items-center">
            Subject: {ticket.title}
            {isFieldModified('title') && (
              <span className="ml-2 text-[10px] bg-purple-600 text-white px-1.5 py-0.5 rounded font-sans font-bold">UPDATED</span>
            )}
          </p>
        </div>

        <div className={isFieldModified('description') || isFieldModified('severity') ? 'p-2 bg-purple-50/80 rounded border border-purple-200 transition-all' : ''}>
          <p>To Whom It May Concern,</p>
          <p className="mt-2">
            This document serves as formal notification regarding a <strong className={isFieldModified('severity') ? 'text-purple-700 font-extrabold underline' : ''}>{ticket.severity.toLowerCase()} severity</strong> issue identified as <em>{ticket.category}</em>.
          </p>
          <p className="mt-2">
            {ticket.description}
          </p>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg border border-gray-200 font-sans text-sm">
          <div className={`flex items-start space-x-2 ${isFieldModified('location') ? 'bg-purple-100/80 p-2 rounded border border-purple-300 transition-all' : ''}`}>
            <MapPin className="w-4 h-4 mt-0.5 text-purple-700" />
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-bold block text-gray-700">Location Details</span>
                {isFieldModified('location') && (
                  <span className="text-[10px] bg-purple-600 text-white font-bold px-1.5 py-0.2 rounded">UPDATED</span>
                )}
              </div>
              <span className={isFieldModified('location') ? 'font-bold text-purple-950' : ''}>
                {ticket.location || 'Location inferred from telemetry (See metadata)'}
              </span>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <Calendar className="w-4 h-4 mt-0.5 text-gray-500" />
            <div>
              <span className="font-bold block text-gray-700">Date of Record</span>
              <span>{new Date(ticket.dateGenerated).toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="font-bold font-sans text-sm uppercase tracking-wider mb-2">Automated Evidence Review</h3>
          <ul className="space-y-2 text-sm">
            {ticket.evidence.map((item, idx) => (
              <li key={idx} className="flex items-center space-x-2">
                <CheckSquare className="w-4 h-4 text-green-700" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* Footer stamp */}
      <div className="mt-12 pt-6 border-t border-gray-300 flex justify-between items-center text-xs text-gray-500 font-sans">
        <p>Generated securely via CivicFlow AI System.</p>
        <div className="w-16 h-16 border-2 border-red-800 text-red-800 rounded-full flex flex-col items-center justify-center transform -rotate-12 opacity-80">
          <span className="font-bold text-[10px]">VERIFIED</span>
          <span className="text-[8px] font-mono">AI-GEN</span>
        </div>
      </div>
    </div>
  );
}
