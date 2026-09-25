#!/usr/bin/env python3
"""
Insert ARM32 SIGBUS fix into home-assistant/wheels builder/pip.py

Usage:
    python3 insert_arm32_fix.py [path/to/builder/pip.py]
"""

from pathlib import Path
import sys
import re

ARM32_FIX = '''
    # === ARM32 SIGBUS fix ===
    arch = os.environ.get("ARCH", "")
    if arch in ("armv7", "armhf"):
        # Force the compiler to never generate unaligned accesses
        # This is the most reliable way to avoid SIGBUS on strict ARM32 CPUs
        arm_flags = "-mno-unaligned-access -mfloat-abi=hard"
        # Optional more specific flags:
        # arm_flags = "-march=armv7-a -mfpu=neon-vfpv4 -mfloat-abi=hard -mno-unaligned-access"

        build_env["CFLAGS"] = f"{build_env.get('CFLAGS', '')} {arm_flags}".strip()
        build_env["CXXFLAGS"] = f"{build_env.get('CXXFLAGS', '')} {arm_flags}".strip()
        build_env["FFLAGS"] = f"{build_env.get('FFLAGS', '')} {arm_flags}".strip()
        # NumPy specific
        build_env["NPY_CFLAGS"] = arm_flags
        build_env["NPY_CXXFLAGS"] = arm_flags
'''

# A hely, ami után beillesztünk
MARKER = 'build_env["MAKEFLAGS"] = f"-j{cpu}"'


def insert_fix(content: str) -> str:
    """Insert the ARM32 fix after every MAKEFLAGS line (idempotent)."""
    if "=== ARM32 SIGBUS fix ===" in content:
        print("ARM32 SIGBUS fix already present – nothing to do.")
        return content

    lines = content.splitlines(keepends=True)
    new_lines = []
    inserted = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Keressük a MAKEFLAGS sort
        if MARKER in line:
            # Ellenőrizzük, hogy a következő sorok között nincs-e már a fix
            # (biztonság kedvéért)
            already = False
            for j in range(i + 1, min(i + 15, len(lines))):
                if "=== ARM32 SIGBUS fix ===" in lines[j]:
                    already = True
                    break

            if not already:
                # Beillesztjük a fixet
                # Megtartjuk az eredeti behúzást
                indent = re.match(r'^(\s*)', line).group(1)
                fix_lines = ARM32_FIX.strip("\n").splitlines()
                for fl in fix_lines:
                    # Az ARM32_FIX már tartalmazza a helyes behúzást (4 space)
                    new_lines.append(fl + "\n")
                inserted += 1
                print(f"  → Inserted ARM32 fix after line {i+1}")

        i += 1

    if inserted == 0:
        print("WARNING: Could not find the MAKEFLAGS marker. No changes made.")
        return content

    print(f"Successfully inserted ARM32 fix in {inserted} place(s).")
    return "".join(new_lines)


def main():
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        # Alapértelmezett relatív útvonal a wheels repo gyökeréből
        target = Path("builder/pip.py")

    if not target.is_file():
        print(f"Error: File not found: {target}")
        sys.exit(1)

    print(f"Processing: {target}")
    original = target.read_text(encoding="utf-8")

    modified = insert_fix(original)

    if modified != original:
        # Backup
        backup = target.with_suffix(target.suffix + ".bak")
        backup.write_text(original, encoding="utf-8")
        print(f"Backup created: {backup}")

        target.write_text(modified, encoding="utf-8")
        print(f"Updated: {target}")
    else:
        print("No changes written.")


if __name__ == "__main__":
    main()
