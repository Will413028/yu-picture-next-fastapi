"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, User } from "../../../lib/api";

type Page = { items: User[]; total: number; page: number; page_size: number };
export default function UsersPage() {
  const [result, setResult] = useState<Page | null>(null);
  const [message, setMessage] = useState("");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [editing, setEditing] = useState<User | null>(null);
  const [busy, setBusy] = useState(false);
  async function load(filter = query, number = page) {
    try {
      setResult(await api<Page>(`/admin/users?page=${number}&page_size=20&${filter}`));
      setMessage("");
    } catch (error) { setResult(null); setMessage((error as Error).message); }
  }
  useEffect(() => { void load(); }, []); // Initial permissions are checked by the API.
  function search(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const params = new URLSearchParams();
    new FormData(event.currentTarget).forEach((value, key) => {
      if (typeof value === "string" && value) params.set(key, value);
    });
    const filter = params.toString();
    setQuery(filter); setPage(1); void load(filter, 1);
  }
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const payload = Object.fromEntries(new FormData(form));
    setBusy(true);
    try {
      await api(editing ? `/admin/users/${editing.id}` : "/admin/users", editing ? "PATCH" : "POST", payload);
      form.reset(); setEditing(null); await load(); setMessage("已儲存");
    } catch (error) { setMessage((error as Error).message); }
    finally { setBusy(false); }
  }
  async function remove(user: User) {
    if (!window.confirm(`刪除使用者 ${user.name}？`)) return;
    setBusy(true);
    try { await api(`/admin/users/${user.id}`, "DELETE"); await load(); }
    catch (error) { setMessage((error as Error).message); }
    finally { setBusy(false); }
  }
  return <main>
    <header><a className="brand" href="/">Yu Picture</a><a className="account-link" href="/account">我的帳號</a></header>
    <h1 style={{ fontSize: 36 }}>使用者管理</h1><p role="status">{message}</p>
    {result && <>
      <form onSubmit={search} className="admin-grid">
        <label>ID<input name="id" type="number" min="1" /></label>
        <label>帳號<input name="account" /></label><label>名稱<input name="name" /></label>
        <label>簡介<input name="profile" /></label>
        <label>角色<select name="role"><option value="">全部</option><option>user</option><option>vip</option><option>admin</option></select></label>
        <label>排序<select name="sort"><option value="created_at">建立時間</option><option value="updated_at">更新時間</option><option value="account">帳號</option><option value="name">名稱</option><option value="role">角色</option><option value="id">ID</option></select></label>
        <label>方向<select name="direction"><option value="desc">遞減</option><option value="asc">遞增</option></select></label>
        <button disabled={busy}>搜尋</button>
      </form>
      <div className="table-scroll"><table><thead><tr><th>帳號</th><th>名稱</th><th>角色</th><th>操作</th></tr></thead><tbody>
        {result.items.map(user => <tr key={user.id}><td>{user.account}</td><td>{user.name}</td><td>{user.role}</td><td><button disabled={busy} onClick={() => setEditing(user)}>編輯</button> <button disabled={busy} onClick={() => void remove(user)}>刪除</button></td></tr>)}
      </tbody></table></div>
      <p>共 {result.total} 位 · 第 {page} 頁</p>
      <button disabled={busy || page === 1} onClick={() => { setPage(page - 1); void load(query, page - 1); }}>上一頁</button>{" "}
      <button disabled={busy || page * 20 >= result.total} onClick={() => { setPage(page + 1); void load(query, page + 1); }}>下一頁</button>
      <h2>{editing ? "編輯使用者" : "新增使用者"}</h2>
      <form onSubmit={save} key={editing?.id ?? "new"} className="admin-grid">
        {!editing && <><label>帳號<input name="account" required minLength={4} maxLength={256} autoComplete="off" /></label><label>初始密碼<input name="password" type="password" required minLength={8} maxLength={128} autoComplete="new-password" /></label></>}
        <label>名稱<input name="name" defaultValue={editing?.name ?? "無名"} maxLength={256} /></label>
        <label>頭像 URL<input name="avatar" defaultValue={editing?.avatar ?? ""} maxLength={1024} /></label>
        <label>簡介<input name="profile" defaultValue={editing?.profile ?? ""} maxLength={512} /></label>
        <label>角色<select name="role" defaultValue={editing?.role ?? "user"}><option>user</option><option>vip</option><option>admin</option></select></label>
        <button disabled={busy}>儲存</button>
        {editing && <button type="button" disabled={busy} onClick={() => setEditing(null)}>取消編輯</button>}
      </form>
    </>}
  </main>;
}
