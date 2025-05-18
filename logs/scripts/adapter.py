# logs/scripts/adapter.py
from pathlib import Path
from typing import List, Dict

# Путь к файлу журнала: data/utm.log в корне проекта
LOG_FILE = Path(__file__).resolve().parents[2] / "data" / "utm.log"

def parse_line(line: str) -> Dict[str, str]:
    """
    Простейший парсер: src_ip dst_ip protocol action ...
    При необходимости доработайте под реальный формат.
    """
    parts = line.strip().split()
    if len(parts) < 4:
        return {}
    return {
        "src_ip": parts[0],
        "dst_ip": parts[1],
        "protocol": parts[2].lower(),
        "action": parts[3].upper(),
        "raw_message": line.strip(),
    }

def run() -> List[Dict[str, str]]:
    """
    Читает LOG_FILE и возвращает список словарей-событий.
    """
    events: List[Dict[str, str]] = []
    if not LOG_FILE.exists():
        return events
    with open(LOG_FILE, "r") as fh:
        for line in fh:
            if not line.strip():
                continue
            ev = parse_line(line)
            if ev:
                events.append(ev)
    return events
