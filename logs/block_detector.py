# logs/block_detector.py
import re
from .tasks import block_ip

# Регулярка на «Invalid user … from <IP>»
SSH_INVALID_RE = re.compile(
    r"Invalid user \w+ from (?P<ip>\d+\.\d+\.\d+\.\d+)"
)

def detect_and_block(event):
    """
    Вызывается после сохранения Event. 
    Если raw_message соответствует нашему случаю — блокируем IP.
    """
    raw = event.raw_message
    m = SSH_INVALID_RE.search(raw)
    if m:
        ip = m.group("ip")
        block_ip.delay(ip)
