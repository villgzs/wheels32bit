```
uv pip install --system --index-strategy unsafe-best-match --no-binary av "av==19.0.0"
```

Igen, össze lehet rakni. Íme egy működő bash szkript:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Használat: ./pack-installed.sh av
# Opcionálisan: ./pack-installed.sh av /tmp/wheels

PKG="${1:-}"
OUTDIR="${2:-./wheels}"

if [[ -z "$PKG" ]]; then
  echo "Használat: $0 <csomagnév> [kimeneti_könyvtár]"
  echo "Példa:    $0 av"
  echo "Példa:    $0 av /tmp/wheels"
  exit 1
fi

# Python elérési út (lehetőleg a venv-ből)
PYTHON="${PYTHON:-python3}"

echo "==> Csomag keresése: $PKG"

# site-packages meghatározása
SITE=$("$PYTHON" -c "import sysconfig; print(sysconfig.get_path('purelib'))")
echo "    site-packages: $SITE"

# Modul és dist-info megkeresése
MODULE_DIR=""
DISTINFO_DIR=""

# 1. Próbáljuk importtal
MODULE_PATH=$("$PYTHON" -c "
import importlib, os, sys
try:
    m = importlib.import_module('$PKG')
    print(os.path.dirname(m.__file__) if hasattr(m, '__file__') and m.__file__ else '')
except Exception as e:
    sys.stderr.write(str(e) + '\n')
    sys.exit(1)
" 2>/dev/null || true)

if [[ -n "$MODULE_PATH" && -d "$MODULE_PATH" ]]; then
  MODULE_DIR="$MODULE_PATH"
fi

# 2. dist-info keresése
shopt -s nullglob
CANDIDATES=("$SITE/$PKG"*.dist-info "$SITE/${PKG//-/_}"*.dist-info)
shopt -u nullglob

for d in "${CANDIDATES[@]}"; do
  if [[ -d "$d" ]]; then
    DISTINFO_DIR="$d"
    break
  fi
done

# Ha az import nem adott modult, próbáljuk a top_level.txt-ből
if [[ -z "$MODULE_DIR" && -n "$DISTINFO_DIR" && -f "$DISTINFO_DIR/top_level.txt" ]]; then
  TOP=$("$PYTHON" -c "
with open('$DISTINFO_DIR/top_level.txt') as f:
    print(f.readline().strip())
")
  if [[ -n "$TOP" && -d "$SITE/$TOP" ]]; then
    MODULE_DIR="$SITE/$TOP"
  elif [[ -f "$SITE/${TOP}.py" ]]; then
    # single-file modul
    MODULE_DIR=""
    SINGLE_FILE="$SITE/${TOP}.py"
  fi
fi

# Egyszerű fallback: $SITE/$PKG
if [[ -z "$MODULE_DIR" && -d "$SITE/$PKG" ]]; then
  MODULE_DIR="$SITE/$PKG"
fi
if [[ -z "$MODULE_DIR" && -d "$SITE/${PKG//-/_}" ]]; then
  MODULE_DIR="$SITE/${PKG//-/_}"
fi

if [[ -z "$DISTINFO_DIR" ]]; then
  echo "Hiba: nem találtam .dist-info mappát a(z) '$PKG' csomaghoz a $SITE alatt."
  exit 1
fi

if [[ -z "$MODULE_DIR" && -z "${SINGLE_FILE:-}" ]]; then
  echo "Hiba: nem találtam a modul mappáját / fájlját."
  exit 1
fi

echo "    modul:     ${MODULE_DIR:-$SINGLE_FILE}"
echo "    dist-info: $DISTINFO_DIR"

# Verzió kiolvasása a METADATA-ból
VERSION=$("$PYTHON" -c "
from pathlib import Path
for line in Path('$DISTINFO_DIR/METADATA').read_text().splitlines():
    if line.startswith('Version:'):
        print(line.split(':',1)[1].strip())
        break
")
echo "    verzió:    $VERSION"

# Ideiglenes könyvtár
WORKDIR=$(mktemp -d /tmp/pack-XXXXXX)
trap 'rm -rf "$WORKDIR"' EXIT

echo "==> Másolás → $WORKDIR"

if [[ -n "$MODULE_DIR" ]]; then
  cp -a "$MODULE_DIR" "$WORKDIR/"
fi
if [[ -n "${SINGLE_FILE:-}" ]]; then
  cp -a "$SINGLE_FILE" "$WORKDIR/"
fi

# dist-info neve legyen szabványos: name-version.dist-info
DISTINFO_NAME=$(basename "$DISTINFO_DIR")
cp -a "$DISTINFO_DIR" "$WORKDIR/$DISTINFO_NAME"

# Kimeneti könyvtár
mkdir -p "$OUTDIR"

echo "==> Wheel készítése..."
"$PYTHON" -m pip install -q wheel
"$PYTHON" -m wheel pack "$WORKDIR" -d "$OUTDIR"

echo ""
echo "Kész:"
ls -lh "$OUTDIR"/${PKG}*.whl 2>/dev/null || ls -lh "$OUTDIR"/*.whl
```

### Használat

```bash
chmod +x pack-installed.sh

# Alap (./wheels mappába)
./pack-installed.sh av

# Saját kimeneti könyvtárral
./pack-installed.sh av /tmp/my-wheels

# Másik Pythonnal / venv-ből
PYTHON=/path/to/venv/bin/python ./pack-installed.sh av
```

### Mit csinál a szkript?

1. Megkeresi a `site-packages`-t  
2. Importtal + `.dist-info` alapján megtalálja a modult  
3. Kimásolja a modul mappát + `.dist-info`-t egy ideiglenes könyvtárba  
4. `wheel pack`-kel létrehozza a `.whl` fájlt  
5. Kitakarítja az ideiglenes mappát  

**Figyelem:** compiled extension (`.so`) esetén a kapott wheel csak ugyanarra a platformra (OS + architektúra + Python verzió) lesz használható.


```
b7a1f97ea5d8:/data# apk add nano
WARNING: updating https://dl-cdn.alpinelinux.org/alpine/v3.24/main/armv7/APKINDEX.tar.gz: DNS: transient error (try again later)
(1/1) Installing nano (9.2-r0)
Executing busybox-1.37.0-r31.trigger
OK: 770.5 MiB in 211 packages
b7a1f97ea5d8:/data# nano wheelminer.sh
b7a1f97ea5d8:/data# bash wheelminer.sh av
==> Csomag keresése: av
    site-packages: /usr/local/lib/python3.14/site-packages
    modul:     /usr/local/lib/python3.14/site-packages/av
    dist-info: /usr/local/lib/python3.14/site-packages/av-19.0.0.dist-info
    verzió:    19.0.0
==> Másolás → /tmp/pack-FJpNCK
==> Wheel készítése...
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
Repacking wheel as ./wheels/av-19.0.0-cp314-cp314-linux_armv7l.whl...OK

Kész:
-rw-r--r--    1 root     root        1.6M Oct  8 11:55 ./wheels/av-19.0.0-cp314-cp314-linux_armv7l.whl
```

```
auditwheel repair ./wheels/av-19.0.0-cp314-cp314-linux_armv7l.whl -w ./wheelhouse/
```
