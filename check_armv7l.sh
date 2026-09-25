#!/bin/bash

apk add file

echo "=== Telepített Python csomagok armv7l kompatibilitási ellenőrzése ==="
echo

BAD_PACKAGES=()

pip list --format=freeze | while IFS='==' read -r pkg version; do
    echo " Package: $pkg $version"
    location=$(python -c "
import importlib.util
try:
    spec = importlib.util.find_spec('$pkg')
    print(spec.origin if spec and spec.origin else '')
except Exception:
    print('')
" 2>/dev/null)

    [ -z "$location" ] && continue
    pkg_dir=$(dirname "$location")

    so_files=$(find "$pkg_dir" -type f \( -name "*.so" -o -name "*.so.*" \) 2>/dev/null \
        | grep -vE 'libstdc\+\+|libgcc_s|liblzma|libffi|libssl|libcrypto|libz\.|libbz2')

    [ -z "$so_files" ] && continue

    # echo "Csomag: $pkg $version"
    has_error=0

    for so in $so_files; do
        base=$(basename "$so")
        info=$(file -b "$so" 2>/dev/null)

        if echo "$info" | grep -qiE 'ELF.*32-bit.*ARM|ARM.*32-bit'; then
            echo "  ✓ OK: $base"
        else
            echo "  ✗ HIBA: $base"
            echo "       → $info"
            has_error=1
        fi
    done

    if [ $has_error -eq 1 ]; then
        echo "  *** Ez a csomag NEM armv7l kompatibilis! ***"
        # A while subshell miatt fájlba írjuk
        echo "$pkg==$version" >> /tmp/bad_packages.txt
    fi
    echo
done

echo
echo "=============================================="
echo "=== HIBÁS CSOMAGOK ÖSSZEFOGLALÓ LISTÁJA ==="
echo "=============================================="

if [ -f /tmp/bad_packages.txt ]; then
    sort -u /tmp/bad_packages.txt
    echo
    echo "Összesen $(sort -u /tmp/bad_packages.txt | wc -l) hibás csomag."
    mv /tmp/bad_packages.txt ./bad_packages.txt
else
    echo "Nincs hibás csomag."
fi

echo "=== Ellenőrzés kész ==="
