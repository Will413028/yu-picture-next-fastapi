# Project instructions

- 本專案以 Next.js + TypeScript 與 FastAPI 重做 yu-picture。
- Next.js 負責 UI 與 SSR；FastAPI 統一承接業務 API，後端採模組化單體。
- 使用 PostgreSQL，從零建立，不涉及既有部署或資料搬移；保留原功能並重新設計 REST API。
- [README.md](README.md) 記錄目前狀態、啟動與驗收入口；已有使用者、登入、管理與會員功能，圖片功能依重做計畫執行。
- [重做計畫](docs/plans/2026-10-01-rebuild.md) 是詳細進度與驗收來源；每階段開工前需展開可執行子計畫，確認未決事項。
- 在實作前盤點原專案行為與缺陷，區分需要保留的功能與需要修正的行為；勿僅根據原 README 推定完整規格。
- 技術元件依功能需求與量測選擇，不要求逐一移植 Java 技術棧。
- 原專案來源：https://github.com/liyupi/yu-picture

## 開發與驗收

- 在 repo root 執行 `make db-up migrate`、`make dev-api`；另一 terminal 執行 `make dev-web`。使用 Python 3.13、Node.js 24+、pnpm 11.2.2、Docker。
- `make check` 是 CI 等價入口；先完成 `make install-frozen` 與 `make browser-install`。各 target 的實際命令見 [Makefile](Makefile)。遠端 CI 是否已跑另見計畫驗收紀錄。
- Make targets 明確固定本機 DB，不使用 shell 中其他 `DATABASE_URL`。瀏覽器測試會停止本專案 DB，DB integration/E2E 必須串行執行。
- health 不碰 DB；readiness 必須真正查 DB，不能以固定成功取代。首頁使用 server-only client、no-store 與有界 timeout。
- PostgreSQL compose 只供本機開發；不可把 trust 配置用於正式部署。停止服務不刪 volume。
