import { useEffect, useRef, useState } from 'react';
import {
  Camera,
  CameraOff,
  Loader2,
  ScanSearch,
  Wifi,
  AlertCircle,
} from 'lucide-react';

import { predictImage } from '../api/client';

export default function CameraPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [cameraActive, setCameraActive] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  // ----------------------------------------------------------
  // START CAMERA
  // ----------------------------------------------------------
  const startCamera = async () => {
    try {
      setError('');
      setResult(null);

      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error(
          'Camera access is not supported by this browser.'
        );
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });

      streamRef.current = stream;

      // Render the video element first.
      setCameraActive(true);

      requestAnimationFrame(() => {
        const video = videoRef.current;

        if (!video) {
          setError(
            'Camera stream opened, but the video element could not be initialized.'
          );
          return;
        }

        video.srcObject = stream;

        video.onloadedmetadata = async () => {
          try {
            await video.play();
          } catch (err) {
            console.error('Video playback error:', err);

            setError(
              `Video playback failed: ${
                err.message || 'Unknown playback error'
              }`
            );
          }
        };
      });
    } catch (err) {
      console.error('Camera error:', err);

      setError(
        `Camera error: ${err.name || 'UnknownError'} — ${
          err.message || 'Unable to access the camera.'
        }`
      );

      setCameraActive(false);
    }
  };

  // ----------------------------------------------------------
  // STOP CAMERA
  // ----------------------------------------------------------
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
      videoRef.current.onloadedmetadata = null;
    }

    setCameraActive(false);
  };

  // ----------------------------------------------------------
  // CAPTURE + ANALYZE
  // ----------------------------------------------------------
  const captureAndAnalyze = async () => {
    if (
      !videoRef.current ||
      !canvasRef.current ||
      !cameraActive ||
      analyzing
    ) {
      return;
    }

    try {
      setError('');
      setAnalyzing(true);

      const video = videoRef.current;
      const canvas = canvasRef.current;

      const width = video.videoWidth;
      const height = video.videoHeight;

      if (!width || !height) {
        throw new Error(
          'Camera frame is not ready yet. Please wait a moment and try again.'
        );
      }

      canvas.width = width;
      canvas.height = height;

      const context = canvas.getContext('2d');

      if (!context) {
        throw new Error('Could not initialize image capture.');
      }

      // Capture current camera frame.
      context.drawImage(
        video,
        0,
        0,
        width,
        height
      );

      // Convert canvas → JPEG blob.
      const blob = await new Promise((resolve, reject) => {
        canvas.toBlob(
          (resultBlob) => {
            if (!resultBlob) {
              reject(
                new Error('Could not capture camera frame.')
              );
              return;
            }

            resolve(resultBlob);
          },
          'image/jpeg',
          0.9
        );
      });

      // Convert blob to File because predictImage()
      // expects a File object.
      const file = new File(
        [blob],
        'camera-capture.jpg',
        {
          type: 'image/jpeg',
        }
      );

      // IMPORTANT:
      // Use the existing API client.
      // It sends the correct "file" form field and
      // uses the Vite development proxy.
      const data = await predictImage(file);

      setResult(data);

    } catch (err) {
      console.error('Analysis error:', err);

      setError(
        err.message ||
          'Unable to analyze the captured image.'
      );
    } finally {
      setAnalyzing(false);
    }
  };

  // ----------------------------------------------------------
  // CLEANUP
  // ----------------------------------------------------------
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current
          .getTracks()
          .forEach((track) => track.stop());

        streamRef.current = null;
      }
    };
  }, []);

  // ----------------------------------------------------------
  // RESPONSE DATA
  // ----------------------------------------------------------
  const vision = result?.vision || null;
  const intelligence = result?.intelligence || null;
  const aiReasoning = intelligence?.ai_reasoning || null;

  // ----------------------------------------------------------
  // UI
  // ----------------------------------------------------------
  return (
    <div className="max-w-5xl mx-auto px-4 py-8">

      {/* HEADER */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold text-gradient mb-2">
          Live Camera
        </h1>

        <p className="text-slate-500 text-sm">
          Capture an e-waste item and run the full AI analysis.
        </p>
      </div>

      {/* CAMERA */}
      <div className="glass-card overflow-hidden">

        <div className="relative aspect-video bg-slate-950">

          {cameraActive ? (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center">
                <CameraOff className="w-14 h-14 text-slate-600 mx-auto mb-4" />

                <h2 className="text-lg font-semibold text-slate-400">
                  Camera is off
                </h2>

                <p className="text-sm text-slate-600 mt-1">
                  Start the camera to analyze an e-waste item.
                </p>
              </div>
            </div>
          )}

          {cameraActive && (
            <>
              <div className="absolute top-4 left-4 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/50 text-xs text-white">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                CAMERA LIVE
              </div>

              <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/50 text-xs text-white">
                <Wifi className="w-3.5 h-3.5" />
                AI READY
              </div>

              {/* Camera guide */}
              <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-8 left-8 w-10 h-10 border-l-2 border-t-2 border-emerald-400" />
                <div className="absolute top-8 right-8 w-10 h-10 border-r-2 border-t-2 border-emerald-400" />
                <div className="absolute bottom-8 left-8 w-10 h-10 border-l-2 border-b-2 border-emerald-400" />
                <div className="absolute bottom-8 right-8 w-10 h-10 border-r-2 border-b-2 border-emerald-400" />
              </div>
            </>
          )}
        </div>

        {/* CONTROLS */}
        <div className="p-5 border-t border-slate-800/60">
          <div className="flex flex-wrap justify-center gap-3">

            {!cameraActive ? (
              <button
                onClick={startCamera}
                className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-emerald-500 text-white font-semibold hover:bg-emerald-400 transition"
              >
                <Camera className="w-5 h-5" />
                Start Camera
              </button>
            ) : (
              <>
                <button
                  onClick={captureAndAnalyze}
                  disabled={analyzing}
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-emerald-500 text-white font-semibold hover:bg-emerald-400 disabled:opacity-60 transition"
                >
                  {analyzing ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <ScanSearch className="w-5 h-5" />
                  )}

                  {analyzing
                    ? 'Analyzing...'
                    : 'Capture & Analyze'}
                </button>

                <button
                  onClick={stopCamera}
                  disabled={analyzing}
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-slate-800 text-slate-300 font-semibold hover:bg-slate-700 disabled:opacity-60 transition"
                >
                  <CameraOff className="w-5 h-5" />
                  Stop Camera
                </button>
              </>
            )}

          </div>
        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="mt-5 p-4 rounded-xl border border-red-500/20 bg-red-500/5 text-red-300 flex items-start gap-3">

          <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />

          <div>
            <p className="font-semibold">
              Camera / analysis error
            </p>

            <p className="text-sm mt-1 text-red-200/80">
              {error}
            </p>
          </div>

        </div>
      )}

      {/* Hidden canvas */}
      <canvas
        ref={canvasRef}
        className="hidden"
      />

      {/* RESULT */}
      {vision && (
        <div className="mt-6 glass-card p-6">

          <div className="flex items-center justify-between mb-5">

            <div>
              <p className="text-xs uppercase tracking-wider text-emerald-400 font-semibold">
                AI Detection
              </p>

              <h2 className="text-2xl font-bold text-slate-100 mt-1">
                {vision.predicted_class || 'Unknown'}
              </h2>
            </div>

            <div className="text-right">

              <p className="text-xs text-slate-500">
                Confidence
              </p>

              <p className="text-xl font-bold text-emerald-400">
                {typeof vision.confidence === 'number'
                  ? `${(vision.confidence * 100).toFixed(1)}%`
                  : '—'}
              </p>

            </div>

          </div>

          {intelligence && (
            <div className="space-y-5">

              {aiReasoning?.assessment && (
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    AI Assessment
                  </p>

                  <p className="text-sm text-slate-300 mt-1 leading-6">
                    {aiReasoning.assessment}
                  </p>
                </div>
              )}

              {aiReasoning?.user_explanation && (
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Explanation
                  </p>

                  <p className="text-sm text-slate-300 mt-1 leading-6">
                    {aiReasoning.user_explanation}
                  </p>
                </div>
              )}

              {aiReasoning?.recovery_pathway && (
                <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/15">

                  <p className="text-xs uppercase tracking-wider text-emerald-400">
                    Recovery Pathway
                  </p>

                  <p className="text-sm text-slate-200 mt-1">
                    {aiReasoning.recovery_pathway}
                  </p>

                </div>
              )}

              {aiReasoning?.reuse_recommendation && (
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Reuse
                  </p>

                  <p className="text-sm text-slate-300 mt-1">
                    {aiReasoning.reuse_recommendation}
                  </p>
                </div>
              )}

              {aiReasoning?.repair_recommendation && (
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Repair
                  </p>

                  <p className="text-sm text-slate-300 mt-1">
                    {aiReasoning.repair_recommendation}
                  </p>
                </div>
              )}

              {aiReasoning?.recycling_recommendation && (
                <div>
                  <p className="text-xs uppercase tracking-wider text-slate-500">
                    Recycling
                  </p>

                  <p className="text-sm text-slate-300 mt-1">
                    {aiReasoning.recycling_recommendation}
                  </p>
                </div>
              )}

              {aiReasoning?.risk_summary && (
                <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/15">

                  <p className="text-xs uppercase tracking-wider text-amber-400">
                    Risk Summary
                  </p>

                  <p className="text-sm text-slate-300 mt-1">
                    {aiReasoning.risk_summary}
                  </p>

                </div>
              )}

            </div>
          )}

        </div>
      )}

    </div>
  );
}