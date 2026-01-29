const TOKEN_KEY = "ml_token";
const UID_KEY = "ml_uid";
const LEVEL_KEY = "ml_level";

export function getToken(): string | null {
  return typeof localStorage !== "undefined" ? localStorage.getItem(TOKEN_KEY) : null;
}
export function setToken(t: string): void {
  localStorage.setItem(TOKEN_KEY, t);
}
export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(UID_KEY);
  localStorage.removeItem(LEVEL_KEY);
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
