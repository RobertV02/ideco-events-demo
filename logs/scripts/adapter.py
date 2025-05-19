# logs/scripts/adapter.py
import re
from pathlib import Path
from typing import List, Dict

LOG_FILE = Path("/var/log/ideco/utm.log")

# Регулярка — ловим именно «Invalid user … from <IP>»
SSH_RE = re.compile(
    r"sshd.*Invalid user \w+ from (?P<ip>\d+\.\d+\.\d+\.\d+)"
)

def run() -> List[Dict]:
    """
    Возвращает список словарей только для тех строк лога,
    в которых найден sshd Invalid user <login> from <IP>.
    """
    if not LOG_FILE.exists():
        return []

    events: List[Dict] = []
    for line in LOG_FILE.read_text().splitlines():
        m = SSH_RE.search(line)
        if not m:
            continue
        ip = m.group("ip")
        events.append({
            "src_ip": ip,
            "dst_ip": "",           # при желании можно указать "ssh"
            "protocol": "ssh",
            "action": "Invalid SSH login",
            "raw_message": line,
        })
    return events
