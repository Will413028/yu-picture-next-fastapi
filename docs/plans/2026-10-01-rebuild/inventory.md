# 原專案介面盤點

來源：https://github.com/liyupi/yu-picture

快照：`a053632c41340152bf75b66b3c543d129123d8ec`；盤點日期：2026-10-01。

重跑：`python3 docs/plans/2026-10-01-rebuild/inventory.py <reference-checkout>`。輸出包含去向提案；以計畫決定表為準。

## REST 端點（53 個，不含 servlet context path）

| 方法 | 舊路徑 | 階段 | 去向 | 原始碼位置 |
|---|---|---|---|---|
| POST | /file/test/upload | 3 | 刪除公開測試端點，改為儲存 adapter integration test（D5 已決） | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/FileController.java:38 |
| GET | /file/test/download/ | 3 | 刪除公開測試端點，改為儲存 adapter integration test（D5 已決） | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/FileController.java:72 |
| GET | /health | 1 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/MainController.java:16 |
| POST | /picture/upload | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:92 |
| POST | /picture/upload/url | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:107 |
| POST | /picture/delete | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:118 |
| POST | /picture/update | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:137 |
| GET | /picture/get | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:167 |
| GET | /picture/get/vo | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:181 |
| POST | /picture/list/page | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:211 |
| POST | /picture/list/page/vo | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:225 |
| POST | /picture/list/page/vo/cache | 3 | 合併至圖片列表，快取內部化（待 D2） | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:262 |
| POST | /picture/edit | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:311 |
| GET | /picture/tag_category | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:322 |
| POST | /picture/review | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:335 |
| POST | /picture/upload/batch | 3 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:348 |
| POST | /picture/search/picture | 6 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:361 |
| POST | /picture/search/color | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:375 |
| POST | /picture/edit/batch | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:389 |
| POST | /picture/out_painting/create_task | 6 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:401 |
| GET | /picture/out_painting/get_task | 6 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/PictureController.java:416 |
| POST | /space/analyze/usage | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceAnalyzeController.java:41 |
| POST | /space/analyze/category | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceAnalyzeController.java:58 |
| POST | /space/analyze/tag | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceAnalyzeController.java:75 |
| POST | /space/analyze/size | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceAnalyzeController.java:92 |
| POST | /space/analyze/user | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceAnalyzeController.java:108 |
| POST | /space/analyze/rank | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceAnalyzeController.java:124 |
| POST | /space/add | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:59 |
| POST | /space/delete | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:67 |
| POST | /space/update | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:93 |
| GET | /space/get | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:120 |
| GET | /space/get/vo | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:134 |
| POST | /space/list/page | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:151 |
| POST | /space/list/page/vo | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:165 |
| POST | /space/edit | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:182 |
| GET | /space/list/level | 4 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceController.java:214 |
| POST | /spaceUser/add | 5 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceUserController.java:48 |
| POST | /spaceUser/delete | 5 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceUserController.java:59 |
| POST | /spaceUser/get | 5 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceUserController.java:79 |
| POST | /spaceUser/list | 5 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceUserController.java:96 |
| POST | /spaceUser/edit | 5 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceUserController.java:110 |
| POST | /spaceUser/list/my | 5 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/SpaceUserController.java:135 |
| POST | /user/register | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:38 |
| POST | /user/login | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:51 |
| GET | /user/get/login | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:63 |
| POST | /user/logout | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:72 |
| POST | /user/add | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:82 |
| GET | /user/get | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:101 |
| GET | /user/get/vo | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:113 |
| POST | /user/delete | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:123 |
| POST | /user/update | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:136 |
| POST | /user/list/page/vo | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:154 |
| POST | /user/exchange/vip | 2 | 改寫為 FastAPI，功能保留；新契約待 D2 | yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/UserController.java:171 |

## 前端路由（17 個）

來源：`yu-picture-frontend/src/router/index.ts`。

| 路由 | 階段 | 去向 |
|---|---|---|
| `/` | 3 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/user/login` | 2 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/user/register` | 2 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/admin/userManage` | 2 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/admin/pictureManage` | 3 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/admin/spaceManage` | 4 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/spaceUserManage/:id` | 5 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/add_picture` | 3 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/add_picture/batch` | 3 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/picture/:id` | 3 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/add_space` | 4 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/my_space` | 4 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/space/:id` | 4 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/space_analyze` | 4 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/search_picture` | 6 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/user_exchange_vip` | 2 | 改寫為 Next.js，功能保留；路徑待 D2 |
| `/about` | 7 | 移除 Vue starter 展示頁（D5 已決） |

## 資料表（4 個）

來源：`yu-picture-backend/sql/create_table.sql`；欄位與索引需在階段 1/2 的 schema 契約逐項映射，不把此表視為完整欄位盤點。

| 表 | 階段 | 去向 |
|---|---|---|
| `user` | 2 | 改寫為 SQLAlchemy model 與 Alembic migration，DB 選型待 D1 |
| `picture` | 3 | 改寫為 SQLAlchemy model 與 Alembic migration，DB 選型待 D1 |
| `space` | 4 | 改寫為 SQLAlchemy model 與 Alembic migration，DB 選型待 D1 |
| `space_user` | 5 | 改寫為 SQLAlchemy model 與 Alembic migration，DB 選型待 D1 |

## WebSocket 事件

來源：`yu-picture-backend/src/main/java/com/yupi/yupicturebackend/manager/websocket/model/PictureEditMessageTypeEnum.java`。

| 事件 | 階段 | 去向 |
|---|---|---|
| `INFO` | 5 | 保留通知、錯誤、進入／退出與操作語意，協定重設待 D2 |
| `ERROR` | 5 | 保留通知、錯誤、進入／退出與操作語意，協定重設待 D2 |
| `ENTER_EDIT` | 5 | 保留通知、錯誤、進入／退出與操作語意，協定重設待 D2 |
| `EXIT_EDIT` | 5 | 保留通知、錯誤、進入／退出與操作語意，協定重設待 D2 |
| `EDIT_ACTION` | 5 | 保留通知、錯誤、進入／退出與操作語意，協定重設待 D2 |

## 元件功能補充

| 元件來源（yu-picture-frontend/src/components/） | 階段 | 去向 |
|---|---|---|
| `ImageCropper.vue` | 4 | 改寫為 React，保留使用者操作 |
| `BatchEditPictureModal.vue` | 4 | 改寫為 React，保留使用者操作 |
| `ShareModal.vue` | 4 | 改寫為 React，保留使用者操作 |
| `ImageOutPainting.vue` | 6 | 改寫為 React，保留使用者操作 |

外部整合：COS 圖片處理、批次圖片抓取、以圖搜圖與 AI 擴圖需各自記錄 request/response fixture、失敗模式與供應商設定；階段 0 尚未完成這些 payload 契約，階段 3/6 開工前必須完成。不得讀取或複製原 repo 的憑證設定。

## 直接消費圖片 URL 的行為

| 行為與來源 | 階段 | 去向 |
|---|---|---|
| 下載：PictureDetailPage.vue:99,170；utils/index.ts:19–23 | 3/4/5 | 保留下載，公共／私人／團隊分別驗收；API 授權後串流或短效 URL，方案待 D4 子設計 |
| 分享：PictureList.vue:131；PictureDetailPage.vue:179；ShareModal.vue | 4/5 | 保留詳情 URL 複製與 QR，仍依圖片權限；不建立匿名分享 grant |
