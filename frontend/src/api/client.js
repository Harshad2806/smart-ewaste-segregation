/**
 * API client for the Smart E-Waste backend.
 *
 * Uses VITE_API_BASE_URL from the environment.
 * In local dev this is empty — Vite proxies /health and /predict to the backend.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * GET /health — check backend readiness.
 * @returns {{ status: string, model_loaded: boolean }}
 */
export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed (${res.status})`);
  return res.json();
}

/**
 * POST /predict — classify an e-waste image.
 * @param {File} file
 * @returns {object} PredictionResponse
 */
export async function predictImage(file) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${BASE_URL}/predict`, {
    method: 'POST',
    body: form,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || `Prediction failed (${res.status})`);
  }

  return data;
}
