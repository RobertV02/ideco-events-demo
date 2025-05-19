# logs/scripts/normalizer.py

from typing import List, Dict
from django.conf import settings
from ..models import Event

def run(events: List[Dict]) -> int:
    """
    Сохраняет события в базу. 
    Для dst_ip ставим адрес UTM (из .env → settings.UTM_HOST).
    """
    count = 0
    for ev in events:
        Event.objects.create(
            src_ip=ev["src_ip"],
            dst_ip=getattr(settings, "UTM_HOST", "0.0.0.0"),
            protocol=ev.get("protocol", ""),
            action=ev.get("action", ""),
            raw_message=ev.get("raw_message", ""),
        )
        count += 1
    return count
