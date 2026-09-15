A wheel-ek gyártásához a core repositoryból **ezek az állományok szükségesek**:

### Minimálisan szükséges fájlok

| Fájl | Miért kell |
|------|-----------|
| `requirements.txt` | Core függőségek listája (core job) |
| `requirements_all.txt` | Az összes integráció függőségeinek forrása |
| `homeassistant/package_constraints.txt` | Constraints fájl a buildhez |
| `script/gen_requirements_all.py` | Generálja a `requirements_all_wheels_*.txt` fájlokat |
| `.python-version` | Python verzió meghatározása az init jobban |

### Amit a generátor (`script/gen_requirements_all.py`) még használ

A script végigmegy a komponenseken, ezért gyakorlatilag kell:

- `homeassistant/components/**/manifest.json` (összes integráció manifestje)
- Esetleg más segédfájlok a `script/` mappából

### Amit **nem** kell a wheel buildhez

- `homeassistant/` Python forráskódja (`.py` fájlok)
- `tests/`
- `Dockerfile`, `rootfs/`
- Dokumentáció, stb.

### Gyakorlati javaslat

Ha te magad buildelsz wheel-eket (pl. 32-bithez), a legtisztább megoldás:

1. Checkoutold a teljes core-t a kívánt verzióra (egyszerűbb).
2. Vagy csak ezeket másold ki:

```bash
requirements.txt
requirements_all.txt
homeassistant/package_constraints.txt
script/gen_requirements_all.py
.python-version
# + a homeassistant/components mappa (a manifest.json-ök miatt)
```

Ha már előre legeneráltad a `requirements_all_wheels_*.txt` fájlokat, akkor még kevesebb is elég:

```text
requirements.txt
requirements_all_wheels_amd64.txt   # vagy a megfelelő arch
requirements_all_wheels_aarch64.txt
homeassistant/package_constraints.txt
```

Szeretnéd, hogy összeállítsak egy minimális fájllistát / sparse-checkout példát is?

A `script/gen_requirements_all.py` a Home Assistant függőségkezelésének központi generáló scriptje. Így működik:

### Fő feladata

Automatikusan legenerálja a következő fájlokat:

- `requirements.txt` (csak a core függőségek)
- `requirements_all.txt` (core + összes integráció függősége)
- `requirements_test_all.txt` (tesztekhez)
- `requirements_all_wheels_*.txt` (wheel buildhez, architektúránként)
- Frissíti a `homeassistant/package_constraints.txt` egy részét

### Hogyan gyűjti össze a függőségeket?

1. **Core függőségek**  
   A `pyproject.toml` → `[project.dependencies]` részből olvassa ki.

2. **Integrációk függőségei**  
   Végigmegy a `homeassistant/components/*/manifest.json` fájlokon, és kiveszi belőlük a `requirements` listát.

3. **Rekurzív függőségek**  
   Ha egy integráció más integrációktól függ (`dependencies` mező a manifestben), azokat is rekurzívan beveszi.

4. **Kizárások**  
   Bizonyos csomagokat (pl. `bluepy`, `evdev`) kikommentez, mert nem telepíthetők minden rendszeren (`EXCLUDED_REQUIREMENTS_ALL`).

5. **Wheel-specifikus változatok**  
   A `wheels_amd64` / `wheels_aarch64` esetén bizonyos csomagokat visszaenged (pl. `evdev`).

### Futtatás

```bash
# Normál generálás
python3 -m script.gen_requirements_all

# CI / wheel buildhez (generálja a requirements_all_wheels_*.txt fájlokat is)
python3 -m script.gen_requirements_all ci
```

### Fontos részek a kódból

```python
# Core függőségek a pyproject.toml-ből
def core_requirements() -> list[str]:
    data = tomllib.loads(Path("pyproject.toml").read_text())
    return data["project"]["dependencies"]

# Integrációk manifestjeiből
def gather_requirements_from_manifests(...):
    # végigmegy homeassistant/components/*/manifest.json-ön

# Rekurzív függőséggyűjtés
def gather_recursive_requirements(domain: str, seen: set[str] | None = None):
    ...
```

### Összefoglaló folyamat

```
pyproject.toml  +  homeassistant/components/*/manifest.json
        ↓
   gen_requirements_all.py
        ↓
requirements.txt
requirements_all.txt
requirements_all_wheels_amd64.txt
requirements_all_wheels_aarch64.txt
(+ package_constraints.txt frissítése)
```

A wheel build workflow (`wheels.yml`) ezért hívja meg a `ci` módot az `init` jobban, hogy legenerálja a `requirements_all_wheels_*.txt` fájlokat, amiket aztán a tényleges wheel builder használ.

Itt a minimális fájllista és a sparse-checkout példa a wheel-ek gyártásához.

### 1. Minimális fájllista (ha már legeneráltad a wheels fájlokat)

Ha a `requirements_all_wheels_*.txt` fájlok már megvannak:

```text
requirements.txt
requirements_all_wheels_amd64.txt      # vagy a neked kellő arch
requirements_all_wheels_aarch64.txt
homeassistant/package_constraints.txt
```

### 2. Minimális lista, ha a generátort is futtatni akarod

```text
.python-version
pyproject.toml
requirements.txt
requirements_all.txt
homeassistant/package_constraints.txt
script/gen_requirements_all.py
script/hassfest/                  # a model.py és társai miatt
homeassistant/components/         # az összes manifest.json miatt
```

A `homeassistant/components/` mappa a legnagyobb, de a generátornak szüksége van rá.

### 3. Sparse-checkout példa (ajánlott)

```yaml
- name: Checkout minimal files for wheels
  uses: actions/checkout@v4
  with:
    repository: home-assistant/core
    ref: ${{ steps.ha.outputs.version }}   # pl. 2026.9.2
    sparse-checkout: |
      .python-version
      pyproject.toml
      requirements.txt
      requirements_all.txt
      homeassistant/package_constraints.txt
      script/gen_requirements_all.py
      script/hassfest
      homeassistant/components
    sparse-checkout-cone-mode: false
```

### 4. Még takarékosabb változat (ha csak a kész wheels listákat használod)

```yaml
- name: Checkout minimal for wheels build
  uses: actions/checkout@v4
  with:
    repository: home-assistant/core
    ref: ${{ steps.ha.outputs.version }}
    sparse-checkout: |
      requirements.txt
      homeassistant/package_constraints.txt
    sparse-checkout-cone-mode: false
```

Majd a `requirements_all_wheels_*.txt` fájlokat külön artifactból vagy saját generálásból adod hozzá.

---

**Ajánlás a te 32-bites esetedre:**

Használd a **3. sparse-checkout** változatot + futtasd le a generátort:

```bash
python3 -m script.gen_requirements_all ci
```

Így megkapod a `requirements_all_wheels_*.txt` fájlokat anélkül, hogy a teljes core repository-t le kellene töltened.
