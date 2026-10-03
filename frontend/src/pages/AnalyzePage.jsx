import { useState, useCallback } from 'react';
import { ScanSearch, Loader2, AlertCircle, RotateCcw, Sparkles } from 'lucide-react';
import DropZone from '../components/DropZone';
import ResultsView from '../components/ResultsView';
import { predictImage } from '../api/client';

const STATUS = { IDLE: 'idle', ANALYZING: 'analyzing', SUCCESS: 'success', ERROR: 'error' };

export default function AnalyzePage({ onResult }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState(STATUS.IDLE);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = useCallback((f) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setStatus(STATUS.IDLE);
    setResult(null);
    setError(null);
  }, []);

  const handleClear = useCallback(() => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview(null);
    setStatus(STATUS.IDLE);
    setResult(null);
    setError(null);
  }, [preview]);

  const handleAnalyze = useCallback(async () => {
    if (!file) return;
    setStatus(STATUS.ANALYZING);
    setError(null);
    try {
      const data = await predictImage(file);
      setResult(data);
      setStatus(STATUS.SUCCESS);
      onResult?.(file.name, data);
    } catch (err) {
      setError(err.message || 'Analysis failed');
      setStatus(STATUS.ERROR);
    }
  }, [file, onResult]);

  const handleNewAnalysis = useCallback(() => {
    handleClear();
  }, [handleClear]);

  const isAnalyzing = status === STATUS.ANALYZING;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* ── Header ─────────────────────────────────────── */}
      <div className="text-center mb-8">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-gradient mb-2">
          E-Waste Analysis
        </h1>
        <p className="text-slate-500 text-sm max-w-md mx-auto">
          Upload an image of electronic waste to identify its class, materials,
          and get an AI-powered recycling recommendation.
        </p>
      </div>

      {/* ── Two-column layout (desktop) / stacked (mobile) ─ */}
      <div className={`grid gap-6 ${result ? 'lg:grid-cols-[380px_1fr]' : 'max-w-xl mx-auto'}`}>
        {/* LEFT: Upload panel */}
        <div className="space-y-4">
          <DropZone
            file={file}
            onFileSelect={handleFileSelect}
            onClear={handleClear}
            disabled={isAnalyzing}
          />

          {/* Image preview */}
          {preview && (
            <div className="glass-card overflow-hidden animate-fade-in">
              <div className="relative aspect-square sm:aspect-video bg-slate-900">
                <img
                  src={preview}
                  alt="Upload preview"
                  className="w-full h-full object-contain"
                />
                {isAnalyzing && (
                  <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm
                                  flex flex-col items-center justify-center gap-3">
                    <Loader2 className="w-10 h-10 text-emerald-400 animate-spin" />
                    <span className="text-sm font-medium text-emerald-300 animate-pulse-soft">
                      Analyzing e-waste…
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Analyze / New Analysis buttons */}
          {file && status !== STATUS.SUCCESS && (
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="btn-primary w-full"
            >
              {isAnalyzing ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing…</>
              ) : (
                <><Sparkles className="w-4 h-4" /> Analyze Image</>
              )}
            </button>
          )}

          {status === STATUS.SUCCESS && (
            <button onClick={handleNewAnalysis} className="btn-secondary w-full">
              <RotateCcw className="w-4 h-4" /> New Analysis
            </button>
          )}

          {/* Error state */}
          {status === STATUS.ERROR && (
            <div className="glass-card p-4 border-red-500/30 animate-fade-in">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-red-400">Analysis Failed</p>
                  <p className="text-sm text-slate-400 mt-1">{error}</p>
                  <button
                    onClick={handleAnalyze}
                    className="btn-secondary mt-3 text-xs"
                  >
                    <RotateCcw className="w-3.5 h-3.5" /> Retry
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: Results */}
        {result && (
          <div className="min-w-0">
            <ResultsView result={result} />
          </div>
        )}
      </div>

      {/* ── Empty state (no file) ──────────────────────── */}
      {!file && (
        <div className="mt-12 text-center animate-fade-in">
          <div className="inline-flex items-center gap-6 text-slate-700">
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-xl bg-slate-900 flex items-center justify-center mb-2">
                <ScanSearch className="w-6 h-6" />
              </div>
              <span className="text-xs">Upload</span>
            </div>
            <div className="w-8 h-px bg-slate-800" />
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-xl bg-slate-900 flex items-center justify-center mb-2">
                <Sparkles className="w-6 h-6" />
              </div>
              <span className="text-xs">Analyze</span>
            </div>
            <div className="w-8 h-px bg-slate-800" />
            <div className="text-center">
              <div className="w-12 h-12 mx-auto rounded-xl bg-slate-900 flex items-center justify-center mb-2">
                <Sparkles className="w-6 h-6" />
              </div>
              <span className="text-xs">Results</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
