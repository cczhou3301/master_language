const TOKEN_KEY = "ml_token";
const UID_KEY = "ml_uid";
const LEVEL_KEY = "ml_level";
const REFRESH_TOKEN_KEY = "ml_refresh_token";

/** Decode JWT payload without verification (client-side). Returns { exp } or null. */
function decodeJwtPayload(token: string): { exp?: number } | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const json = atob(base64);
    return JSON.parse(json) as { exp?: number };
  } catch {
    return null;
  }
}

/** True if access token is missing or expired (with optional buffer seconds before exp). */
export function isAccessTokenExpired(token: string | null, bufferSeconds = 60): boolean {
  if (!token) return true;
  const payload = decodeJwtPayload(token);
  if (!payload || payload.exp == null) return true;
  return Date.now() / 1000 >= payload.exp - bufferSeconds;
}

export function getToken(): string | null {
  return typeof localStorage !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
}
export function setToken(t: string): void {
  localStorage.setItem(TOKEN_KEY, t);
}
export function getRefreshToken(): string | null {
  return typeof localStorage !== "undefined" ? localStorage.getItem(REFRESH_TOKEN_KEY) : null;
}
export function setRefreshToken(t: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, t);
}
export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(UID_KEY);
  localStorage.removeItem(LEVEL_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
export function setUserId(id: number): void {
  localStorage.setItem(UID_KEY, String(id));
}
export function getUserId(): number | null {
  const s = localStorage.getItem(UID_KEY);
  return s ? parseInt(s, 10) : null;
}
export function setLevel(level: number): void {
  localStorage.setItem(LEVEL_KEY, String(level));
}
export function getLevel(): number {
  const s = typeof localStorage !== "undefined" ? localStorage.getItem(LEVEL_KEY) : null;
  return s ? parseInt(s, 10) : 0;
}

export function authHeaders(): Record<string, string> {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export type ApiUrlFn = (path: string) => string;

/**
 * Ensure we have a valid access token. If current token is expired, call refresh and store new one.
 * Returns true if caller can proceed with auth (token valid or refreshed); false if user must log in again.
 */
export async function ensureValidToken(apiBaseUrl: ApiUrlFn): Promise<boolean> {
  const token = getToken();
  const refreshToken = getRefreshToken();
  if (!token && !refreshToken) return false;
  if (token && !isAccessTokenExpired(token)) return true;
  if (!refreshToken) {
    clearAuth();
    return false;
  }
  try {
    const res = await fetch(apiBaseUrl("/api/auth/refresh"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const data = (await res.json().catch(() => ({}))) as { access_token?: string; refresh_token?: string; user_id?: number; level?: number };
    if (!res.ok) {
      clearAuth();
      return false;
    }
    if (data.access_token) setToken(data.access_token);
    if (data.refresh_token) setRefreshToken(data.refresh_token);
    if (data.user_id != null) setUserId(data.user_id);
    if (data.level != null) setLevel(data.level);
    return true;
  } catch {
    clearAuth();
    return false;
  }
}

/**
 * Call backend logout to revoke refresh token, then clear local auth.
 * Call this when user clicks "Log out". No-op if no refresh token.
 */
export async function logout(apiBaseUrl: (path: string) => string): Promise<void> {
  const refreshToken = getRefreshToken();
  if (refreshToken) {
    try {
      await fetch(apiBaseUrl("/api/auth/logout"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } catch {
      // ignore network errors; still clear local auth
    }
  }
  clearAuth();
}
