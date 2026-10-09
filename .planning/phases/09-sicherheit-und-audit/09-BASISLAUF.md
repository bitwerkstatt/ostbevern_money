---
phase: "9"
art: basislauf
head: 1d0df35da1842daec515b40dd62f8d918e240105
erstellt: 2026-10-09T06:19:00Z
pytest_passed: 681
pytest_skipped: 0
alle_py: byte-identisch
vitest_tests: ausstehend
e2e_ci_passed: ausstehend
e2e_mobil_passed: ausstehend
e2e_texte_passed: ausstehend
---

# Phase 9: Basislauf (D-23)

Ein Lauf der vollständigen CI-Kette auf dem Code nach Welle 1 (Pläne 09-01 und 09-02). `head` im Frontmatter ist der Commit, dessen Code getestet wurde. Die Verifier prüfen mit `git diff --quiet <head> HEAD -- pipeline app daten scripts .github`, dass sich seitdem kein Codepfad geändert hat. Vor und nach dem Lauf war `git status --porcelain -- pipeline app daten scripts .github` leer (der Lauf hat nichts verändert).

Alle Zahlen in diesem Dokument stammen aus Befehlen, die in diesem Plan gelaufen sind.

## Pipeline

Arbeitsverzeichnis: Worktree des Executors auf `head`. Plattform Linux, Python 3.12 (uv 0.9.26).

### 1. Umgebung und statische Prüfungen

```
$ uv sync --locked --directory pipeline
exit 0
$ (cd pipeline && uv run ruff check .)
All checks passed!
exit 0
$ (cd pipeline && uv run ruff format --check .)
51 files already formatted
exit 0
```

Dauer: unter 1 s für alle drei Befehle zusammen (Wanduhr, ganze Sekunden; die Umgebung war aus dem uv-Cache warm).

### 2. Volle pytest-Suite

```
$ uv run --directory pipeline pytest -p no:cacheprovider -rs -q
681 passed in 350.31s (0:05:50)
exit 0
```

- Keine `SKIPPED`-Zeile in der Ausgabe, `pytest_skipped: 0`.
- Hinweis zum ersten Lauf: Der erste Lauf auf einer frischen Worktree-Kopie ohne `app/node_modules` endete mit `680 passed, 1 skipped in 350.66s`. Übersprungen wurde `tests/test_formatiere.py:463` (`test_port_wie_format_ts`), weil `app/node_modules/typescript/package.json` fehlte. Der Skip ist umgebungsbedingt (kein Codefehler). Daraufhin lief `npm ci` in `app/` (Linux, `node_modules` ist über `app/.gitignore` ausgeschlossen) und die volle Suite wurde erneut gestartet. Maßgeblich ist dieser zweite Lauf mit 681 Tests und null Skips. Die CI-Pipeline-Stufe hat kein `node_modules` und überspringt diesen Test regulär; hier lief er mit.

### 3. Reproduzierbarkeit: alle.py

```
$ uv run --directory pipeline python alle.py --jahr 2026
exit 0
Dauer: 29 s
```

Entscheidende Ausgabezeilen (unverändert aus der Ausgabe kopiert):

```
Jahrgang 2026: raw_data/haushalt-2026.pdf (400 Seiten erwartet), 15 Seitenbereiche, Sollwerte geladen.
Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte.
Schritt 02: 14899 Planzeilen geschrieben.
Schritt 03: 63 Einträge geschrieben: daten/aufbereitet/produkte.json
Schritt 03: 827 Einträge geschrieben: daten/aufbereitet/grundzahlen.csv
Schritt 03: 229 Einträge geschrieben: daten/aufbereitet/erlaeuterungen.csv
Schritt 04: 959 Zeilen geschrieben: daten/aufbereitet/investitionen.csv
Schritt 04: 8 Zeilen geschrieben: daten/aufbereitet/ve_faelligkeiten.csv
Schritt 04: 959 Zeilen geschrieben: daten/zwischen/investitionen_pb.csv
Querschnitte: 1152 Werte geschrieben.
Schritt 05: 162 Zeilen geschrieben: daten/aufbereitet/stellenplan.csv
Schritt 07: geschrieben: app/src/data/haushalt.json
Schritt 07: geschrieben: app/src/data/stellenplan.json
Schritt 07: geschrieben: app/src/data/produkte.json
Schritt 07: geschrieben: app/src/data/investitionen.json
Schritt 07: geschrieben: app/src/data/texte.json
Schritt 08: 2496 Belege, 33 ohne Markierung, 231 Seiten, 0 Bilder neu gerendert
```

Prüfregeln 1 bis 10 (Schritt 06), jede aus der Ausgabe kopiert:

```
Schritt 06: Regel 1: grün (6593 Werte)
Schritt 06: Regel 2: grün (7994 Werte)
Schritt 06: Regel 3: grün (114 Werte)
Schritt 06: Regel 4: grün (259 Werte)
Schritt 06: Regel 5: grün (150 Werte)
Schritt 06: Regel 6: grün (1964 Werte)
Schritt 06: Regel 7: grün (1152 Werte)
Schritt 06: Regel 8: grün (820 Werte)
Schritt 06: Regel 9: grün (12 Werte)
Schritt 06: Regel 10: grün (19 Werte)
Schritt 06: Veraltete Befunde: 0
```

### 4. Byte-Identität nach alle.py

```
$ git diff --stat --exit-code -- daten app/src/data
(leer)
exit 0
$ git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen
(leer)
exit 0
```

Ergebnis Pipeline: alle Schritte grün, `daten/`, `app/src/data/` und `app/public/quellen` byte-identisch beziehungsweise unverändert (`alle_py: byte-identisch`).

## App (Scratch-Kopie)

ausstehend (Aufgabe 2).

## Playwright

ausstehend (Aufgabe 2).

## Verifikationsstatus vor der Re-Verifikation

ausstehend (Aufgabe 2).

## npm audit

ausstehend (Aufgabe 2).

## Hinweise für die Verifier

ausstehend (Aufgabe 2).
