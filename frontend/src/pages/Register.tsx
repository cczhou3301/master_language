import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../config";
import { setToken, setRefreshToken, setUserId, setLevel } from "../lib/auth";

const PASSWORD_MAX_BYTES = 20;

function truncateToMaxBytes(str: string, maxBytes: number): string {
  const encoder = new TextEncoder();
  if (encoder.encode(str).length <= maxBytes) return str;
  let end = str.length;
  while (end > 0 && encoder.encode(str.slice(0, end)).length > maxBytes) end--;
  return str.slice(0, end);
}

export function Register() {
  const [code, setCode] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [err, setErr] = useState("");
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    if (password !== confirmPassword) {
      setErr("Passwords do not match.");
      return;
    }
    const res = await fetch(api("/api/auth/activation/register"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code.trim(), phone: phone.trim(), email: email.trim(), password }),
    });
    const data = await res.json().catch(() => ({}));
    const payload = typeof data.detail === "object" && data.detail != null ? data.detail : data;
    if (res.ok) {
      setToken(data.access_token);
      if (data.refresh_token) setRefreshToken(data.refresh_token);
      setUserId(data.user_id);
      if (data.level != null) setLevel(data.level);
      navigate("/");
      return;
    }
    setErr(payload.message || data.detail?.message || data.message || "Registration failed.");
  }

  const inputClass =
    "w-full px-4 py-3 pr-11 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 text-slate-900 dark:text-white placeholder:text-slate-400 focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all";
  const labelClass = "block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1.5 px-0.5";
  const iconClass = "material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg pointer-events-none select-none";

  return (
    <div className="bg-background-light dark:bg-background-dark min-h-screen flex items-center justify-center p-4 sm:p-6">
      <div className="w-full max-w-[480px] bg-white dark:bg-slate-900 shadow-lg shadow-slate-200/60 dark:shadow-none rounded-3xl p-8 md:p-12 transition-colors duration-300">
        {/* Header: icon + title + subtitle */}
        <div className="flex flex-col items-center mb-8 text-center">
          <div className="mb-4 bg-blue-50 dark:bg-blue-900/30 p-4 rounded-2xl inline-flex">
            <span className="material-symbols-outlined text-5xl text-blue-600 dark:text-blue-400">school</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-800 dark:text-white mb-2">Master English!</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">Join our community and master your English speaking skills.</p>
        </div>

        {err && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 rounded-xl">
            <p className="text-red-600 dark:text-red-400 text-sm leading-relaxed">{err}</p>
          </div>
        )}

        <form className="space-y-5" onSubmit={onSubmit}>
          {/* Activation Code */}
          <div>
            <div className="flex flex-wrap justify-between items-end gap-1 mb-1.5 px-0.5">
              <label className={labelClass}>Activation Code</label>
              <span className="text-[11px] text-slate-500 dark:text-slate-400 leading-tight">
                (How to get? Contact WeChat: <span className="text-blue-600 dark:text-blue-400 font-medium">masterLanguage</span>)
              </span>
            </div>
            <div className="relative">
              <input className={inputClass} placeholder="Enter your activation code" required type="text" value={code} onChange={(e) => setCode(e.target.value)} />
              <span className={iconClass}>key</span>
            </div>
          </div>

          {/* Email Address */}
          <div>
            <label className={labelClass}>Email Address</label>
            <div className="relative">
              <input className={inputClass} placeholder="example@email.com" required type="email" value={email} onChange={(e) => setEmail(e.target.value.slice(0, 255))} />
              <span className={iconClass}>mail</span>
            </div>
          </div>

          {/* Phone Number */}
          <div>
            <label className={labelClass}>Phone Number</label>
            <div className="relative">
              <input className={inputClass} placeholder="Your phone number" required type="tel" value={phone} onChange={(e) => setPhone(e.target.value.slice(0, 32))} />
              <span className={iconClass}>call</span>
            </div>
          </div>

          {/* Password */}
          <div>
            <label className={labelClass}>Password</label>
            <div className="relative">
              <input className={inputClass} placeholder="Create a password" required type="password" value={password} onChange={(e) => setPassword(truncateToMaxBytes(e.target.value, PASSWORD_MAX_BYTES))} />
              <span className={iconClass}>lock</span>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className={labelClass}>Confirm Password</label>
            <div className="relative">
              <input className={inputClass} placeholder="Confirm your password" required type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(truncateToMaxBytes(e.target.value, PASSWORD_MAX_BYTES))} />
              <span className={iconClass}>lock_reset</span>
            </div>
          </div>

          <button
            type="submit"
            className="w-full mt-6 gradient-button hover:opacity-95 active:scale-[0.98] text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-blue-500/25"
          >
            Create My Account
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 text-center">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Already have an account? <Link className="text-blue-600 dark:text-blue-400 font-semibold hover:underline" to="/login">Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
