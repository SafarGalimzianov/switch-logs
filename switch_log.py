# logs setup for HPE J9981A OfficeConnect 1820 48G

import json, socket, time, os, pathlib
from datetime import datetime, timezone, timedelta

LISTEN_ADDR, LISTEN_PORT = '0.0.0.0', 514
LOG_DIR = pathlib.Path(r'D:\Prgrms\switch-logs\logs\hpe'); LOG_DIR.mkdir(parents=True, exist_ok=True)
TZ = timezone(timedelta(hours=5))
def path_for_today():
    return LOG_DIR / (datetime.now(TZ).strftime('%Y-%m-%d') + '.jsonl')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_ADDR, LISTEN_PORT))
sock.settimeout(1.0)  # let the loop wake up so Ctrl+C is handled promptly
print(f'Listening on UDP/{LISTEN_PORT} ...')

try:
    while True:
        try:
            data, (src_ip, src_port) = sock.recvfrom(16384)
        except socket.timeout:
            continue  # check for Ctrl+C again

        evt = {
            'ts': datetime.now(TZ).isoformat(),
            'src_ip': src_ip,
            'raw': data.decode(errors='replace')
        }
        evt_readable = {
            'ts': datetime.now(TZ).strftime('%m-%d %H:%M:%S'),
            'src_ip': src_ip,
            'raw': data.decode(errors='replace')
        }
        printable = f"{evt_readable['ts']}: {evt_readable['raw']}"
        print(printable)
        with open(path_for_today(), 'a', encoding='utf-8') as f:
            f.write(json.dumps(evt, ensure_ascii=False) + '\n')
except KeyboardInterrupt:
    print('\nStopping (Ctrl+C)...')
finally:
    sock.close()
    print('Socket closed.')
