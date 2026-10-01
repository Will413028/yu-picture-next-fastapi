# 缺陷與沿用盤點

來源快照與命令見 inventory.md；下列為靜態觀察，尚未跑舊系統 regression。來源路徑皆相對 reference checkout，行號以該快照為準。Will 2026-10-01 已核准 B1–B6 與 B7 的一致性修正；B7 會員業務保留原規則，不採用角色分離與延長既有期限提案。

| ID | 證據 | 建議處置 | 驗收／mutation |
|---|---|---|---|
| B1 | PictureServiceImpl.uploadPicture 在 saveOrUpdate 後 totalCount+=1、totalSize+=picSize | 修正 replacement 為大小差額、count 不變（階段 4） | 先新增再替換，count=1、size=新大小；改回舊寫法必失敗 |
| B2 | 同函式先執行物件上傳，再執行 DB transaction | 修正 DB 失敗的 orphan 清理與 retry 去重（階段 3） | 注入 DB failure，最終沒有 orphan 且 retry 只存一筆；移除補償則失敗 |
| B3 | manager/auth/StpInterfaceImpl 空 context 回 ADMIN_PERMISSIONS，context 從 HTTP 解析 | 改成明確 principal/resource/action policy，不能從缺失 context 推導授權（階段 2/4/5） | 缺資源／錯資源／其他空間皆不能得到寫權限；改成預設放行則失敗 |
| B4 | manager/upload/UrlPictureUpload.validPicture 僅檢查 HTTP scheme 與 HEAD headers；processFile 另下載 | 改成限制 resolved IP、redirect 每跳檢查、GET 串流大小與影像解碼限制（階段 3） | 私網、redirect 私網、偽造 length、過大解碼 fixture 拒絕；回舊校驗時失敗 |
| B5 | UserServiceImpl.getEncryptPassword 使用 md5DigestAsHex | 新建帳號使用 Argon2id，不移植舊雜湊（階段 2） | 密碼可驗證、隨機 salt、資料庫無明文；換回 MD5 時規格測試失敗 |
| B6 | PictureEditHandler 使用 JVM maps、containsKey+put、disconnect 按 userId 退出 | 重新設計原子取得編輯權與 session/lease 身分，保留單編輯者語意（階段 5） | 兩 client 搶鎖與同帳號多 tab 斷線不錯放鎖；多實例需求待決，不直接宣稱來源鎖一定競態 |
| B7 | UserServiceImpl.java:275–277 先消耗 code 檔，再更新 user；285–305 的 file lock 不涵蓋 DB；340–352 從現在起算一年並改 userRole=VIP | 修正：兌換碼消耗與 user 更新放 PostgreSQL 同一 transaction，失敗不消耗、同碼只兌一次。接受原業務：每次兌換期限設為兌換當下加 12 個月，記錄使用代碼，userRole 設為 VIP（含原管理員）；不改成角色分離或累加剩餘期限。Will 2026-10-01 已決；階段 2 | DB failure 後 code 可再次兌換；两人同碼只一人成功；同碼重複兌換拒絕；固定時計驗證期限始終 now+12 months 與 role=VIP。改回分開寫入時 regression 失敗；改為累加期限或保留舊角色時相容性測試失敗 |

會員來源的「JSON 兌換碼存放」只讀公開方法，不開啟實際 code 檔；新系統兌換碼管理方式在階段 2 schema 子計畫核定，不自行增加付款或訂閱功能。

## 分享與下載的已確認來源行為

- PictureList.vue:131、PictureDetailPage.vue:179 組合 `/picture/{id}` 詳情 URL；ShareModal.vue 複製連結與產生 QR。分享不建立匿名 grant，仍遵循圖片本身權限。重做保留此語意；匿名分享 token 不在目前範圍。
- PictureDetailPage.vue:99、170 與 utils/index.ts:19–23 使用 saveAs(url, fileName) 下載圖片；新系統必須提供同等下載功能，私人／團隊存取採 API 授權後串流或短效 URL（D4 的子設計），不能因更換儲存方式而漏掉。

## 沿用機制重新評估

| 機制 | 來源 | 今日從零設計 | 決定與重評條件 |
|---|---|---|---|
| 圖片上傳共用流程 | PictureUploadTemplate | typed source + storage/processing adapter，清楚的失敗補償 | 保留流程意圖，Python 不移植 Object 與繼承階層；階段 3 設計審查 |
| 空間角色 | SpaceRoleEnum / SpaceUserAuthManager | resource-scoped policy | 保留角色業務，實作另定；缺矩陣不開工 |
| 單編輯者 | PictureEditHandler | 原子 editor lease + event protocol | 保留單編輯者功能；若改多人同編，需使用者另決 |
| Java long ID | SQL schema / frontend typings | API string ID，DB ID 方案在 schema 子計畫定 | 不複製 Snowflake generator；有搬資料需求才重評 |
| DDD 資料夾 | backend-ddd | 模組化單體，不先增加空 abstraction | 不照搬 DDD 路徑；業務需要 aggregate boundary 才引入 |
| Disruptor / Redis+Caffeine / sharding | 原專案 managers/config | 普通 worker、正確 SQL/索引先行，量測再加機制 | 延後優化；性能瓶頸與目標數值出現才評估 |

## 安全預設來源

- 密碼：https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html（Argon2id 最低設定依實作時官方版本核對）。
- Session：https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html（opaque session，HttpOnly/Secure cookie，失效與輪替）。
- CSRF：https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html。
- URL 匯入：https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html。

session TTL 預設 idle 30 分鐘、absolute 24 小時（可推翻）；以伺服器時計與測試驗證，不依賴 client。所有安全預設仍需階段 2/3 子計畫具體化。
