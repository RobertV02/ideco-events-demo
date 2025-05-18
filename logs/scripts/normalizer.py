# logs/scripts/normalizer.py
from typing import List, Dict
from logs.models import Event

def run(events: List[Dict[str, str]]) -> int:
    """
    Сохраняет события в базу данных как объекты Event.
    """
    for ev in events:
        Event.objects.create(
            src_ip=ev['src_ip'],
            dst_ip=ev['dst_ip'],
            protocol=ev['protocol'],
            action=ev['action'],
            raw_message=ev['raw_message']
        )
    return len(events)
