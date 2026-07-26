import { useState, useRef, useCallback } from 'react';
import { Upload, ImageIcon, Leaf, ChevronDown, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { predictCropDisease, type PredictResponse } from '@/lib/api';

const CROP_TYPES = [
  { value: 'any', label: 'Any / Unknown' },
  { value: 'Tomato', label: 'Tomato' },
  { value: 'Maize', label: 'Maize (Corn)' },
  { value: 'Potato', label: 'Potato' },
];

interface UploadViewProps {
  onResult: (result: PredictResponse, image: string) => void;
}

export default function UploadView({ onResult }: UploadViewProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [cropType, setCropType] = useState<string>('any');
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith('image/')) {
      setError('Please upload a valid image file (JPG, PNG, WEBP).');
      return;
    }
    setError(null);
    setFile(f);
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(f);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await predictCropDisease(file, cropType);
      onResult(result, preview!);
    } catch (err) {
      setError('Connection failed. Check your network and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setPreview(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="animate-fade-in-up w-full max-w-xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: 'hsl(145 42% 28%)' }}
          >
            <Leaf className="w-4 h-4 text-white" />
          </div>
          <span
            className="text-xs font-semibold tracking-widest uppercase"
            style={{ color: 'hsl(145 42% 28%)' }}
          >
            Field Diagnostics
          </span>
        </div>
        <h1
          className="font-display text-4xl font-bold leading-tight mb-2"
          style={{ color: 'hsl(30 20% 14%)' }}
        >
          Crop Disease<br />Detection
        </h1>
        <p className="text-sm leading-relaxed" style={{ color: 'hsl(30 12% 44%)' }}>
          Photograph a diseased leaf, select your crop, and get an instant diagnosis with actionable field recommendations.
        </p>
      </div>

      {/* Drop Zone */}
      <div
        className={`relative border-2 border-dashed rounded-xl transition-all duration-200 cursor-pointer mb-5 ${
          isDragging ? 'drag-over border-primary' : 'border-border hover:border-primary/50'
        }`}
        style={{ backgroundColor: isDragging ? 'hsl(145 42% 28% / 0.05)' : undefined }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !preview && fileInputRef.current?.click()}
        data-testid="upload-dropzone"
      >
        {preview ? (
          <div className="relative">
            <img
              src={preview}
              alt="Uploaded leaf"
              className="w-full rounded-xl object-cover"
              style={{ maxHeight: '320px' }}
              data-testid="img-preview"
            />
            <div
              className="absolute inset-0 rounded-xl"
              style={{ background: 'linear-gradient(to top, rgba(30,20,10,0.5) 0%, transparent 60%)' }}
            />
            <div className="absolute bottom-0 left-0 right-0 p-4 flex items-end justify-between">
              <div>
                <p className="text-white text-sm font-semibold truncate max-w-[200px]">
                  {file?.name}
                </p>
                <p className="text-white/70 text-xs">
                  {file ? (file.size / 1024).toFixed(0) + ' KB' : ''}
                </p>
              </div>
              <button
                className="text-white/80 hover:text-white text-xs underline underline-offset-2 transition-colors"
                onClick={(e) => { e.stopPropagation(); handleClear(); }}
                data-testid="button-clear-image"
              >
                Change image
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-14 px-6 text-center">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4"
              style={{ backgroundColor: 'hsl(145 42% 28% / 0.10)' }}
            >
              {isDragging ? (
                <Upload className="w-7 h-7" style={{ color: 'hsl(145 42% 28%)' }} />
              ) : (
                <ImageIcon className="w-7 h-7" style={{ color: 'hsl(145 42% 28%)' }} />
              )}
            </div>
            <p className="font-semibold text-sm mb-1" style={{ color: 'hsl(30 20% 14%)' }}>
              {isDragging ? 'Release to upload' : 'Drag & drop a leaf photo'}
            </p>
            <p className="text-xs mb-4" style={{ color: 'hsl(30 12% 44%)' }}>
              or click to browse — JPG, PNG, WEBP supported
            </p>
            <div
              className="px-4 py-1.5 rounded-lg text-xs font-semibold border"
              style={{
                borderColor: 'hsl(145 42% 28% / 0.3)',
                color: 'hsl(145 42% 28%)',
                backgroundColor: 'hsl(145 42% 28% / 0.06)',
              }}
            >
              Browse Files
            </div>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleInputChange}
        data-testid="input-file"
      />

      {/* Crop Type Select */}
      <div className="mb-5">
        <Label
          htmlFor="crop-type"
          className="text-xs font-semibold tracking-wide uppercase mb-2 block"
          style={{ color: 'hsl(30 12% 44%)' }}
        >
          Crop Type
        </Label>
        <Select value={cropType} onValueChange={setCropType}>
          <SelectTrigger
            id="crop-type"
            className="w-full h-11 font-medium"
            data-testid="select-crop-type"
          >
            <div className="flex items-center gap-2">
              <Leaf className="w-4 h-4" style={{ color: 'hsl(145 42% 28%)' }} />
              <SelectValue placeholder="Select crop type" />
            </div>
            <ChevronDown className="w-4 h-4 opacity-50 ml-auto" />
          </SelectTrigger>
          <SelectContent>
            {CROP_TYPES.map((crop) => (
              <SelectItem key={crop.value} value={crop.value} data-testid={`option-crop-${crop.value}`}>
                {crop.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Error Message */}
      {error && (
        <div
          className="mb-4 px-4 py-3 rounded-lg border text-sm font-medium animate-fade-in"
          style={{
            backgroundColor: 'hsl(4 72% 46% / 0.08)',
            borderColor: 'hsl(4 72% 46% / 0.3)',
            color: 'hsl(4 72% 38%)',
          }}
          data-testid="status-error"
        >
          {error}
        </div>
      )}

      {/* Analyze Button */}
      <Button
        className="w-full h-12 text-sm font-bold tracking-wide"
        disabled={!file || isLoading}
        onClick={handleAnalyze}
        data-testid="button-analyze"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Analyzing sample...
          </span>
        ) : (
          'Run Diagnosis'
        )}
      </Button>

      {/* Loading overlay */}
      {isLoading && (
        <div className="mt-5 animate-fade-in">
          <div
            className="rounded-xl p-5 border"
            style={{
              backgroundColor: 'hsl(145 42% 28% / 0.06)',
              borderColor: 'hsl(145 42% 28% / 0.2)',
            }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ backgroundColor: 'hsl(145 42% 28% / 0.15)' }}
              >
                <Loader2 className="w-4 h-4 animate-spin" style={{ color: 'hsl(145 42% 28%)' }} />
              </div>
              <div>
                <p className="text-sm font-semibold" style={{ color: 'hsl(30 20% 14%)' }}>
                  Processing leaf sample
                </p>
                <p className="text-xs" style={{ color: 'hsl(30 12% 44%)' }}>
                  Running AI model inference...
                </p>
              </div>
            </div>
            <div
              className="h-1.5 rounded-full overflow-hidden"
              style={{ backgroundColor: 'hsl(145 42% 28% / 0.15)' }}
            >
              <div
                className="h-full rounded-full"
                style={{
                  width: '70%',
                  backgroundColor: 'hsl(145 42% 28%)',
                  animation: 'indeterminate 1.5s ease-in-out infinite',
                }}
              />
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes indeterminate {
          0% { transform: translateX(-100%); width: 60%; }
          100% { transform: translateX(250%); width: 60%; }
        }
      `}</style>
    </div>
  );
}
