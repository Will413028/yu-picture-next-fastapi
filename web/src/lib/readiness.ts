import "server-only";

export type ServiceState = "connected" | "disconnected" | "unreachable";

export async function getServiceState(): Promise<ServiceState> {
  const base = process.env.API_BASE_URL ?? "http://127.0.0.1:8009";
  try {
    const response = await fetch(`${base}/api/v1/ready`, {
      cache: "no-store",
      signal: AbortSignal.timeout(4000),
    });
    const body: unknown = await response.json();
    if (typeof body !== "object" || body === null) return "unreachable";
    if (response.status === 200 && "status" in body && body.status === "ready"
      && "database" in body && body.database === "connected") return "connected";
    if (response.status === 503 && "status" in body && body.status === "unavailable"
      && "database" in body && body.database === "disconnected") return "disconnected";
    return "unreachable";
  } catch {
    return "unreachable";
  }
}
