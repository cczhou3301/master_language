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

function getDeviceFingerprintId(): string {
  const n = typeof navigator !== "undefined" ? navigator : { userAgent: "", language: "", platform: "", languages: [] as string[], hardwareConcurrency: 0, deviceMemory: 0 };
  const s = typeof screen !== "undefined" ? screen : { width: 0, height: 0, colorDepth: 0, pixelDepth: 0 };
  const parts = [
    n.userAgent || "",
    n.language || "",
    Array.isArray(n.languages) ? n.languages.join(",") : "",
    n.platform || "",
    String(s.width ?? 0),
    String(s.height ?? 0),
    String(s.colorDepth ?? 0),
    String(s.pixelDepth ?? 0),
    String(new Date().getTimezoneOffset()),
    String(n.hardwareConcurrency ?? 0),
    String((n as { deviceMemory?: number }).deviceMemory ?? ""),
  ];
  const str = parts.join("|");
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h + str.charCodeAt(i)) | 0;
  }
  const hex = Math.abs(h).toString(16).slice(0, 12);
  return "web-" + (hex || "0");
}

function getDeviceName(): string {
  if (typeof navigator === "undefined") return "Web";
  return (navigator.userAgent || "Web").slice(0, 48);
}

export function Login() {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [deviceId] = useState(getDeviceFingerprintId);
  const [deviceName] = useState(getDeviceName);
  const [err, setErr] = useState("");
  const [isDeviceLimit, setIsDeviceLimit] = useState(false);
  const navigate = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setIsDeviceLimit(false);
    const res = await fetch(api("/api/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ login: login.trim(), password, device_id: deviceId, device_name: deviceName }),
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
    const isLimit = res.status === 403 && (payload.code === "DEVICE_LIMIT_REACHED" || data.code === "DEVICE_LIMIT_REACHED");
    setIsDeviceLimit(!!isLimit);
    setErr(payload.message || data.detail?.message || data.message || "Login failed.");
  }

  return (
    <div className="bg-background-light dark:bg-background-dark min-h-screen flex items-center justify-center p-4 transition-colors duration-200">
      <button className="fixed top-6 right-6 p-2 rounded-full bg-white dark:bg-slate-800 shadow-lg text-slate-600 dark:text-slate-300 hover:scale-110 transition-transform" type="button" onClick={() => document.documentElement.classList.toggle("dark")}>
        <span className="material-symbols-outlined">dark_mode</span>
      </button>
      <div className="w-full max-w-[440px] bg-white dark:bg-slate-900 shadow-2xl shadow-slate-200/50 dark:shadow-none rounded-3xl p-8 md:p-12">
        <div className="flex flex-col items-center mb-10">
          <div className="w-16 h-16 bg-brand rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 mb-6">
            <span className="material-symbols-outlined text-white text-4xl">school</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-800 dark:text-white mb-2 tracking-tight">Master English!</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm">专业英语口语学习平台</p>
        </div>
        <div className={"mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 rounded-xl" + (err ? "" : " hidden")}>
          <p className="text-red-600 dark:text-red-400 text-sm leading-relaxed">
            {isDeviceLimit ? "您的账号已在多台设备上登录，已达上限。请先退出其他设备后再登录。" : err}
          </p>
        </div>
        <form className="space-y-6" onSubmit={onSubmit}>
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2" htmlFor="username">手机号或邮箱</label>
            <div className="relative">
              <input className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border-2 border-slate-100 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-teal-200 dark:focus:ring-teal-900 focus:border-teal-400 dark:focus:border-teal-600 outline-none transition-all text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500" id="username" name="username" placeholder="请输入手机号或电子邮箱" type="text" value={login} onChange={(e) => setLogin(e.target.value.slice(0, 255))} required />
            </div>
          </div>
          <div>
            <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2" htmlFor="password">密码</label>
            <div className="relative">
              <input className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border-2 border-slate-100 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-teal-200 dark:focus:ring-teal-900 focus:border-teal-400 dark:focus:border-teal-600 outline-none transition-all text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500" id="password" name="password" placeholder="请输入密码" type="password" value={password} onChange={(e) => setPassword(truncateToMaxBytes(e.target.value, PASSWORD_MAX_BYTES))} required />
            </div>
          </div>
          <button className="gradient-btn w-full py-4 rounded-xl text-slate-800 font-bold text-lg shadow-md hover:shadow-lg hover:opacity-90 transition-all active:scale-[0.98] mt-2" type="submit">
            登录
          </button>
        </form>
        <div className="mt-10 pt-8 border-t border-slate-100 dark:border-slate-800 text-center">
          <p className="text-slate-500 dark:text-slate-400 text-sm">
            还没有账户？
            <Link className="text-blue-600 dark:text-blue-400 font-semibold hover:underline ml-1" to="/register">立即注册</Link>
          </p>
        </div>
      </div>
      <div className="fixed bottom-6 text-center text-slate-400 dark:text-slate-500 text-xs px-4">
        <p>没有激活码，请联系微信：<span className="font-medium text-slate-600 dark:text-slate-400">masterLanguage</span></p>
      </div>
    </div>
  );
}
