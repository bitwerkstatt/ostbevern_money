<!-- GSD:project-start source:PROJECT.md -->

## Project

**Ostbevern Money**

Eine statische Webanwendung, die den Bürgerinnen und Bürgern von Ostbevern den Haushalt 2026 der Gemeinde erklärt. Sie beantwortet zwei Leitfragen: **Wo kommt das Geld der Gemeinde her?** und **Wofür wird es ausgegeben?**. Ergänzend zeigt sie die Entwicklung 2024–2029, Investitionen und Schulden, den Gestaltungsspielraum des Rats und den Stellenplan. Die Daten stammen aus einer Python-Pipeline, die das 400-seitige ProFIS+-PDF ausliest und gegen die Planwerte prüft. Vorbild ist „Münster Money“ (Code for Münster, Münsterhack '26).

Die vollständige fachliche Spezifikation steht in `discussion/SPEZIFIKATION.md`. Sie ist die maßgebliche Detailquelle für Datenmodell, Prüfregeln, Seiteninhalte und Sollwerte (Anhang B).

**Core Value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen gegen den Gesamtplan und die Satzung belegt. Die beiden Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.

### Constraints

- **Tech stack Pipeline**: Python ≥ 3.12, uv, pdfplumber, polars, typer, pytest. Das entspricht dem Münster-Stack und erleichtert die Übernahme.
- **Tech stack App**: Vue 3, TypeScript, Vite, Web Awesome, ECharts (`vue-echarts`), Hash-Router. So lassen sich die Münster-Komponenten wiederverwenden.
- **Hosting**: GitHub Pages unter eigenem GitHub-Account, Deployment über GitHub Actions. Es gibt kein Backend.
- **Genauigkeit**: Abweichungen über 1 € gegenüber den Planwerten gelten als Fehler, außer sie sind in `befunde.md` dokumentiert. Bürgerinformation muss stimmen.
- **Datenschutz**: Mitarbeitendennamen werden extrahiert, aber nicht ausgeliefert.
- **Sprache**: Die App ist deutsch und durchgehend in der Du-Anrede.
- **Pro-Kopf-Werte**: Grundlage sind 11.741 Einwohner (IT.NRW, 30.06.2024, Vorbericht S. 24/25). Der Wert ist in `meta.json` konfigurierbar.
- **Barrierefreiheit**: Lighthouse a11y ≥ 95, Fokussteuerung, Kontraste, `prefers-reduced-motion`, responsiv ab 360 px.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

**Pipeline** (`pipeline/`): Python 3.12 (uv-verwaltet über `pipeline/.python-version`), uv 0.9.x, pdfplumber, polars, typer, pytest, ruff (genaue Versionen in `pipeline/uv.lock`).

**App** (`app/`): Vue 3, vue-router 5 mit Hash-History, Vite, TypeScript (Scaffold-Pin), Web Awesome 3 (Komponenten werden einzeln in `app/src/main.ts` importiert, Icons selbst gehostet unter `app/public/icons`, Goldakzent über `wa-brand-yellow`), ECharts 6 über vue-echarts 8 (nur die in `app/src/charts/echartsTheme.ts` registrierten Module), ESLint-Flat-Config plus Prettier, Node 22 (`app/.nvmrc`).

**CI**: `.github/workflows/ci.yml` mit den Jobs `pipeline` und `app`.

### Befehle

Pipeline (vom Repo-Root aus):
- `uv sync --directory pipeline`
- `uv run --directory pipeline pytest`
- `uv run --directory pipeline ruff check .`
- `uv run --directory pipeline ruff format .`
- `uv run --directory pipeline python alle.py --jahr 2026` (ohne `--jahr` gilt `STANDARD_JAHR`)

Hinweis: Ein bloßes `uv run pipeline/SKRIPT.py` vom Repo-Root nutzt **nicht** die Pipeline-Umgebung — deshalb immer `--directory pipeline` angeben (Abweichung von Spez. 5.2).

App (vom Repo-Root aus):
- `npm --prefix app ci`
- `npm --prefix app run dev`
- `npm --prefix app run build`
- `npm --prefix app run type-check`
- `npm --prefix app run lint` (und `lint:fix`)
- `npm --prefix app run format` und `format:check`
- `npm --prefix app run test`

CI lokal nachstellen (identisch zu `.github/workflows/ci.yml`):
```
(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)
(cd app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run test && npm run build)
```
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

- **Deutsche Bezeichner ohne Umlaute** — in Code und Daten, z. B. `ertraege`, `zuschussbedarf`, `lade_jahrgang`.
- **Beträge als int-Euro** — Formatierung ausschließlich in der App über `app/src/charts/format.ts`.
- **Nur 1-basierte PDF-Seiten** — `pdf_seite`, niemals gedruckte Seitenzahlen.
- **Keine Jahrgangswerte im Code** — Haushaltsjahr, PDF-Pfad, Spaltenköpfe, Seitenbereiche, Kopfzeilen-Muster und erwartete Anzahlen stehen in `pipeline/jahrgaenge/{jahr}.toml`, Sollwerte in `{jahr}_sollwerte.toml`. Gelesen wird ausschließlich über `ostbevern.konfiguration.lade_jahrgang` bzw. `lade_sollwerte`. Der Standardjahrgang steht an genau einer Stelle, `STANDARD_JAHR`. Jedes Pipeline-Skript nimmt `--jahr` entgegen. Die App bezieht den Jahrgang aus `app/src/data/`.
- **Du-Anrede** — durchgehend in allen App-Texten.
- **Zahlen in Texten aus Daten** — niemals von Hand eingetippt; jeder erklärende Text mit einer Zahl verweist auf eine PDF-Seite.

Konventionen aus dieser Phase:
- Pipeline-Skripte sind dünne typer-Einstiegspunkte, die eigentliche Logik liegt in `pipeline/ostbevern/`.
- Fachliche Regeln (Zeilenformeln, Minderaufwand-Zeilen, Ausschluss TP 27/28) bleiben im Code.
- Generierte Daten unter `daten/` werden eingecheckt.
- Die Basiskomponenten behalten die Münster-Namen und -Props (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `format.ts`, `echartsTheme.ts`, `bildschirm.ts`).
- Farben ausschließlich über `--wa-*`-Tokens, Chartfarben ausschließlich aus `echartsTheme.ts`.
- Projekteigene CSS-Klassen tragen das Präfix `om-`.
- Beispielwerte erscheinen nur hinter dem `ChartCard`-Flag `beispieldaten`.
- Keine Drittanbieter-Requests zur Laufzeit.
- Beim Commit werden nur die explizit benannten Pfade gestaged.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Datenfluss: `raw_data/haushalt-2026.pdf` → `pipeline/` (Bibliothek `ostbevern/`, Konfiguration `jahrgaenge/`, Einstieg `alle.py`, nummerierte Schritte ab Phase 2) → `daten/{zwischen,aufbereitet,manuell,pruefberichte}` → `app/src/data/` JSON (ab Phase 4) → Vue-App (`src/pages`, `src/components`, `src/charts`, `src/lib`, `src/data`) → GitHub Pages (Phase 7). Die CI prüft beide Projektteile bei jedem Push.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
