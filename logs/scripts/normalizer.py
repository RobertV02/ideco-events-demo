# logs/scripts/normalizer.py
from typing import List, Dict
from ..models import Event

def run(events: List[Dict]) -> int:
    """
    Сохраняет только те события, в которых есть src_ip.
    """
    count = 0
    for ev in events:
        # src_ip гарантированно непустой, т.к. фильтруем в адаптере
        Event.objects.create(
            src_ip=ev["src_ip"],
            dst_ip=ev.get("dst_ip", ""),
            protocol=ev.get("protocol", ""),
            action=ev.get("action", ""),
            raw_message=ev.get("raw_message", ""),
        )
        count += 1
    return count
