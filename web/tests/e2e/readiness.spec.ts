import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import path from "node:path";

const compose = path.resolve(import.meta.dirname, "../../../compose.yaml");
function database(action: "stop" | "start") {
  execFileSync("docker", ["compose", "-f", compose, action, "db"], {
    timeout: 30_000,
    stdio: "pipe",
  });
}

test("SSR follows real DB availability and recovers", async ({ page, request }) => {
  // Two bounded Docker operations plus recovery polling exceed the default 30s.
  test.setTimeout(90_000);
  await page.goto("/");
  await expect(page.getByTestId("service-status")).toHaveAttribute("data-state", "connected");
  await page.screenshot({ path: "test-results/homepage-desktop.png", fullPage: true });
  try {
    database("stop");
    const ready = await request.get("http://127.0.0.1:8009/api/v1/ready");
    expect(ready.status()).toBe(503);
    const live = await request.get("http://127.0.0.1:8009/api/v1/health");
    expect(live.status()).toBe(200);
    await page.reload();
    await expect(page.getByTestId("service-status")).toHaveAttribute("data-state", "disconnected");
    await expect(page.getByRole("status")).toHaveText("資料庫暫時無法連線");
  } finally {
    database("start");
  }
  await expect.poll(async () => {
    const response = await request.get("http://127.0.0.1:8009/api/v1/ready");
    return response.status();
  }, { timeout: 20_000 }).toBe(200);
  await page.reload();
  await expect(page.getByTestId("service-status")).toHaveAttribute("data-state", "connected");
});

test("API connection failure still renders a usable page", async ({ page }) => {
  await page.goto("http://127.0.0.1:3310");
  await expect(page.getByTestId("service-status")).toHaveAttribute("data-state", "unreachable");
  await expect(page.getByRole("status")).toHaveText("服務暫時無法連線");
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});

test("homepage fits mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: "test-results/homepage-mobile.png", fullPage: true });
});
