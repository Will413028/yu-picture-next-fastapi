import { expect, test } from "@playwright/test";
import { createHash, randomBytes } from "node:crypto";
import { execFileSync } from "node:child_process";
import path from "node:path";

test.setTimeout(90_000);

function fixture(account: string, action: "promote" | "cleanup" | "code", digest?: string) {
  execFileSync("uv", ["--directory", path.resolve(import.meta.dirname, "../../../api"), "run", "--frozen", "python", "-m", "tests.browser_fixture"], {
    input: JSON.stringify({ account, action, digest }), stdio: ["pipe", "pipe", "pipe"],
    timeout: 35_000,
    env: { ...process.env, APP_ENV: "local", DATABASE_URL: "postgresql+psycopg://postgres@127.0.0.1:55479/yupicture" },
  });
}

test("register, login, reload and logout through same-origin proxy", async ({ page }) => {
  const account = `e2e_${randomBytes(8).toString("hex")}`;
  const password = randomBytes(24).toString("base64url");
  const code = randomBytes(24).toString("base64url");
  const codeDigest = createHash("sha256").update(code).digest("hex");
  try {
  await page.goto("/account");
  await expect(page.getByRole("button", { name: "建立帳號" })).toBeVisible();
  await page.screenshot({ path: "test-results/account-desktop.png", fullPage: true });
  await page.getByRole("button", { name: "建立帳號" }).click();
  await page.getByLabel("帳號", { exact: true }).fill(account);
  await page.getByLabel("密碼", { exact: true }).fill(password);
  await page.getByLabel("確認密碼").fill(password);
  await page.getByRole("button", { name: "註冊", exact: true }).click();
  await expect(page.getByRole("status")).toHaveText("註冊成功，請登入");
  await page.getByLabel("帳號", { exact: true }).fill(account);
  await page.getByLabel("密碼", { exact: true }).fill(password);
  await page.getByRole("button", { name: "登入", exact: true }).click();
  await expect(page.getByRole("heading", { name: "我的帳號" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: "我的帳號" })).toBeVisible();
  fixture(account, "code", codeDigest);
  await page.getByLabel("會員兌換碼").fill(code);
  await page.getByRole("button", { name: "兌換會員" }).click();
  await expect(page.getByRole("status")).toHaveText("會員兌換成功");
  await expect(page.getByText("角色：vip", { exact: true })).toBeVisible();
  await page.getByRole("link", { name: "查看公開個人頁" }).click();
  await expect(page.getByRole("heading", { name: "無名", exact: true })).toBeVisible();
  await page.goto("/account");
  await expect(page.getByRole("heading", { name: "我的帳號" })).toBeVisible();
  await page.getByRole("button", { name: "登出", exact: true }).click();
  await expect(page.getByRole("heading", { name: "登入", exact: true })).toBeVisible();
  } finally { fixture(account, "cleanup", codeDigest); }
});

test("administrator manages a user through the browser", async ({ page }) => {
  const account = `e2e_${randomBytes(8).toString("hex")}`;
  const other = `e2e_${randomBytes(8).toString("hex")}`;
  const password = randomBytes(24).toString("base64url");
  try {
    await page.goto("/account");
    await page.getByRole("button", { name: "建立帳號" }).click();
    await page.getByLabel("帳號", { exact: true }).fill(account);
    await page.getByLabel("密碼", { exact: true }).fill(password);
    await page.getByLabel("確認密碼").fill(password);
    await page.getByRole("button", { name: "註冊", exact: true }).click();
    await expect(page.getByRole("status")).toHaveText("註冊成功，請登入");
    fixture(account, "promote");
    await page.getByLabel("帳號", { exact: true }).fill(account);
    await page.getByLabel("密碼", { exact: true }).fill(password);
    await page.getByRole("button", { name: "登入", exact: true }).click();
    await page.getByRole("link", { name: "管理使用者" }).click();
    await expect(page.getByRole("button", { name: "儲存" })).toBeVisible();
    const create = page.locator("form").last();
    await create.getByLabel("帳號", { exact: true }).fill(other);
    await create.getByLabel("初始密碼").fill(randomBytes(24).toString("base64url"));
    await create.getByLabel("名稱", { exact: true }).fill("瀏覽器測試");
    await create.getByRole("button", { name: "儲存" }).click();
    await expect(page.getByRole("status")).toHaveText("已儲存");
    const row = page.getByRole("row").filter({ hasText: other });
    await row.getByRole("button", { name: "編輯" }).click();
    await page.locator("form").last().getByLabel("名稱", { exact: true }).fill("更新測試");
    await page.getByRole("button", { name: "儲存" }).click();
    await expect(row).toContainText("更新測試");
    page.once("dialog", dialog => dialog.accept());
    await row.getByRole("button", { name: "刪除" }).click();
    await expect(row).toHaveCount(0);
  } finally { fixture(other, "cleanup"); fixture(account, "cleanup"); }
});

test("ordinary visitor cannot use administration", async ({ page }) => {
  await page.goto("/admin/users");
  await expect(page.getByRole("status")).toHaveText("請先登入");
  await expect(page.getByRole("button", { name: "儲存" })).toHaveCount(0);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/account");
  await expect(page.getByRole("button", { name: "登入", exact: true })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: "test-results/account-mobile.png", fullPage: true });
});
