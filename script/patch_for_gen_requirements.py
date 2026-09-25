#!/usr/bin/env python3
"""Replace OVERRIDDEN_REQUIREMENTS_ACTIONS block (from = { to matching })."""

from pathlib import Path

FILE = Path("script/gen_requirements_all.py")  # állítsd be a helyes útvonalat

NEW = '''OVERRIDDEN_REQUIREMENTS_ACTIONS = {
    "pytest": {
        "exclude": set(),
        "include": set(),
        "markers": {},
    },
    "wheels_aarch64": {
        "exclude": set(),
        "include": INCLUDED_REQUIREMENTS_WHEELS,
        "markers": {},
    },
    # Pandas has issues building on armhf, it is expected they
    # will drop the platform in the near future (they consider it
    # "flimsy" on 386). The following packages depend on pandas,
    # so we comment them out.
    "wheels_armhf": {
        "exclude": {"env-canada", "noaa-coops", "pyezviz", "pykrakenapi"},
        "include": INCLUDED_REQUIREMENTS_WHEELS,
        "markers": {},
    },
    "wheels_armv7": {
        "exclude": set(),
        "include": INCLUDED_REQUIREMENTS_WHEELS,
        "markers": {},
    },
    "wheels_amd64": {
        "exclude": set(),
        "include": INCLUDED_REQUIREMENTS_WHEELS,
        "markers": {},
    },
    "wheels_i386": {
        "exclude": set(),
        "include": INCLUDED_REQUIREMENTS_WHEELS,
        "markers": {},
    },
}'''

content = FILE.read_text()
start_marker = "OVERRIDDEN_REQUIREMENTS_ACTIONS = {"

start = content.find(start_marker)
if start == -1:
    raise SystemExit("Nem található: OVERRIDDEN_REQUIREMENTS_ACTIONS = {")

# Keressük a matching záró }-t (figyelembe véve a beágyazott kapcsos zárójeleket)
i = start + len(start_marker)
depth = 1
while i < len(content) and depth > 0:
    if content[i] == "{":
        depth += 1
    elif content[i] == "}":
        depth -= 1
    i += 1

if depth != 0:
    raise SystemExit("Nem található a matching záró }")

# Az i most a záró } után van
end = i
new_content = content[:start] + NEW + content[end:]
FILE.write_text(new_content)
print("Csere sikeres.")
