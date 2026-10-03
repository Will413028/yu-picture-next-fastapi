---
title: 保留會員兌換業務規則，以單資料庫交易修正一致性
date: 2026-10-01
status: active
tags: [personal, decision, postgresql]
---

# 保留會員兌換業務規則，以單資料庫交易修正一致性

## Context

原來源將code消耗與會員DB更新分開，可能失敗消耗碼或併發重複。Will核准修原子性，並明確要求先保留原會員業務；不是因live相容性被迫保留。

- `external`：2026-10-01 Will要求「先保留原會員業務規則，其餘修正採用」。
- `external`：無既有部署／資料，不涉及code檔與會員搬移。
- `inherited`：來源的期限與角色效果仍成立，因這次重做以功能對照為範圍；JSON存碼與file lock不構成約束。

## Options Considered

- **基準：相關更新在同一relational DB transaction一起commit／rollback**。來源：[PostgreSQL Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)。此基準說明一致性，不定義會員產品模型。
- **A：保留期限／角色，code與user同DB transaction（選用）**。成功結果維持來源；修正失敗與併發一致性，不另設會員資格模型。
- **B：角色與entitlement分離，從max(now, expiry)延長**。可保留管理角色與剩餘期限；代價是改變原產品結果，超出本次已決範圍。角色分離與期限累加可分別選，不必綁成一組。
- **C：保留跨儲存code管理，加reservation／補償**。可接獨立code系統；代價是恢復與reconciliation，目前無外部code系統迫使採用。

## Decision

- **D1（來源D5）**：每次兌換now＋12個日曆月、role=vip；不延長既有expiry、不保留原admin角色、不新增自動到期降級。
- **D2（來源B7）**：code消耗、user更新、session撤銷／輪替同一transaction；同碼只能成功一次，任一步失敗不消耗碼。
- 原碼只在輸入流程使用，DB存digest，response不帶原code／hash；安全修正不改D1。

## Rationale

- **D1**：保留Will核准的功能對照，而非套一般訂閱模型；期限與角色的成功效果是已接受取捨，不是遺漏修正。未有新產品要求，不選B。
- **D2**：相較跨檔案補償，單DB能直接回滾且不用新增協調服務。代價是code狀態與會員更新共同依賴DB；目前沒有獨立code服務的需求。

## Expected Outcome

同碼併發只有一人成功；失敗後碼可再次使用。固定時鐘測試守住已核准期限與角色，包括已有較晚expiry、既有admin與2/29邊界；一致性修正不帶入新會員模型。

## Followup

- 正式部署前驗證登入／兌換rate limit、session清理及HTTPS／Secure cookie。
- 真實admin與code初始化留在人員授權操作；目前只有合成測試資料。

## Revocation Triggers

- 要求保留剩餘期限、會員不影響管理角色、付費訂閱或自動到期 → 另決會員模型與遷移。
- Code消耗移到外部系統，不能同DB transaction → 重評reservation／補償。

## Review Notes

兩份獨立草稿均要求將業務效果與原子性分開記錄，並指出角色／期限可獨立修訂，已納入。

## Related

- [Greenfield 技術棧與儲存](2026-10-01-greenfield-stack-and-storage.md)。
- 來源：2026-10-01與Will討論；原始決定可於repo執行 `git show 24c0f3569b7259a5ea6eeef08f3d7d5418f53639:docs/plans/2026-10-01-rebuild/behavior.md`，驗收取 `git show 24c0f3569b7259a5ea6eeef08f3d7d5418f53639:docs/plans/2026-10-01-users.md`。
- 已跑17項API及3種mutation；會員rollback先flush flag再注入失敗，提前commit mutation會在used_by斷言失敗。
- 未刪來源；無Lessons Rule，業務取捨屬本repo，不抽成跨專案規則。
