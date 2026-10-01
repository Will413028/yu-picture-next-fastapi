import { NextRequest } from "next/server";

type Context = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: Context) {
  const { path } = await context.params;
  const base = process.env.API_BASE_URL ?? "http://127.0.0.1:8009";
  const target = new URL(`/api/v1/${path.map(encodeURIComponent).join("/")}`, base);
  target.search = request.nextUrl.search;
  const headers = new Headers();
  for (const name of ["cookie", "content-type", "origin", "x-csrf-token"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  if (Number(request.headers.get("content-length")) > 16384) {
    return Response.json({ detail: "請求內容過大" }, { status: 413 });
  }
  const body = ["GET", "HEAD"].includes(request.method)
    ? undefined : await request.arrayBuffer();
  if (body && body.byteLength > 16384) {
    return Response.json({ detail: "請求內容過大" }, { status: 413 });
  }
  try {
    const upstream = await fetch(target, {
      method: request.method, headers, body, cache: "no-store",
      redirect: "manual", signal: AbortSignal.timeout(10000),
    });
    const outgoing = new Headers({ "Cache-Control": "no-store" });
    const contentType = upstream.headers.get("content-type");
    if (contentType) outgoing.set("content-type", contentType);
    for (const cookie of upstream.headers.getSetCookie()) outgoing.append("set-cookie", cookie);
    return new Response(upstream.body, { status: upstream.status, headers: outgoing });
  } catch {
    return Response.json({ detail: "服務暫時無法使用" }, { status: 503 });
  }
}

export { proxy as GET, proxy as POST, proxy as PATCH, proxy as DELETE };
