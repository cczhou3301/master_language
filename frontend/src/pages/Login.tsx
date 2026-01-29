import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../config";
import { setToken, setUserId, setLevel } from "../lib/auth";

export function Login() {
  const [step, setStep] = useState<"login" | "device-block">("login");
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [deviceId] = useState(() => `web-${Math.random().toString(36).slice(2, 12)}`);
  const [deviceName] = useState(() => navigator.userAgent.slice(0, 48) || "Web");
  const [err, setErr] = useState("");
  const [activeDevices, setActiveDevices] = useState<Array<{ device_name: string }>>([]);
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    const res = await fetch(api("/api/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login: login.trim(), password, device_id: deviceId, device_name: deviceName }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok) {
      setToken(data.access_token);
      setUserId(data.user_id);
      if (data.level != null) setLevel(data.level);
      navigate("/");
      return;
    }
    if (res.status === 403 && data.code === "DEVICE_LIMIT_REACHED") {
      setStep("device-block");
      setActiveDevices(data.active_devices || []);
      setErr(data.message || "Account is in use on 3 devices. Log out on one device to continue.");
      return;
    }
    setErr(data.detail?.message || data.message || "Login failed.");
  }

  if (step === "device-block") {
    return (
      <div className="container" style={{ paddingTop: 48 }}>
        <div style={{ maxWidth: 400, margin: "0 auto" }}>
          <h2>Device limit reached</h2>
          <p style={{ color: "var(--muted)" }}>{err}</p>
          <ul>
            {activeDevices.map((d, i) => (
              <li key={i}>{d.device_name || "Unknown device"}</li>
            ))}
          </ul>
          <p>Log out on one of these devices, then try again.</p>
          <button type="button" onClick={() => { setStep("login"); setErr(""); }}>Back</button>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ paddingTop: 48 }}>
      <div style={{ maxWidth: 360, margin: "0 auto" }}>
        <h1>MasterLanguage</h1>
        <p style={{ color: "var(--muted)", marginBottom: 24 }}>Log in with phone or email and password.</p>
        <form onSubmit={onSubmit}>
          <label style={{ display: "block", marginBottom: 8 }}>Phone or email</label>
          <input
            type="text"
            inputMode="email"
            autoComplete="username"
            value={login}
            onChange={(e) => setLogin(e.target.value.slice(0, 255))}
            placeholder="Phone number or email"
            required
          />
          <label style={{ display: "block", marginTop: 16, marginBottom: 8 }}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {err && <p style={{ color: "var(--danger)", marginTop: 12 }}>{err}</p>}
          <button type="submit" className="primary" style={{ marginTop: 24, width: "100%", maxWidth: 320 }}>
            Log in
          </button>
        </form>
        <p style={{ marginTop: 24 }}>
          <a href="/register">Register</a> · <a href="/">Feed</a>
        </p>
      </div>
    </div>
  );
}
