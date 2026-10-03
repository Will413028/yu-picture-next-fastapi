---
title: 從零重做圖庫，採獨立 FastAPI 業務邊界與 S3 影像管線
date: 2026-10-01
status: active
tags: [personal, decision, nextjs, fastapi, postgresql]
---

# 從零重做圖庫，採獨立 FastAPI 業務邊界與 S3 影像管線

## Context

Will 要完整重做原圖庫功能，指定 Next.js＋FastAPI，並選 PostgreSQL、重新設計 REST 與 S3-compatible 自行處理圖片。本 ADR 回溯已決取捨，不從已實作 code 倒推選型動機。

- `external`：Will 2026-10-01 確認沒有既有部署、client或資料；不需要相容窗口或搬移。
- `inherited`：來源功能、角色、錯誤情境與單編輯者語意仍作規格；因目標是功能對照重做，仍成立。
- 原 MySQL、COS、Java效能機制不是保留約束；沒有既有部署迫使新系統沿用。

## Options Considered

### 應用架構

- **基準：單一應用、依責任分模組**。部署與交易最簡單；需維持內部邊界。來源：[Microsoft application architectures](https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures)；支持單體起步，沒有指定本專案語言。
- **A：Spring Boot／Vue重建**。行為與技術對照較直接；不達成本次指定的Next.js／FastAPI實作。
- **B：Next.js全端單體**。少一套runtime與跨服務契約；業務集中TypeScript，不取得獨立Python API邊界。
- **C：Next.js＋FastAPI模組化單體（選用）**。UI／SSR與統一業務API分工；代價是雙runtime、HTTP transport與cookie傳遞。
- **D：按領域拆微服務**。可獨立擴展；目前未有負載或組織證據值得支付跨服務一致性成本。

### 資料與契約

- **A：MySQL＋原API**。來源比對容易；延續來源collation與action routes。
- **B：PostgreSQL＋REST重設（選用）**。新client與schema可一起設計；必須逐項映射payload、角色、錯誤情境與查詢差異。DB與API亦可分別替換，不是技術上必須綁定。

### 儲存與影像

- **A：COS＋供應商影像處理**。較少自行維護解碼、縮圖與metadata；依賴供應商處理契約。
- **B：S3-compatible＋自行處理（選用）**。儲存與處理可各自驗證；自行承擔資源限制、品質、清理與retry。S3物件API能力來源：[Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)，不代表所有compatible provider無差異。
- **C：本機filesystem**。薄路徑最簡單；正式部署、多實例與搬移另需設計，不能視為完成S3整合。

## Decision

- **D1**：Next.js承接UI／SSR；FastAPI統一業務與授權，後端模組化單體。
- **D2**：PostgreSQL；保留功能但重新設計REST，不承諾原route相容。
- **D3**：S3-compatible adapter＋自行處理圖片；尚未選provider、local runtime或影像套件。
- **D4**：不先搬分庫分表、二級快取與專用高效佇列；功能保留，機制依量測選型。

## Rationale

- **D1**：滿足Will指定的重做方向，以獨立API邊界承接所有授權；相較全端單體，接受雙工具鏈與transport成本。無需求證據支持先拆微服務。
- **D2**：無舊client／資料，重設契約的代價是盤點與驗收，而非服務中斷。PostgreSQL是本次已選技術，來源沒有性能比較；不宣稱優於MySQL，接受帳號比對、索引與查詢重新驗證成本。
- **D3**：降低對COS影像功能的牽制，代價是自行負責完整影像管線；compatible只代表接口方向，仍需逐provider驗證。
- **D4**：先建立薄路徑與功能證據；不選原效能機制不是刪除原使用者功能。

## Expected Outcome

能逐項對照來源功能，所有業務授權由FastAPI執行；換契約與儲存不造成漏功能。骨架與帳號已驗收，圖片／空間／外部服務仍待各階段完成。

## Followup

- 步驟3核定provider、影像處理、metadata、授權下載、補償／retry與真實整合。
- 步驟5核定單／多實例協作；步驟6選搜尋／AI provider與成本。
- 建立remote後驗證CI／Node24；步驟7核定部署環境與正式驗收。

## Revocation Triggers

- 新增既有部署、資料或client → 重評相容／搬移策略。
- 實測單DB或worker無法達標 → 重評對應機制，不預設全面改微服務。
- Provider授權或影像能力不符需求，或DB重驗成本失衡 → 重評選型。

## Review Notes

初稿兩份獨立唯讀草稿已對照；補入技術動機不可杜撰、會員／DB/API可獨立決策、provider差異與尚未驗證的邊界。

## Related

- [會員行為與原子兌換](2026-10-01-membership-behavior-and-atomic-redemption.md)。
- 2026-10-01與Will討論；本ADR是決策紀錄。來源可取回：於repo執行 `git show 24c0f3569b7259a5ea6eeef08f3d7d5418f53639:docs/plans/2026-10-01-rebuild.md`；D1／D2／D4／D5是來源決定編號，本文D1–D4是歸納編號。
- 未刪除來源計畫；未新增Lessons Rule，無tech抽取。
