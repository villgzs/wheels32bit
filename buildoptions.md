Íme a még nem használt opciók pontos jelentése a Home Assistant wheels builder alapján:

### `--single`
- **Típus:** flag (kapcsoló)
- **Alapértelmezett:** `False`
- **Mit csinál:**  
  Minden csomagot **egyenként** fordít le (`pip wheel csomagnév==verzió`), nem egy nagy `pip wheel -r requirements.txt` hívással.

**Előnyei:**
- Egy csomag hibája nem állítja le az egész buildet (a többi tovább megy).
- Jobban kontrollálható, melyik csomagnál bukik el.
- Timeout esetén is több csomag készülhet el (mert nem egyetlen hosszú folyamat fut).

**Hátránya:** lassabb, mert minden csomagnál újra fel kell építenie a függőségi fát.

Jelenleg a workflow a „mindent egyszerre” módot használja (`--single` nélkül).

---

### `--test`
- **Típus:** flag
- **Alapértelmezett:** `False`
- **Mit csinál:**  
  Lefuttatja a teljes build + auditwheel folyamatot, de **nem tölti fel** az eredményt (`run_upload` kihagyása).

Hasznos teszteléshez, ha csak azt akarod ellenőrizni, hogy a fordítás sikerül-e, anélkül hogy bármit is felülírnál a távoli indexen.

---

### `--local`
- **Típus:** flag
- **Alapértelmezett:** `False`
- **Mit csinál:**  
  Nem requirements fájlból dolgozik, hanem a **jelenlegi munkakönyvtárból** (`/data`) próbál wheel-t építeni (`pip wheel .`).

Tipikusan akkor hasznos, ha egyetlen Python csomag forráskódját másoltad be a konténerbe, és azt akarod lefordítani.

---

### `--prebuild-dir`
- **Típus:** útvonal (könyvtár)
- **Mit csinál:**  
  Nem fordít semmit. Csak a megadott könyvtárban lévő `.whl` fájlokat másolja be a kimeneti mappába, majd lefuttatja rajtuk az auditwheel-t és (ha nincs `--test`) feltölti őket.

Használati eset:  
ha már van kész wheel-készleted (pl. korábbi futásból vagy más gépről), és csak azokat szeretnéd „rendbe tenni” + feltölteni.

---

### `--pip`
- **Típus:** string (csomaglista, pontosvesszővel elválasztva)
- **Mit csinál:**  
  A fordítás **előtt** telepít extra Python csomagokat a builder környezetbe (`pip install ...`).

Példa:
```bash
--pip "cython==3.0.10;numpy<2.0;setuptools-scm"
```

Ez hasznos, ha bizonyos build-time függőségeket (pl. régebbi Cython, speciális setuptools stb.) akarsz biztosítani, mielőtt a tényleges wheel-ek fordítása elkezdődik.

---

### Összefoglaló táblázat

| Opció            | Típus     | Alapértelmezett | Fő hatás                                      | Mikor hasznos?                          |
|------------------|-----------|------------------|-----------------------------------------------|-----------------------------------------|
| `--single`       | flag      | ki               | Csomagonként külön fordít                     | Hibák izolálása, jobb timeout-tűrés     |
| `--test`         | flag      | ki               | Nincs feltöltés                               | Csak tesztelés                          |
| `--local`        | flag      | ki               | Helyi forrásból fordít (`pip wheel .`)        | Egyedi csomag fordítása                 |
| `--prebuild-dir` | path      | –                | Már kész wheel-eket vesz át                   | Kész wheel-ek feltöltése                |
| `--pip`          | string    | –                | Extra Python csomagok telepítése build előtt  | Speciális build-függőségek              |

A te jelenlegi workflow-d a leggyakoribb „normál” módot használja (requirements fájl + egyszerre fordítás + feltöltés). A `--single` és a nagyobb `--timeout` kombinációja különösen hasznos lehet a hosszú armv7 build-eknél.
