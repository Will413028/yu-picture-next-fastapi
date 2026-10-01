"""Extract only public code contracts; never inspect application configuration."""
import argparse
import re
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
args = parser.parse_args()
source = args.source.resolve()
revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
backend = source / "yu-picture-backend"
prefix = "src/main/java/com/yupi/yupicturebackend"
rows = []
for file in sorted((backend / prefix / "controller").glob("*.java")):
    content = file.read_text()
    base = re.search(r'@RequestMapping\("([^"]+)"\)', content).group(1)
    for match in re.finditer(r'^[ \t]*@(Get|Post|Put|Delete)Mapping\("([^"]+)"\)', content, re.M):
        line = content[:match.start()].count("\n") + 1
        module = file.stem
        path = base.rstrip("/") + match.group(2)
        phase = {"UserController": "2", "PictureController": "3", "SpaceController": "4", "SpaceAnalyzeController": "4", "SpaceUserController": "5", "MainController": "1", "FileController": "3"}[module]
        if "/out_painting/" in path or path == "/picture/search/picture":
            phase = "6"
        if path == "/picture/edit/batch" or path == "/picture/search/color":
            phase = "4"
        disposition = "改寫為 FastAPI，功能保留；新契約待 D2"
        if module == "FileController":
            disposition = "刪除公開測試端點，改為儲存 adapter integration test（D5 已決）"
        if path == "/picture/list/page/vo/cache":
            disposition = "合併至圖片列表，快取內部化（待 D2）"
        rows.append((match.group(1).upper(), path, phase, disposition, f"yu-picture-backend/{prefix}/controller/{file.name}:{line}"))
print("# 原專案介面盤點\n")
print(f"來源：https://github.com/liyupi/yu-picture\n\n快照：`{revision}`；盤點日期：2026-10-01。\n")
print("重跑：`python3 docs/plans/2026-10-01-rebuild/inventory.py <reference-checkout>`。輸出包含去向提案；以計畫決定表為準。\n")
print(f"## REST 端點（{len(rows)} 個，不含 servlet context path）\n")
print("| 方法 | 舊路徑 | 階段 | 去向 | 原始碼位置 |\n|---|---|---|---|---|")
for row in rows:
    print("| " + " | ".join(row) + " |")
router = source / "yu-picture-frontend/src/router/index.ts"
routes = re.findall(r"path:\s*'([^']+)'", router.read_text())
print(f"\n## 前端路由（{len(routes)} 個）\n")
print("來源：`yu-picture-frontend/src/router/index.ts`。\n")
print("| 路由 | 階段 | 去向 |\n|---|---|---|")
for route in routes:
    phase = "3"
    if route in ["/user/login", "/user/register", "/admin/userManage", "/user_exchange_vip"]:
        phase = "2"
    elif "spaceUserManage" in route:
        phase = "5"
    elif "space" in route.lower():
        phase = "4"
    elif route == "/search_picture":
        phase = "6"
    disposition = "改寫為 Next.js，功能保留；路徑待 D2"
    if route == "/about":
        disposition = "移除 Vue starter 展示頁（D5 已決）"
        phase = "7"
    print(f"| `{route}` | {phase} | {disposition} |")
sql = backend / "sql/create_table.sql"
tables = re.findall(r"create table if not exists (\w+)", sql.read_text(), re.I)
print(f"\n## 資料表（{len(tables)} 個）\n")
print("來源：`yu-picture-backend/sql/create_table.sql`；欄位與索引需在階段 1/2 的 schema 契約逐項映射，不把此表視為完整欄位盤點。\n")
print("| 表 | 階段 | 去向 |\n|---|---|---|")
for table in tables:
    phase = {"user": "2", "picture": "3", "space": "4", "space_user": "5"}[table]
    print(f"| `{table}` | {phase} | 改寫為 SQLAlchemy model 與 Alembic migration，DB 選型待 D1 |")
print("\n## WebSocket 事件\n")
print("來源：`yu-picture-backend/src/main/java/com/yupi/yupicturebackend/manager/websocket/model/PictureEditMessageTypeEnum.java`。\n")
print("| 事件 | 階段 | 去向 |\n|---|---|---|")
enum = backend / prefix / "manager/websocket/model/PictureEditMessageTypeEnum.java"
for event in re.findall(r'^\s*(\w+)\("', enum.read_text(), re.M):
    print(f"| `{event}` | 5 | 保留通知、錯誤、進入／退出與操作語意，協定重設待 D2 |")
print("\n## 元件功能補充\n")
print("| 元件來源（yu-picture-frontend/src/components/） | 階段 | 去向 |\n|---|---|---|")
for name, phase in [("ImageCropper.vue", "4"), ("BatchEditPictureModal.vue", "4"), ("ShareModal.vue", "4"), ("ImageOutPainting.vue", "6")]:
    if not (source / "yu-picture-frontend/src/components" / name).is_file():
        raise SystemExit(f"Expected component missing: {name}")
    print(f"| `{name}` | {phase} | 改寫為 React，保留使用者操作 |")
print("\n外部整合：COS 圖片處理、批次圖片抓取、以圖搜圖與 AI 擴圖需各自記錄 request/response fixture、失敗模式與供應商設定；階段 0 尚未完成這些 payload 契約，階段 3/6 開工前必須完成。不得讀取或複製原 repo 的憑證設定。")
print("\n## 直接消費圖片 URL 的行為\n")
print("| 行為與來源 | 階段 | 去向 |\n|---|---|---|")
print("| 下載：PictureDetailPage.vue:99,170；utils/index.ts:19–23 | 3/4/5 | 保留下載，公共／私人／團隊分別驗收；API 授權後串流或短效 URL，方案待 D4 子設計 |")
print("| 分享：PictureList.vue:131；PictureDetailPage.vue:179；ShareModal.vue | 4/5 | 保留詳情 URL 複製與 QR，仍依圖片權限；不建立匿名分享 grant |")
