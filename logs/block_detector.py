import re, logging
from .tasks import block_ip

log = logging.getLogger(__name__)

SSH_INVALID_RE = re.compile(r"Invalid user \w+ from (?P<ip>\d+\.\d+\.\d+\.\d+)")

def detect_and_block(event):
    raw = event.raw_message
    log.info(f"[DETector] Проверяем событие: {raw!r}")
    m = SSH_INVALID_RE.search(raw)
    if m:
        ip = m.group("ip")
        log.info(f"[DETector] Найден SSH brute по IP {ip}, ставим block_ip")
        block_ip.delay(ip)
    else:
        log.info("[DETector] Это не SSH brute")
