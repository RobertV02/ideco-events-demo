# logs/scripts/adapter.py
from pathlib import Path
from typing import List, Dict

LOG_FILE = Path("/var/log/ideco/utm.log")

def run() -> List[Dict]:
    """
    Возвращает список всех новых строк лога в виде словарей:
    {'raw_message': <строка>}
    """
    if not LOG_FILE.exists():
        return []

    with LOG_FILE.open("r") as f:
        lines = [l.rstrip() for l in f.readlines()]

    return [{"raw_message": l} for l in lines if l.strip()]
