# logs/scripts/cleaner.py
from typing import List, Dict
from logs.models import Event

def run(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Убирает события, которые уже есть в базе данных (модель Event).
    """
    filtered: List[Dict[str, str]] = []
    for ev in events:
        exists = Event.objects.filter(
            src_ip=ev['src_ip'],
            dst_ip=ev['dst_ip'],
            protocol=ev['protocol'],
            action=ev['action'],
            raw_message=ev['raw_message']
        ).exists()
        if not exists:
            filtered.append(ev)
    return filtered
