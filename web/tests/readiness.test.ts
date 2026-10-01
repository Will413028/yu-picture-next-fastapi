import assert from "node:assert/strict";
import { createServer } from "node:http";
import { test } from "node:test";
import { getServiceState } from "../src/lib/readiness.ts";

test("transport errors produce unreachable", async (t) => {
  t.mock.method(globalThis, "fetch", async () => { throw new TypeError("connection failed"); });
  assert.equal(await getServiceState(), "unreachable");
});

test("request timeout produces unreachable with bounded deadline", async (t) => {
  const server = createServer(() => {});
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  assert.ok(address && typeof address !== "string");
  const previousBase = process.env.API_BASE_URL;
  process.env.API_BASE_URL = `http://127.0.0.1:${address.port}`;
  const timeout = AbortSignal.timeout.bind(AbortSignal);
  const probe = t.mock.method(AbortSignal, "timeout", () => timeout(20));
  try {
    assert.equal(await getServiceState(), "unreachable");
    assert.deepEqual(probe.mock.calls[0].arguments, [4000]);
  } finally {
    if (previousBase === undefined) delete process.env.API_BASE_URL;
    else process.env.API_BASE_URL = previousBase;
    server.closeAllConnections();
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
});

test("unexpected status or malformed schema cannot report ready", async (t) => {
  t.mock.method(globalThis, "fetch", async () => new Response('{"status":"ready","database":"connected"}', { status: 500 }));
  assert.equal(await getServiceState(), "unreachable");
  t.mock.method(globalThis, "fetch", async () => new Response('{"status":"ready"}', { status: 200 }));
  assert.equal(await getServiceState(), "unreachable");
});
