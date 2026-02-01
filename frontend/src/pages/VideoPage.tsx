import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../config";
import { authHeaders, ensureValidToken } from "../lib/auth";

type Sub = { id: number; start_ms: number; end_ms: number; text_en: string; text_zh: string };
type Video = {
  id: number;
  external_id: string;
  title_en: string;
  title_zh: string | null;
  thumbnail_url: string;
  duration_seconds: number;
  difficulty: number;
  accent: string;
  topic: string;
  subtitle_lines: Sub[];
};

export function VideoPage() {
  const { id } = useParams<{ id: string }>();
  const [v, setV] = useState<Video | null>(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    ensureValidToken(api).then((ok) => {
      if (cancelled) return;
      if (!ok) {
        setErr("Session expired. Please log in again.");
        return;
      }
      fetch(api(`/api/videos/${id}`), { headers: authHeaders() })
        .then((r) => (r.ok ? r.json() : Promise.reject(new Error("Not found"))))
        .then(setV)
        .catch((e) => setErr(e.message || "Could not load video."));
    });
    return () => { cancelled = true; };
  }, [id]);

  if (err) return <div className="container"><p style={{ color: "var(--danger)" }}>{err}</p><Link to="/">Back</Link></div>;
  if (!v) return <div className="container"><p>Loading…</p></div>;

  return (
    <div className="container">
      <p><Link to="/">← Back</Link></p>
      <h1>{v.title_en}</h1>
      {v.title_zh && <p style={{ color: "var(--muted)" }}>{v.title_zh}</p>}
      <p style={{ fontSize: 14 }}>Lv.{v.difficulty} · {v.accent} · {v.topic} · {Math.floor(v.duration_seconds / 60)} min</p>
      {/* PRD 2.1–2.2: video player + subtitle stream. Here: placeholder + subtitle list. */}
      <div style={{ aspectRatio: "16/9", background: "#111", borderRadius: "var(--radius)", marginBottom: 24, display: "flex", alignItems: "center", justifyContent: "center", color: "#666" }}>
        Video player (embed or HLS); ID: {v.external_id}
      </div>
      <h3>Subtitles (Intensive reading)</h3>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {v.subtitle_lines.map((s) => (
          <li
            key={s.id}
            style={{
              padding: "12px 0",
              borderBottom: "1px solid var(--border)",
              display: "grid",
              gap: 4,
            }}
          >
            <span style={{ fontSize: 12, color: "var(--muted)" }}>
              {(s.start_ms / 1000).toFixed(1)}s – {(s.end_ms / 1000).toFixed(1)}s
            </span>
            <span>{s.text_en}</span>
            {s.text_zh && <span style={{ color: "var(--muted)" }}>{s.text_zh}</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
