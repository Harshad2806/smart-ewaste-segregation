import { useRef, useState, useCallback } from 'react';
import { Upload, ImagePlus, X, FileImage } from 'lucide-react';

const ACCEPT = 'image/jpeg,image/png,image/webp,image/bmp,image/tiff';

export default function DropZone({ onFileSelect, file, onClear, disabled }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      const dropped = e.dataTransfer.files[0];
      if (dropped && dropped.type.startsWith('image/')) {
        onFileSelect(dropped);
      }
    },
    [disabled, onFileSelect],
  );

  const handleChange = (e) => {
    const selected = e.target.files[0];
    if (selected) onFileSelect(selected);
    e.target.value = '';
  };

  // ── File selected state ──────────────────────────────────
  if (file) {
    return (
      <div className="glass-card p-4 animate-fade-in">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
            <FileImage className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-slate-200 truncate">{file.name}</p>
            <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
          {!disabled && (
            <button
              onClick={onClear}
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-500 hover:text-slate-300 transition"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    );
  }

  // ── Empty / Drop zone state ──────────────────────────────
  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      className={`
        relative group cursor-pointer rounded-2xl border-2 border-dashed
        transition-all duration-300 p-10
        flex flex-col items-center justify-center text-center gap-4
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${
          dragOver
            ? 'border-emerald-400 bg-emerald-500/5 scale-[1.01]'
            : 'border-slate-700 hover:border-slate-500 bg-slate-900/30'
        }
      `}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        onChange={handleChange}
        className="hidden"
        disabled={disabled}
      />

      <div
        className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-colors ${
          dragOver ? 'bg-emerald-500/15' : 'bg-slate-800 group-hover:bg-slate-700'
        }`}
      >
        {dragOver ? (
          <ImagePlus className="w-8 h-8 text-emerald-400" />
        ) : (
          <Upload className="w-8 h-8 text-slate-400 group-hover:text-slate-300 transition-colors" />
        )}
      </div>

      <div>
        <p className="text-base font-semibold text-slate-200">
          {dragOver ? 'Drop to upload' : 'Drag & drop your e-waste image'}
        </p>
        <p className="text-sm text-slate-500 mt-1">or click to browse</p>
      </div>

      <p className="text-xs text-slate-600">
        Supports JPG, PNG, WebP, BMP, TIFF
      </p>
    </div>
  );
}
