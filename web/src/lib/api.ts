export type User = {
  id: string; account: string; name: string; avatar: string | null;
  profile: string | null; role: "user" | "admin" | "vip";
  vip_expires_at: string | null; vip_number: string | null;
};

export async function api<T>(path: string, method = "GET", payload?: unknown): Promise<T> {
  const headers: Record<string, string> = {};
  if (method !== "GET") {
    const csrf = await fetch("/api/v1/auth/csrf", { cache: "no-store" });
    if (!csrf.ok) throw new Error("服務暫時無法使用");
    const value: { csrf_token: string } = await csrf.json();
    headers["X-CSRF-Token"] = value.csrf_token;
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(`/api/v1${path}`, {
    method, headers, cache: "no-store",
    body: payload === undefined ? undefined : JSON.stringify(payload),
  });
  if (!response.ok) {
    const value = await response.json().catch(() => ({}));
    throw new Error(typeof value.detail === "string" ? value.detail : "操作失敗");
  }
  return response.status === 204 ? undefined as T : response.json();
}
