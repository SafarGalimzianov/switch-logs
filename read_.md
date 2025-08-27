It’s the error handler for decoding bytes to text. With errors='replace', any invalid byte sequence for the chosen codec is not fatal; it gets replaced with the Unicode replacement character � (U+FFFD) instead of raising UnicodeDecodeError. This keeps your logging robust if a packet has bad bytes.
Tip: make the encoding explicit so behavior is predictable.

```python
# ...existing code...
        evt = {
            'ts': datetime.now(TZ).isoformat(),
            'src_ip': src_ip,
            'raw': data.decode('utf-8', errors='replace')
        }
        evt_readable = {
            'ts': datetime.now(TZ),
            'src_ip': src_ip,
            'raw': data.decode('utf-8', errors='replace')
        }
# ...existing code...
```
Other handlers you might see:

strict (default): raise an exception on bad bytes
ignore: drop bad bytes silently
backslashreplace: show escapes like \xNN for bad bytes