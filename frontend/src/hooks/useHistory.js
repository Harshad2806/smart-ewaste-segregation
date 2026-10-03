import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'ewaste_history';
const MAX_ENTRIES = 50;

function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(entries) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

/**
 * React hook for managing analysis history in localStorage.
 *
 * Each entry:
 *  { id, timestamp, imageName, vision, intelligence }
 */
export function useHistory() {
  const [history, setHistory] = useState(loadHistory);

  // Sync to localStorage on every change.
  useEffect(() => {
    saveHistory(history);
  }, [history]);

  /** Add a new analysis result to history. */
  const addEntry = useCallback((imageName, result) => {
    const entry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      imageName,
      vision: result.vision,
      intelligence: result.intelligence,
    };
    setHistory((prev) => [entry, ...prev].slice(0, MAX_ENTRIES));
  }, []);

  /** Remove a single entry by id. */
  const removeEntry = useCallback((id) => {
    setHistory((prev) => prev.filter((e) => e.id !== id));
  }, []);

  /** Clear all history. */
  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  /** Computed statistics for the dashboard. */
  const stats = computeStats(history);

  return { history, addEntry, removeEntry, clearHistory, stats };
}

function computeStats(history) {
  if (history.length === 0) {
    return {
      totalScans: 0,
      avgConfidence: 0,
      highConfRate: 0,
      classCounts: {},
      topClass: null,
      tierCounts: { high: 0, medium: 0, low: 0 },
    };
  }

  const classCounts = {};
  const tierCounts = { high: 0, medium: 0, low: 0 };
  let confSum = 0;
  let highConf = 0;

  for (const entry of history) {
    const cls = entry.vision?.predicted_class || 'unknown';
    classCounts[cls] = (classCounts[cls] || 0) + 1;

    const conf = entry.vision?.confidence || 0;
    confSum += conf;
    if (conf >= 0.55) highConf++;

    const tier = entry.intelligence?.confidence_tier || 'low';
    if (tier in tierCounts) tierCounts[tier]++;
  }

  const topClass = Object.entries(classCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || null;

  return {
    totalScans: history.length,
    avgConfidence: confSum / history.length,
    highConfRate: highConf / history.length,
    classCounts,
    topClass,
    tierCounts,
  };
}
