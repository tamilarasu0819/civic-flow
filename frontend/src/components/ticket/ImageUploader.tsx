import { useState, useRef } from 'react';
import { UploadCloud } from 'lucide-react';
import { useTicketStore } from '../../store/useTicketStore';

interface ImageUploaderProps {
  onUploadStart: (file: File) => void;
}

export function ImageUploader({ onUploadStart }: ImageUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { setImagePreviewUrl } = useTicketStore();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true);
    } else if (e.type === 'dragleave') {
      setIsDragging(false);
    }
  };

  const validateAndProcessFile = (file: File) => {
    setError(null);
    if (!file.type.startsWith('image/')) {
      setError('Please upload a valid image file.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        setImagePreviewUrl(e.target.result as string);
        onUploadStart(file);
      }
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndProcessFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndProcessFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center w-full max-w-2xl mx-auto p-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-accent-cyan to-accent-purple">
          CivicFlow AI Core
        </h1>
        <p className="text-white/60">Upload infrastructure imagery to begin intelligent analysis</p>
      </div>

      <div 
        className={`relative w-full h-64 flex flex-col items-center justify-center rounded-2xl border transition-all duration-500 overflow-hidden backdrop-blur-xl ${
          isDragging ? 'border-accent-cyan bg-accent-cyan/10 scale-105 shadow-[0_0_30px_rgba(0,240,255,0.3)]' : 'border-white/10 bg-white/5 hover:border-accent-cyan/50 hover:bg-white/10 hover:shadow-[0_0_20px_rgba(0,240,255,0.15)] cursor-pointer'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleChange} 
          accept="image/*" 
          className="hidden" 
        />
        
        <div className="flex flex-col items-center justify-center space-y-4 pointer-events-none">
          <div className={`p-4 rounded-full ${isDragging ? 'bg-accent-cyan/20' : 'bg-white/5'}`}>
            <UploadCloud className={`w-10 h-10 ${isDragging ? 'text-accent-cyan' : 'text-white/50'}`} />
          </div>
          <div className="text-center">
            <p className="text-lg font-semibold text-white/80">
              Drag & drop an image here
            </p>
            <p className="text-sm text-white/40 mt-1">or click to browse files</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 px-4 py-2 bg-accent-pink/20 border border-accent-pink text-accent-pink rounded-md">
          {error}
        </div>
      )}
    </div>
  );
}
