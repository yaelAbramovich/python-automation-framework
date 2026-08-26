import json
from pathlib import Path
from typing import Any

_STRINGS_FILE_PATH = Path(__file__).parent / "strings.json"

with _STRINGS_FILE_PATH.open(encoding="utf-8") as _strings_file:
    strings: dict[str, Any] = json.load(_strings_file)
