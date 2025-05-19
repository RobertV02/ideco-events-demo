# logs/scripts/cleaner.py
from typing import List, Dict

def run(events: List[Dict]) -> List[Dict]:
    """
    Фильтрует дубликаты raw_message.
    """
    seen = set()
    unique = []
    for ev in events:
        rm = ev["raw_message"]
        if rm not in seen:
            seen.add(rm)
            unique.append(ev)
    return unique
