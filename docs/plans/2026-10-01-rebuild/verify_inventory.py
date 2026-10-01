"""Verify reproducibility and that adding an endpoint changes the inventory."""
import contextlib
import io
import re
import runpy
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

here = Path(__file__).resolve().parent
source = Path(sys.argv[1]).resolve()
script = here / "inventory.py"


def render(root):
    output = io.StringIO()
    with patch.object(sys, "argv", [str(script), str(root)]), contextlib.redirect_stdout(output):
        runpy.run_path(str(script), run_name="__main__")
    return output.getvalue()


actual = render(source)
expected = (here / "inventory.md").read_text()
assert actual == expected, "Inventory differs; regenerate and review"
assert "REST 端點（53 個" in actual
assert "前端路由（17 個" in actual
assert "資料表（4 個" in actual
assert len(re.findall(r"^\| `(INFO|ERROR|ENTER_EDIT|EXIT_EDIT|EDIT_ACTION)`", actual, re.M)) == 5

# Copy only the public contract files the extractor consumes. Never copy configs.
with tempfile.TemporaryDirectory(prefix="inventory-mutation-", dir=here) as temp:
    fixture = Path(temp)
    paths = list(source.glob("yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/*.java"))
    paths += [source / "yu-picture-backend/sql/create_table.sql", source / "yu-picture-frontend/src/router/index.ts"]
    paths += [source / "yu-picture-backend/src/main/java/com/yupi/yupicturebackend/manager/websocket/model/PictureEditMessageTypeEnum.java"]
    paths += [source / "yu-picture-frontend/src/components" / name for name in ["ImageCropper.vue", "BatchEditPictureModal.vue", "ShareModal.vue", "ImageOutPainting.vue"]]
    for path in paths:
        target = fixture / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    controller = fixture / "yu-picture-backend/src/main/java/com/yupi/yupicturebackend/controller/MainController.java"
    controller.write_text(controller.read_text() + '\n    @GetMapping("/mutation-probe")\n')
    # Preserve the snapshot label while mutating public source in an isolated fixture.
    with patch("subprocess.check_output", return_value="a053632c41340152bf75b66b3c543d129123d8ec\n"):
        mutated = render(fixture)
    assert mutated != expected
    assert "REST 端點（54 個" in mutated
    assert "GET | /mutation-probe" in mutated

print("PASS: inventory reproducible; 53 endpoints / 17 routes / 4 tables / 5 message types")
print("PASS: added endpoint detected in isolated mutation fixture; source untouched")
