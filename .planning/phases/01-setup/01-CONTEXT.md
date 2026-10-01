# Phase 1: Setup - Context

**Gathered:** 2026-10-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Ein leeres, aber lauffähiges Gerüst für beide Projektteile:
- **Pipeline:** uv-Projekt in `pipeline/` (Python 3.12, pdfplumber, polars, typer, pytest), Bibliothek `ostbevern/`, Jahrgangskonfiguration für 2026, grüner Rauchtest
- **App:** Vue-3-Grundgerüst in `app/` (TS, Vite, Web Awesome, vue-echarts, Hash-Router) mit den neu geschriebenen Münster-Basiskomponenten; `npm run build`, `vue-tsc` und ESLint laufen fehlerfrei
- **Repo:** Struktur nach Spez. 7, PDF unter `raw_data/`, Konventionen und Befehle in `.claude/CLAUDE.md`, CI-Workflow in GitHub Actions

Keine Extraktion (ab Phase 2), keine fachlichen Seiten (ab Phase 5), kein Deployment (Phase 7).

</domain>

<decisions>
## Implementation Decisions

### Münster-Übernahme
- **D-01:** Den Münster-Code (`codeformuenster/haushalt-muenster-2026`) nutzen wir **nur als Vorlage** und schreiben ihn selbst neu. Es werden keine Dateien 1:1 kopiert und das Repo wird nicht geklont.
- **D-02:** Die neuen Komponenten behalten die **Namen und Props/Schnittstellen der Münster-Komponenten** (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`, `charts/echartsTheme.ts`, `lib/bildschirm.ts`). Die Umsetzung schreiben wir selbst. So lassen sich Ideen aus Münster leicht übertragen.
- **D-03:** In Phase 1 entstehen **nur die Basiskomponenten**: `PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `format.ts`, `echartsTheme.ts` und `bildschirm.ts`. `GlossarBegriff`, `BegriffeListe`, `ProduktAkkordeon` und Sankey folgen in Phase 5, `QuelleSeitenleiste` in Phase 7, jeweils erst bei Bedarf.
- **D-04:** Die App bekommt eine **eigene Ostbevern-Farbpalette** (z. B. angelehnt an die Gemeindefarben), als Web-Awesome-Theme und als ECharts-Theme (`echartsTheme.ts`). Die Kontraste müssen schon jetzt dem a11y-Ziel genügen (Lighthouse ≥ 95).
- **D-05:** Lizenz: **MIT** (`LICENSE` im Root). README und App (Fußzeile oder Über-Hinweis) nennen „Inspiriert von Münster Money (Code for Münster)“ mit Link. — **Reversibility:** one-way — Nach der Veröffentlichung lässt sich eine MIT-Lizenz für bereits verteilte Versionen nicht zurücknehmen.

### Jahrgangskonfiguration
- **D-06:** Format TOML, Ort `pipeline/jahrgaenge/2026.toml`. Die Datei wird mit `tomllib` aus der Standardbibliothek gelesen, es kommt keine weitere Abhängigkeit dazu. Für 2027 legt man eine neue Datei daneben.
- **D-07:** Die Jahrgangsdatei enthält **alles PDF-Spezifische**:
  - Haushaltsjahr und PDF-Pfad
  - Spaltenköpfe je Plantyp (Ergebnisplan 6 Spalten; Finanzplan und Investitionen 7 Spalten mit VE)
  - Seitenbereiche der Kapitel (Spez. 2)
  - Kopfzeilen-Muster für die Seitenklassifikation
  - erwartete Anzahlen (15 PB, 63 Produkte)

  **Fachliche Regeln bleiben im Code**, darunter die Zeilenformeln, die Zeilennummern des Minderaufwands und der Ausschluss von TP 27/28.
- **D-08:** Die Sollwerte (Anhang B) liegen in einer **eigenen Datei je Jahrgang**: `pipeline/jahrgaenge/2026_sollwerte.toml`. Die Tests laden sie, im Testcode stehen keine Jahrgangszahlen. Phase 1 legt die Datei mit Struktur an (mindestens Satzung § 1 bzw. B.1-Kopfwerte). Phase 2 füllt sie vollständig.
- **D-09:** Den Jahrgang wählt die Option **`--jahr`** an jedem Pipeline-Skript. Der **Standardwert 2026 steht an genau einer Stelle** und ist nicht über die Skripte verstreut. Pipeline und Tests nutzen denselben Lader, z. B. `ostbevern.konfiguration.lade_jahrgang(jahr)`.

### Pipeline-Aufbau
- **D-10:** Die Pipeline besteht aus **nummerierten Skripten** nach Spez. 5.2 (`pipeline/01_seiten_klassifizieren.py` … `08_quellenbelege.py`, `alle.py`). Es sind dünne typer-Einstiegspunkte, die eigentliche Logik liegt im Paket `pipeline/ostbevern/`. In Phase 1 gibt es nur die Skripte, die das Gerüst braucht. Leere Platzhalter für spätere Schritte sind Ermessenssache.
- **D-11:** Das PDF wird nach **`raw_data/haushalt-2026.pdf` umbenannt**, und die Kopie in `discussion/` wird gelöscht. Es bleibt im normalen Git, ohne LFS. Den Pfad liest die Pipeline nur aus der Jahrgangsdatei.
- **D-12:** `uv run pytest` prüft in Phase 1 mit einem **Rauchtest**:
  - Die Jahrgangsdatei lädt und ist vollständig (Pflichtschlüssel vorhanden).
  - Die Sollwertdatei lädt.
  - Das PDF existiert und hat 400 Seiten (der erwartete Wert steht in der Jahrgangsdatei).
- **D-13:** Python **3.12**: `.python-version` = 3.12, `requires-python = ">=3.12"`.

### CI & Tooling
- **D-14:** **ruff** prüft Lint und Format (`ruff check`, `ruff format --check`) und ist Dev-Abhängigkeit im uv-Projekt. mypy/pyright kommen nicht dazu.
- **D-15:** Es gibt **eine Workflow-Datei `.github/workflows/ci.yml` mit zwei parallelen Jobs**. Sie läuft bei jedem Push und PR, ohne Pfadfilter:
  - `pipeline`: uv einrichten, `uv sync`, `ruff check`, `ruff format --check`, `pytest`
  - `app`: Node 22, `npm ci`, `vue-tsc`, ESLint, Prettier-Check, `npm run build`

  Der Deploy-Workflow kommt erst in Phase 7.
- **D-16:** **Node 22 LTS** (`.nvmrc` und `engines`) mit **npm** und **Prettier**, eingebunden über `eslint-config-prettier`. `npm run format:check` läuft in der CI.
- **D-17:** Befehle und Konventionen stehen in der vorhandenen **`.claude/CLAUDE.md`**, in deren Abschnitten „Technology Stack“ und „Conventions“. Eine Root-`CLAUDE.md` wird nicht angelegt, das ist eine bewusste Abweichung von Spez. 7. Die GSD-verwalteten Abschnitte, etwa „Developer Profile“, bleiben unangetastet. Diese Konventionen kommen hinein (Erfolgskriterium 5):
  - deutsche Bezeichner ohne Umlaute
  - Beträge als int-Euro
  - nur 1-basierte PDF-Seiten
  - keine Jahrgangswerte im Code
  - Du-Anrede
  - Zahlen in Texten aus Daten
- **D-18:** **Es gibt noch kein GitHub-Remote.** Phase 1 schreibt `ci.yml` und prüft alle CI-Befehle **lokal** mit denselben Befehlen. Das Repo legt der Nutzer selbst an und pusht. Ob die CI auf GitHub grün läuft, zeigt sich beim ersten Push. Der Executor legt kein Repo an und pusht nicht.

### Claude's Discretion
- `.gitignore`-Inhalt: `node_modules`, `.venv`, `dist`, `__pycache__`, `.DS_Store` usw. Generierte Daten unter `daten/` bleiben laut Spez. 7 eingecheckt. Ob `daten/zwischen/` eingecheckt wird, entscheidet der Planner. Empfehlung: ja, wegen der Diff-Prüfung in Phase 4.
- Leere Verzeichnisse (`daten/*`) per `.gitkeep` oder README.
- Umfang des App-Gerüsts: Layout-Shell (Navigation, Fußzeilen-Platzhalter) und welche Routen schon als leere Seiten existieren. Nötig sind mindestens eine Startseite und eine Demo-Nutzung der Basiskomponenten, damit Build und Typprüfung sie wirklich abdecken.
- Konkrete Farbwerte der Ostbevern-Palette (kontrastgeprüft).
- ESLint-Konfiguration (Flat Config, `@vue/eslint-config-typescript`) und ruff-Regelsatz.
- Interne Modulaufteilung von `ostbevern/` über `konfiguration.py` hinaus.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` §2: PDF-Aufbau, Seitenbereiche, Spaltenköpfe (Quelle für den Inhalt von `2026.toml`)
- `discussion/SPEZIFIKATION.md` §5.1–5.2: Pipeline-Werkzeuge und Skript-Reihenfolge (`01_…` bis `alle.py`)
- `discussion/SPEZIFIKATION.md` §6.1: App-Technik und Liste der Münster-Komponenten
- `discussion/SPEZIFIKATION.md` §7: Repository-Struktur und Konventionen (Abweichung: CLAUDE.md nach D-17, PDF-Name nach D-11)
- `discussion/SPEZIFIKATION.md` §8: Qualität und Tests
- `discussion/SPEZIFIKATION.md` Anhang B: Sollwerte (Struktur für `2026_sollwerte.toml`)

### Projektplanung
- `.planning/PROJECT.md`: Constraints, Key Decisions, Konventionen
- `.planning/REQUIREMENTS.md`: SETUP-01 bis SETUP-05, QUAL-01
- `.planning/ROADMAP.md`: Phase 1, Erfolgskriterien 1–5
- `.claude/CLAUDE.md`: Zieldatei für Befehle und Konventionen (D-17)

### Externe Vorlage
- https://github.com/codeformuenster/haushalt-muenster-2026: Vorlage für Komponentennamen und Props (D-01, D-02). Nur lesen, nicht kopieren.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Im Repo gibt es noch keinen Code. Bisher liegen dort nur `.planning/`, `discussion/` und `raw_data/`.
- Die Münster-App (extern) dient als Vorlage für die Basiskomponenten, siehe D-01 und D-02.

### Established Patterns
- Noch keine. Diese Phase legt die Muster fest: Konventionen in `.claude/CLAUDE.md`, Jahrgangskonfiguration über TOML und `--jahr`.

### Integration Points
- `raw_data/haushalt-2026.pdf`: wird in Phase 2 von `pipeline/ostbevern/` gelesen
- `pipeline/jahrgaenge/2026.toml` und `2026_sollwerte.toml`: werden ab Phase 2 von allen Schritten und Tests gelesen
- `app/src/data/`: ab Phase 4 Ziel der generierten JSON-Dateien. Bis dahin reichen Platzhalter oder Demo-Daten.

</code_context>

<specifics>
## Specific Ideas

- Der Erwartungswert „400 Seiten“ für den PDF-Rauchtest steht in der Jahrgangsdatei, nicht im Test.
- Der Hinweis auf Münster Money gilt ausdrücklich als Dank bzw. Inspirationsnachweis, nicht als Lizenzpflicht, denn es wird kein Code kopiert.

</specifics>

<deferred>
## Deferred Ideas

None. Die Diskussion blieb im Rahmen der Phase.

</deferred>

---

*Phase: 01-setup*
*Context gathered: 2026-10-01*
