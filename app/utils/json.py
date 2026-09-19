import json
from typing import Any


def parse_json(text: str) -> Any:
    return json.loads(text)


def to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
