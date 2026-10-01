import { defineConfig } from "@playwright/test";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  timeout: 30_000,
  use: { baseURL: "http://127.0.0.1:3309", screenshot: "only-on-failure" },
  webServer: [
    {
      command: "make dev-api",
      cwd: root,
      url: "http://127.0.0.1:8009/api/v1/health",
      reuseExistingServer: false,
      timeout: 90_000,
    },
    {
      command: "pnpm start",
      env: { API_BASE_URL: "http://127.0.0.1:8009" },
      url: "http://127.0.0.1:3309",
      reuseExistingServer: false,
      timeout: 90_000,
    },
    {
      command: "pnpm exec next start --hostname 127.0.0.1 --port 3310",
      env: { API_BASE_URL: "http://127.0.0.1:1" },
      url: "http://127.0.0.1:3310",
      reuseExistingServer: false,
      timeout: 90_000,
    },
  ],
});
