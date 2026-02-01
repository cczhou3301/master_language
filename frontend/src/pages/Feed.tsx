import { useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { api } from "../config";
import { getToken, authHeaders, logout, ensureValidToken } from "../lib/auth";

type Card = {
  id: number;
  external_id: string;
  title_en: string;
  title_zh: string | null;
  thumbnail_url: string;
  duration_seconds: number;
  difficulty: number;
  accent: string;
  topic: string;
  completed: boolean;
};

const DIFF = ["", "Easy", "Intermediate", "Upper", "Advanced", "Native"];
const DIFF_COLOR: Record<number, string> = { 1: "#16a34a", 2: "#ca8a04", 3: "#d97706", 4: "#dc2626", 5: "#7c2d12" };

export function Feed() {
  const [list, setList] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [logoutTick, setLogoutTick] = useState(0);

  async function handleLogout() {
    await logout(api);
    setLogoutTick((t) => t + 1);
  }

  useEffect(() => {
    let cancelled = false;
    ensureValidToken(api).then((ok) => {
      if (cancelled) return;
      if (!ok) {
        setLoading(false);
        return;
      }
      const h = authHeaders();
      fetch(api("/api/videos?limit=20"), { headers: h })
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error("Fetch failed"))))
        .then(setList)
        .catch((e) => setErr(e.message || "Could not load feed."))
        .finally(() => setLoading(false));
    });
    return () => { cancelled = true; };
  }, [logoutTick]);

  if (!getToken()) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="container">
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ margin: 0 }}>MasterLanguage</h1>
        {getToken() ? (
          <button onClick={handleLogout}>Log out</button>
        ) : (
          <span style={{ display: "flex", gap: 8 }}>
            <Link to="/login"><button>Log in</button></Link>
            <Link to="/register"><button>Register</button></Link>
          </span>
        )}
      </header>
      {err && <p style={{ color: "var(--danger)" }}>{err}</p>}
      {loading && <p>Loading…</p>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 }}>
        {list.map((v) => (
          <Link key={v.id} to={`/video/${v.id}`} style={{ color: "inherit", textDecoration: "none" }}>
            <article
              style={{
                border: "1px solid var(--border)",
                borderRadius: "var(--radius)",
                overflow: "hidden",
                background: "var(--bg)",
              }}
            >
              <div style={{ aspectRatio: "16/9", background: "#eee", position: "relative" }}>
                {v.thumbnail_url && (
                  <img src={v.thumbnail_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                )}
                <span
                  style={{
                    position: "absolute",
                    bottom: 8,
                    right: 8,
                    background: "rgba(0,0,0,0.7)",
                    color: "#fff",
                    padding: "2px 6px",
                    borderRadius: 4,
                    fontSize: 12,
                  }}
                >
                  {Math.floor(v.duration_seconds / 60)} min
                </span>
                {v.completed && (
                  <span style={{ position: "absolute", top: 8, right: 8, fontSize: 18 }}>✓</span>
                )}
              </div>
              <div style={{ padding: 12 }}>
                <div style={{ fontSize: 12, marginBottom: 4 }}>
                  <span style={{ color: DIFF_COLOR[v.difficulty] || "var(--muted)" }}>
                    {DIFF[v.difficulty] || "Lv." + v.difficulty}
                  </span>
                  {" · "}{v.accent}{v.topic ? ` · ${v.topic}` : ""}
                </div>
                <h3 style={{ margin: "0 0 4px", fontSize: "1rem" }}>{v.title_en || "Untitled"}</h3>
                {v.title_zh && <p style={{ margin: 0, color: "var(--muted)", fontSize: 14 }}>{v.title_zh}</p>}
              </div>
            </article>
          </Link>
        ))}
      </div>
    </div>
  );
}
