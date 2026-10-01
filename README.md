# yu-picture-next-fastapi

以 Next.js 與 FastAPI 完整重做 [yu-picture](https://github.com/liyupi/yu-picture) 的學習專案。

## 已選定的架構

- Next.js + TypeScript：UI 與 SSR。
- FastAPI：統一承接業務 API，使用模組化單體。
- PostgreSQL：全新資料庫，不搬移既有系統資料。
- API：保留功能，重新設計 REST API，不要求舊 client 相容。
- 儲存：S3-compatible，圖片處理由應用與 worker 負責；實際供應商待選。
- 原專案作為功能與行為參考；既有缺陷需明確盤點與修正。
- 物件儲存供應商與正式部署方案尚未定案；登入安全預設見計畫。
- 採用計畫的安全與一致性修正；會員保留原兌換業務規則，詳見行為附件 B7。

## 目前狀態

已有 Next.js 首頁、註冊／登入／登出、公開 profile、管理員使用者 CRUD、會員兌換，以及 FastAPI health/readiness、PostgreSQL 與 Alembic migrations。帳號入口為 `/account`，管理入口為 `/admin/users`；圖片與空間功能尚未實作，正式部署尚未設定。

首位管理員與會員碼使用本機 CLI，密碼與代碼以隱藏輸入提供，不使用固定密碼。於本機依序啟動 DB、migration 後執行：

```sh
APP_ENV=local DATABASE_URL=postgresql+psycopg://postgres@127.0.0.1:55479/yupicture uv --directory api run --frozen python -m app.cli bootstrap-admin admin-user
APP_ENV=local DATABASE_URL=postgresql+psycopg://postgres@127.0.0.1:55479/yupicture uv --directory api run --frozen python -m app.cli add-vip-code
```

本機 HTTP 使用 HttpOnly session cookie；非 local 使用 Secure，unsafe API 驗證 Origin 與 CSRF。正式環境另提供 `ALLOWED_ORIGINS`。會員沿用原期限與角色規則；詳見[使用者子計畫](docs/plans/2026-10-01-users.md)。

## 本機啟動

需要 Node.js 24+、pnpm 11.2.2、Python 3.13、uv 與 Docker。於 repo root 執行：

```sh
make install-frozen
make db-up
make migrate
make dev-api
```

另開一個 terminal，在 repo root 執行 `make dev-web`，開啟 http://127.0.0.1:3309 。API 文件在 http://127.0.0.1:8009/docs 。

初次使用 Playwright 請執行 `make browser-install`；會下載 Chromium，Linux 上也會安裝系統依賴。本機驗收入口為 `make check`，須先完成 frozen install 與 browser install。所有 Make targets 使用本專案的本機 DB，不讀 `.env`；正式環境可直接使用 app 並以環境提供 `DATABASE_URL`、`API_BASE_URL`。

本機 PostgreSQL 綁定 `127.0.0.1:55479`，使用獨立 volume 與無密碼 trust，僅適用本機開發。`make db-stop` 停止本專案 DB，不刪資料。瀏覽器測試會短暫停止／重啟此 DB；同一時間只跑一組 DB integration/E2E。

## 驗收入口

- `make lint-api test-api`：Python lint、API unit／真實 PostgreSQL 與 migration 基線測試。
- `make test-web typecheck build`：SSR client 錯誤／timeout 測試、TypeScript 與 production build。
- `make test-e2e`：真實瀏覽器驗證註冊／登入／會員兌換／登出、admin CRUD、DB 停止／恢復、API 無法連線與手機版；先執行 build。
- `make test-mutation`：確認固定成功 DB probe、繞過 admin gate、會員提前 commit 都會被 regression 擋住；測試失敗是刻意注入的結果，外層命令只有在成功擋住時回傳 0。
- `make check`：依序啟動 DB、migration、上述全部檢查；GitHub Actions 使用相同入口。

## 待執行路線

- [完整重做計畫與進度](docs/plans/2026-10-01-rebuild.md)：來源盤點 → walking skeleton → 使用者與登入 → 公共圖庫 → 私人空間 → 團隊協作 → 外部搜尋／AI → 收尾部署。

每階段需有可重跑的驗收；功能完成以盤點清單逐項對照為準。
