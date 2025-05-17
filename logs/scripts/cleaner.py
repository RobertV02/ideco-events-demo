from typing import List, Dict, Set, Tuple

def run(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Удаляет дубликаты (src_ip, dst_ip, protocol, action).
    """
    unique: Set[Tuple[str, str, str, str]] = set()
    cleaned: List[Dict[str, str]] = []

    for ev in events:
        key = (ev["src_ip"], ev["dst_ip"], ev["protocol"], ev["action"])
        if key in unique:
            continue
        unique.add(key)
        cleaned.append(ev)

    return cleaned
