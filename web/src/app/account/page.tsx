"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, User } from "../../lib/api";

export default function AccountPage() {
  const [user, setUser] = useState<User | null>(null);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (new URLSearchParams(window.location.search).get("mode") === "register") setMode("register");
    api<User>("/auth/me").then(setUser).catch(() => {}).finally(() => setLoading(false));
  }, []);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    setBusy(true); setMessage("");
    try {
      if (user) {
        setUser(await api<User>("/membership/redemptions", "POST", data));
        setMessage("會員兌換成功");
      } else if (mode === "register") {
        await api("/auth/register", "POST", data);
        setMode("login"); setMessage("註冊成功，請登入");
      } else {
        setUser(await api<User>("/auth/login", "POST", data));
      }
      form.reset();
    } catch (error) { setMessage((error as Error).message); }
    finally { setBusy(false); }
  }
  async function logout() {
    setBusy(true);
    try { await api("/auth/logout", "POST"); setUser(null); setMessage("已登出"); }
    catch (error) { setMessage((error as Error).message); }
    finally { setBusy(false); }
  }
  return <main>
    <header><a className="brand" href="/">Yu Picture</a></header>
    <section className="account-panel">
      <h1>{user ? "我的帳號" : mode === "login" ? "登入" : "建立帳號"}</h1>
      {loading ? <p>載入中…</p> : user ? <>
        <p>{user.name} · {user.account}</p><p>角色：{user.role}</p>
        <p><a href={`/users/${user.id}`}>查看公開個人頁</a></p>
        {user.vip_expires_at && <p>會員期限：{new Date(user.vip_expires_at).toLocaleDateString("zh-TW")}</p>}
        <form onSubmit={submit}>
          <label>會員兌換碼<input name="code" required maxLength={128} autoComplete="off" /></label>
          <button disabled={busy}>兌換會員</button>
        </form>
        {user.role === "admin" && <p><a href="/admin/users">管理使用者</a></p>}
        <button onClick={logout} disabled={busy}>登出</button>
      </> : <>
        <form onSubmit={submit} key={mode}>
          <label>帳號<input name="account" required minLength={4} maxLength={256} autoComplete="username" /></label>
          <label>密碼<input name="password" type="password" required minLength={8} maxLength={128} autoComplete={mode === "login" ? "current-password" : "new-password"} /></label>
          {mode === "register" && <label>確認密碼<input name="confirm_password" type="password" required minLength={8} maxLength={128} autoComplete="new-password" /></label>}
          <button disabled={busy}>{mode === "login" ? "登入" : "註冊"}</button>
        </form>
        <button disabled={busy} onClick={() => { setMode(mode === "login" ? "register" : "login"); setMessage(""); }}>{mode === "login" ? "建立帳號" : "已有帳號，登入"}</button>
      </>}
      <p role="status">{message}</p>
    </section>
  </main>;
}
