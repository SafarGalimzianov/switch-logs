# Summary of Python string formatting features

s = 'hi\nµ'
evt = {'ts': '2025-08-27T12:34:56', 'raw': 'port up'}

# 1) str.format
print('{}: {}'.format(evt['ts'], evt['raw']))                  # positional
print('{ts}: {raw}'.format(ts=evt['ts'], raw=evt['raw']))      # named
print('{ts}: {raw}'.format(**evt))                             # dict unpack

# 2) f-strings (expressions inline)
print(f"{evt['ts']}: {evt['raw']}")

# 3) Conversions: !s (str), !r (repr), !a (ascii)
print(f'{s!s}')    # str -> prints actual newline + µ
print(f'{s!r}')    # repr -> shows escapes and quotes
print(f'{s!a}')    # ascii -> non-ASCII escaped

# 4) __str__ vs __repr__
class Thing:
    def __repr__(self): return 'Thing(id=42)'
    def __str__(self):  return 'Thing pretty'

t = Thing()
print(f'{t}')      # uses __str__
print(f'{t!r}')    # uses __repr__
print('{x!r}'.format(x=t))  # same as above via format

# 5) Raw strings vs conversions
print(r'{s}')      # raw literal; not an f-string -> prints "{s}"
print(rf'{s}')     # raw only affects literal parts; inserted value still normal
print(rf'{s!r}')   # conversion still applies; raw affects only surrounding text

# 6) Escaping braces
print(f'{{literal}} {s!r}')
print('{{literal}}: {}'.format('ok'))