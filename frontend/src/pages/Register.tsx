import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../config";
import { setToken, setUserId, setLevel } from "../lib/auth";

export function Register() {
  const [step, setStep] = useState<1 | 2>(1);
  const [code, setCode] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  async function onValidate(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    const res = await fetch(api("/api/auth/activation/validate"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.trim() }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.valid) {
      setStep(2);
      return;
    }
    setErr(data.detail?.message || data.message || "Invalid or already used code.");
  }

  async function onRegister(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    const p = phone.trim() || undefined;
    const em = email.trim() || undefined;
    if (!p && !em) {
      setErr("Please enter at least one of phone or email.");
      return;
    }
    const res = await fetch(api("/api/auth/activation/register"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.trim(), phone: p, email: em, password }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      setToken(data.access_token);
      setUserId(data.user_id);
      if (data.level != null) setLevel(data.level);
      navigate("/");
      return;
    }
    setErr(data.detail?.message || data.message || "Registration failed.");
  }

  return (
    <div className="container" style={{ paddingTop: 48 }}>
      <div style={{ maxWidth: 360, margin: "0 auto" }}>
        <h1>MasterLanguage — Register</h1>
        <p style={{ color: "var(--muted)", marginBottom: 24 }}>
          Invite-only. Enter your activation code.
        </p>

        {step === 1 && (
          <form onSubmit={onValidate}>
            <label style={{ display: "block", marginBottom: 8 }}>Activation code</label>
            <input
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="e.g. DEV001"
              required
            />
            {err && <p style={{ color: "var(--danger)", marginTop: 12 }}>{err}</p>}
            <button type="submit" className="primary" style={{ marginTop: 24, width: "100%", maxWidth: 320 }}>
              Validate
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={onRegister}>
            <p style={{ color: "var(--success)", marginBottom: 16 }}>Code validated. Set your account (at least one of phone or email).</p>
            <label style={{ display: "block", marginBottom: 8 }}>Phone (optional, up to 32 chars)</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value.slice(0, 32))}
              placeholder="e.g. 13800138000 or +8613800138000"
            />
            <label style={{ display: "block", marginTop: 16, marginBottom: 8 }}>Email (optional)</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value.slice(0, 255))}
              placeholder="you@example.com"
            />
            <label style={{ display: "block", marginTop: 16, marginBottom: 8 }}>Password (6+ chars)</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
            {err && <p style={{ color: "var(--danger)", marginTop: 12 }}>{err}</p>}
            <button
              type="submit"
              className="primary"
              style={{ marginTop: 24, width: "100%", maxWidth: 320 }}
              disabled={!phone.trim() && !email.trim()}
            >
              Create account
            </button>
            <button type="button" style={{ marginTop: 8 }} onClick={() => { setStep(1); setErr(""); }}>
              Back
            </button>
          </form>
        )}

        <p style={{ marginTop: 24 }}>
          <Link to="/login">Log in</Link> · <Link to="/">Feed</Link>
        </p>
      </div>
    </div>
  );
}
