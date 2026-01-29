/**
 * API base URL: switch via .env
 * - .env.development: VITE_API_BASE=http://localhost:8000
 * - .env.production:  VITE_API_BASE=https://api.masterlanguage.com
 */
const VITE_API_BASE = typeof import.meta.env !== "undefined" && import.meta.env?.VITE_API_BASE;
export const API_BASE = (VITE_API_BASE || "").replace(/\/$/, "") || "http://localhost:8000";

export function api(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${p}`;
}
