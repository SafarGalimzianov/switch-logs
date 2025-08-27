# logs setup for HPE J9981A OfficeConnect 1820 48G

import json, socket, time, os, pathlib
from datetime import datetime, timezone, timedelta

LISTEN_ADDR, LISTEN_PORT = "0.0.0.0", 514
LOG_DIR = pathlib.Path(r"D:\Prgrms\switch_logs"); LOG_DIR.mkdir(parents=True, exist_ok=True)
TZ = timezone(timedelta(hours=5))
def path_for_today():
    return LOG_DIR / (datetime.now(TZ).strftime("%Y-%m-%d") + ".jsonl")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_ADDR, LISTEN_PORT))
print(f"Listening on UDP/{LISTEN_PORT} ...")

while True:
    data, (src_ip, src_port) = sock.recvfrom(16384)
    evt = {
        "ts": datetime.now(TZ).isoformat(),
        "src_ip": src_ip,
        "raw": data.decode(errors="replace")
        # optional: parse severity/facility/app from raw here if you like
    }
    print(evt)
    with open(path_for_today(), "a", encoding="utf-8") as f:
        f.write(json.dumps(evt, ensure_ascii=False) + "\n")
