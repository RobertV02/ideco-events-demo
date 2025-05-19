# logs/scripts/normalizer.py

from typing import List, Dict
from ..models import Event

def run(events: List[Dict]) -> int:
    """
    Сохраняет новые события в базу данных.
    Ожидается, что каждый ev – словарь с ключами:
      src_ip, dst_ip, protocol, action, raw_message
    Возвращает количество сохранённых записей.
    """
    count = 0
    for ev in events:
        Event.objects.create(
            src_ip=ev.get("src_ip", ""),
            dst_ip=ev.get("dst_ip", ""),
            protocol=ev.get("protocol", ""),
            action=ev.get("action", ""),
            raw_message=ev.get("raw_message", ""),
        )
        count += 1
    return count
