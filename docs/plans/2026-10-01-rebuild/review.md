# 計畫審查與驗收

2026-10-01：獨立唯讀 plan_review agent 對計畫、附件與原程式碼核對 8 項。發現 5 項，全部修正；沒有駁回。不是程式實作的 design review，該審查仍在各階段收尾執行。

| Finding | 處置 | 證據 |
|---|---|---|
| R1 盤點行號與結尾不一致 | 已修 | extractor 的 annotation regex 改成水平空白；verify_inventory.py 精確比較全部輸出，已通過 |
| R2 會員 D5 blocker 沒有 B 項 | 已修 | behavior.md B7 與步驟 2 blocker 直接對應；原兌換/DB 邊界、期限與角色處置明確，等待 D5 決定 |
| R3 README 的 DB/skeleton 與計畫相矛盾 | 已修 | README/AGENTS 與已決 PostgreSQL/REST 一致，skeleton 與登入分開；詳細進度只有計畫一處 |
| R4 漏掉下載消費端 | 已修 | inventory.py/md 直接 URL 消費清單；步驟 3 公共下載、4 私人下載、5 團隊 action 矩陣 |
| R5 分享已有來源事實卻仍擋住 | 已修 | behavior.md 記錄 source 詳情 URL/QR；步驟 4 移除匿名 grant blocker，不新增分享權益 |

已跑：verify_inventory.py 精確輸出比較與新增源 endpoint 的隔離 mutation fixture、本機 Markdown 文件連結檢查、second-brain lint-rules.py/check-links.py。原始碼 reference status 乾淨、HEAD 為盤點快照。

步驟0時未跑：舊應用 build/run、新應用 tests/build/E2E/migration/provider smoke，當時沒有原環境且新應用尚未實作。後續已跑驗收以主計畫進度表與各子計畫為準；圖片／provider整合仍未開始。

## 接手入口

- 下一步：展開步驟 3 公共圖庫與 S3／影像處理子計畫；步驟 2 功能、plan/code/design 審查及最後版本完整 make check 已完成，證據見主計畫與 users 子計畫。
- 前提：Will 2026-10-01 已決 Next.js UI/SSR + FastAPI API 模組化單體、PostgreSQL、REST 重設、從零建立無搬移，均仍成立。
- Git main 已初始化，無 commit／remote；依賴與 Chromium 已安裝。外部新下載與任何 credential 動作按工作區授權規則另行確認。
- D4 已選 S3-compatible＋自行處理圖片，實際 provider 尚未選；D5 已採 B1–B6/B7 原子性修正與移除測試端點／About，會員業務保留原規則。不得默默改成會員角色分離／累加期限或選定正式儲存 provider。
- 這是學習重做，尚未建立 second-brain 專案 wiki；決定目前存在本計畫，獨立 ADR 與 second-brain recording 尚未建立，不宣稱已完成這些流程。

## 步驟 1 驗收摘要

- frozen install 與完整 make check 成功；5 API/migration + 3 client unit + 3 Playwright tests。
- 故意注入 fixed-success DB probe 被既有負向測試擋住，mutation 外層 exit 0；不修改共享 source。
- 桌機與390px手機 screenshot 已檢視，無截斷／橫向溢出；截圖在 ignored web/test-results/。
- DB 已恢復健康並保留開發 volume；測試 API/Web servers 已由 Playwright 關閉。
- 設計審查0項；code review1項（health未碰DB的assert）已修；計畫審查2項已修，未駁回。
- GitHub Actions 遠端未執行，dev-web 熱更新未驗證；指令與設定存在不代表執行過。
