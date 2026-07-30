import { Copy, FileDown, Send, FileText } from 'lucide-react';
import { useTicketStore } from '../../store/useTicketStore';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { useState } from 'react';

export function ExportActionPanel() {
  const { activeTicket } = useTicketStore();
  const [isExporting, setIsExporting] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyText = async () => {
    if (!activeTicket) return;
    const text = `Ticket ID: ${activeTicket.id}\nTitle: ${activeTicket.title}\nSeverity: ${activeTicket.severity}\nCategory: ${activeTicket.category}\nDepartment: ${activeTicket.department}\nDescription: ${activeTicket.description}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadPDF = async () => {
    const element = document.getElementById('complaint-preview');
    if (!element || isExporting) return;
    
    setIsExporting(true);
    try {
      const canvas = await html2canvas(element, { scale: 2 });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(`CivicFlow_Ticket_${activeTicket?.id}.pdf`);
    } catch (error) {
      console.error('PDF Export failed', error);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownloadMD = () => {
    if (!activeTicket) return;
    const mdContent = `# ${activeTicket.title}
**Ticket ID**: ${activeTicket.id}
**Date**: ${new Date(activeTicket.dateGenerated).toLocaleString()}
**Department**: ${activeTicket.department}
**Severity**: ${activeTicket.severity}
**Category**: ${activeTicket.category}

## Description
${activeTicket.description}

## Evidence
${activeTicket.evidence.map(e => `- ${e}`).join('\n')}
`;
    
    const blob = new Blob([mdContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Ticket_${activeTicket.id}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex items-center space-x-4 bg-card-glass backdrop-blur-md p-4 rounded-xl border border-white/10">
      <button 
        onClick={handleCopyText}
        className="flex items-center space-x-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/20 rounded-lg text-sm text-white transition-colors"
      >
        <Copy className="w-4 h-4 text-white/70" />
        <span>{copied ? 'Copied!' : 'Copy Text'}</span>
      </button>

      <button 
        onClick={handleDownloadPDF}
        disabled={isExporting}
        className="flex items-center space-x-2 px-4 py-2 bg-accent-cyan/10 hover:bg-accent-cyan/20 border border-accent-cyan/50 text-accent-cyan rounded-lg text-sm transition-colors disabled:opacity-50"
      >
        <FileDown className="w-4 h-4" />
        <span>{isExporting ? 'Generating...' : 'Export PDF'}</span>
      </button>

      <button 
        onClick={handleDownloadMD}
        className="flex items-center space-x-2 px-4 py-2 bg-accent-purple/10 hover:bg-accent-purple/20 border border-accent-purple/50 text-accent-purple rounded-lg text-sm transition-colors"
      >
        <FileText className="w-4 h-4" />
        <span>Download .md</span>
      </button>

      <div className="flex-1" />

      <div className="relative group">
        <button 
          disabled
          className="flex items-center space-x-2 px-6 py-2 bg-accent-green/20 border border-accent-green/50 text-accent-green rounded-lg text-sm opacity-50 cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
          <span>Submit to Portal</span>
        </button>
        {/* Tooltip */}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-max px-3 py-1 bg-black/90 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
          Disabled in MVP. Requires government API credentials.
        </div>
      </div>
    </div>
  );
}
