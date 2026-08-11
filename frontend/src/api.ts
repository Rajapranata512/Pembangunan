/* ===================================================
   api.ts — API client untuk semua endpoint backend
   =================================================== */
import type {
  PaginatedRegions, RegionDetail, ScoreData,
  AiInsightData, MapDataPoint, RecommendationResponse,
} from './types';

const BASE = '/api/v1';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

/* GET /regions */
export async function getRegions(params?: {
  province?: string; type?: string; min_score?: number;
  sort_by?: string; page?: number; limit?: number;
}): Promise<PaginatedRegions> {
  const sp = new URLSearchParams();
  if (params?.province) sp.set('province', params.province);
  if (params?.type) sp.set('type', params.type);
  if (params?.min_score) sp.set('min_score', String(params.min_score));
  if (params?.sort_by) sp.set('sort_by', params.sort_by);
  if (params?.page) sp.set('page', String(params.page));
  if (params?.limit) sp.set('limit', String(params.limit));
  return fetchJSON(`${BASE}/regions?${sp}`);
}

/* GET /regions/:id */
export async function getRegionDetail(id: number): Promise<RegionDetail> {
  return fetchJSON(`${BASE}/regions/${id}`);
}

/* GET /regions/:id/scores */
export async function getRegionScores(id: number): Promise<ScoreData> {
  return fetchJSON(`${BASE}/regions/${id}/scores`);
}

/* GET /regions/:id/insight */
export async function getRegionInsight(id: number): Promise<AiInsightData> {
  return fetchJSON(`${BASE}/regions/${id}/insight`);
}

/* GET /compare?ids=x,y */
export async function compareRegions(ids: number[]): Promise<RegionDetail[]> {
  return fetchJSON(`${BASE}/compare?ids=${ids.join(',')}`);
}

/* POST /recommendations */
export async function getRecommendations(body: {
  goal: string; province?: string; min_population?: number;
}): Promise<RecommendationResponse> {
  return fetchJSON(`${BASE}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

/* GET /map-data */
export async function getMapData(params?: {
  province?: string; score_type?: string;
}): Promise<MapDataPoint[]> {
  const sp = new URLSearchParams();
  if (params?.province) sp.set('province', params.province);
  if (params?.score_type) sp.set('score_type', params.score_type);
  return fetchJSON(`${BASE}/map-data?${sp}`);
}

/* POST /ai/chat */
export async function sendChatMessage(message: string, sessionId?: string): Promise<{session_id: string; response: string}> {
  return fetchJSON(`${BASE}/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

/* POST /ai/generate-insight/:id */
export async function generateInsight(regionId: number): Promise<import('./types').GenerateInsightResponse> {
  return fetchJSON(`${BASE}/ai/generate-insight/${regionId}`, { method: 'POST' });
}

/* GET /ai/report/:id — returns PDF blob */
export async function downloadReport(regionId: number): Promise<void> {
  const res = await fetch(`${BASE}/ai/report/${regionId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ProspekJawa_Report.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/* GET /ai/sentiment/:id */
export async function getSentiment(regionId: number): Promise<import('./types').SentimentData> {
  return fetchJSON(`${BASE}/ai/sentiment/${regionId}`);
}

