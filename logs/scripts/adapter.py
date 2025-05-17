import os
from pathlib import Path
from typing import List, Dict

LOG_FILE = os.getenv("IDECO_LOG_PATH", str(Path.home() / "utm_sample.log"))

def parse_line(line: str) -> Dict[str, str]:
    """
    Простейший парсер: src_ip dst_ip protocol action ...
    При необходимости доработайте под реальный формат Ideco.
    """
    parts = line.strip().split()
    if len(parts) < 4:
        return {}
    return {
        "src_ip":     parts[0],
        "dst_ip":     parts[1],
        "protocol":   parts[2].lower(),
        "action":     parts[3].upper(),
        "raw_message": line.strip(),
    }

def run() -> List[Dict[str, str]]:
    """
    Читает LOG_FILE и возвращает список словарей-событий.
    """
    events: List[Dict[str, str]] = []
    if not os.path.exists(LOG_FILE):
        return events

    with open(LOG_FILE, "r") as fh:
        for line in fh:
            if not line.strip():
                continue
            ev = parse_line(line)
            if ev:
                events.append(ev)
    return events
