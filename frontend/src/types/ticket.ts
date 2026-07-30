export type SeverityLevel = 'Critical' | 'High' | 'Medium' | 'Low';

export interface VisionAnalysisResult {
  detectedObjects: string[];
  severityEstimate: SeverityLevel;
  confidenceScore: number;
  extractedText?: string;
  infrastructureAffected?: string[];
}

export interface GeneratedTicket {
  id: string;
  title: string;
  description: string;
  category: string;
  department: string;
  severity: SeverityLevel;
  location?: string;
  evidence: string[];
  dateGenerated: string;
}

export interface ImageUploaderProps {
  onUploadStart: (file: File) => void;
}

export interface SeverityCardProps {
  severity: SeverityLevel;
  confidence: number;
}

export interface IssueCategoryCardProps {
  category: string;
  infrastructure: string[];
}

export interface DepartmentCardProps {
  department: string;
}

export interface ComplaintPreviewProps {
  ticket: GeneratedTicket;
}

export interface JsonInspectorProps {
  visionData: VisionAnalysisResult | null;
  ticketData: GeneratedTicket | null;
}
