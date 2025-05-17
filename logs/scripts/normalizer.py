from typing import List, Dict
from django.db import transaction
from logs.models import Event

def run(events: List[Dict[str, str]]) -> int:
    """
    Сохраняет события в БД, возвращает количество созданных записей.
    """
    created = 0
    with transaction.atomic():
        for ev in events:
            Event.objects.create(
                src_ip      = ev["src_ip"],
                dst_ip      = ev["dst_ip"],
                protocol    = ev["protocol"],
                action      = ev["action"],
                raw_message = ev["raw_message"],
            )
            created += 1
    return created
