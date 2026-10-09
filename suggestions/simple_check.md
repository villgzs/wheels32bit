Íme egy kész, gyakorlatban használható Python script, ami pontosan azt csinálja, amit kérsz.

### `check_ha_packages.py`

```python
#!/usr/bin/env python3
"""
Home Assistant Core csomagok verzió-ellenőrzője.
Minden telepített csomagnál megpróbálja importálni és kiírni a verzióját.
"""

from __future__ import annotations

import importlib
import importlib.metadata
import sys
from typing import Optional

# Néhány csomagnál a pip neve ≠ az import név
IMPORT_NAME_MAP = {
    "Pillow": "PIL",
    "PyYAML": "yaml",
    "PyJWT": "jwt",
    "python-slugify": "slugify",
    "PyTurboJPEG": "turbojpeg",
    "opencv-python-headless": "cv2",
    "opencv-python": "cv2",
    "opencv-contrib-python": "cv2",
    "scikit-learn": "sklearn",
    "scikit-image": "skimage",
    "beautifulsoup4": "bs4",
    "protobuf": "google.protobuf",
    "pyserial": "serial",
    "pyserial-asyncio": "serial_asyncio",
    "pyserial-asyncio-fast": "serial_asyncio_fast",
    "Ruamel.yaml": "ruamel.yaml",
    "ruamel.yaml": "ruamel.yaml",
    "attrs": "attr",
    "typing-extensions": "typing_extensions",
    "importlib-metadata": "importlib.metadata",
    "importlib-resources": "importlib.resources",
    "backports.zoneinfo": "backports.zoneinfo",
    "async-timeout": "async_timeout",
    "frozenlist": "frozenlist",
    "multidict": "multidict",
    "yarl": "yarl",
    "aiohttp": "aiohttp",
    "home-assistant-bluetooth": "home_assistant_bluetooth",
    "ha-ffmpeg": "haffmpeg",
    "hass-nabucasa": "hass_nabucasa",
    "home-assistant-frontend": "hass_frontend",
    "home-assistant-intents": "home_assistant_intents",
}


def get_installed_distributions() -> list[tuple[str, str]]:
    """Visszaadja a telepített csomagokat (név, verzió) listaként."""
    dists = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata.get("Name") or dist.metadata.get("name")
        version = dist.version
        if name and version:
            dists.append((name, version))
    # ABC sorrend
    dists.sort(key=lambda x: x[0].lower())
    return dists


def guess_import_name(pkg_name: str) -> str:
    """Pip névből megpróbálja kitalálni az import nevet."""
    if pkg_name in IMPORT_NAME_MAP:
        return IMPORT_NAME_MAP[pkg_name]

    # leggyakoribb átalakítások
    name = pkg_name.replace("-", "_")
    return name


def get_module_version(module) -> Optional[str]:
    """Különböző helyeken keresi a verziót a modulban."""
    for attr in ("__version__", "VERSION", "version", "__VERSION__"):
        v = getattr(module, attr, None)
        if v is not None:
            return str(v)

    # néha a version egy objektum
    ver_obj = getattr(module, "version", None)
    if ver_obj is not None and hasattr(ver_obj, "__str__"):
        return str(ver_obj)

    return None


def check_package(pkg_name: str, pkg_version: str) -> None:
    import_name = guess_import_name(pkg_name)

    try:
        mod = importlib.import_module(import_name)
    except Exception as e:
        print(f"{pkg_name:40}  pip={pkg_version:12}  IMPORT FAIL: {type(e).__name__}: {e}")
        return

    mod_version = get_module_version(mod)

    if mod_version is None:
        print(f"{pkg_name:40}  pip={pkg_version:12}  import={import_name:25}  (nincs __version__)")
    else:
        match = "OK" if mod_version == pkg_version else "DIFF"
        print(
            f"{pkg_name:40}  pip={pkg_version:12}  "
            f"import={import_name:25}  mod={mod_version:12}  [{match}]"
        )


def main() -> None:
    print(f"Python: {sys.version}")
    print(f"Prefix: {sys.prefix}")
    print("-" * 100)

    packages = get_installed_distributions()
    print(f"Telepített csomagok száma: {len(packages)}\n")

    for name, version in packages:
        check_package(name, version)

    print("-" * 100)
    print("Kész.")


if __name__ == "__main__":
    main()
```

### Használat a Home Assistant konténerben

```bash
# másold be a scriptet, pl.
cat > /config/check_ha_packages.py << 'EOF'
... a fenti kód ...
EOF

chmod +x /config/check_ha_packages.py
python3 /config/check_ha_packages.py
```

### Mit csinál?

1. `importlib.metadata` segítségével összegyűjti az **összes** telepített csomagot (ez jobb, mint a `pip freeze`).
2. Minden csomagnál megpróbálja importálni (figyelembe véve a gyakori névkülönbségeket: `Pillow` → `PIL`, `PyYAML` → `yaml` stb.).
3. Kiírja:
   - pip szerinti nevet + verziót
   - az import nevet
   - a modul `__version__` (vagy `VERSION`) értékét
   - `OK` / `DIFF` / `IMPORT FAIL` státuszt

### Példa kimenet (részlet)

```
av                                       pip=19.0.0       import=av                       mod=19.0.0       [OK]
aiohttp                                  pip=3.14.3       import=aiohttp                  mod=3.14.3       [OK]
Pillow                                   pip=12.3.0       import=PIL                      mod=12.3.0       [OK]
PyYAML                                   pip=6.0.3        import=yaml                     mod=6.0.3        [OK]
some-c-extension                         pip=1.2.3        IMPORT FAIL: ModuleNotFoundError: ...
```

Ha szeretnéd, tudok belőle egy rövidebb bash változatot is, vagy olyat, ami csak a Home Assistant `requirements_all.txt` / `package_constraints.txt` csomagjait ellenőrzi.
