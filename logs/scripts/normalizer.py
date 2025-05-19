# logs/scripts/normalizer.py
from typing import List, Dict
from ..models import Event

def run(events: List[Dict]) -> int:
    """
    Создаёт Event для каждого new_event.
    """
    count = 0
    for ev in events:
        Event.objects.create(
            src_ip="",          # будем парсить в детекторе
            dst_ip="",
            protocol="",
            action="",
            description="",
            raw_message=ev["raw_message"]
        )
        count += 1
    return count
