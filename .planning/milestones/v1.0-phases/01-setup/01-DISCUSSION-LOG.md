# Phase 1: Setup - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-01
**Phase:** 01-setup
**Areas discussed:** Münster-Übernahme, Jahrgangskonfiguration, Pipeline-Aufbau, CI & Tooling

---

## Münster-Übernahme

| Option | Description | Selected |
|--------|-------------|----------|
| Kopieren und anpassen | Ausgewählte Dateien 1:1 kopieren, dann anpassen | |
| Repo klonen und entschlacken | Ganze Münster-App übernehmen, Unpassendes entfernen | |
| Nur als Vorlage, neu schreiben | Dateien dienen nur als Vorlage, der Code wird selbst geschrieben | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| Basis jetzt, Rest bei Bedarf | Basiskomponenten in P1, Sankey/Glossar/Akkordeon in P5, Quelle in P7 | ✓ |
| Alle aus der Liste jetzt | Alles sofort übernehmen | |

| Option | Description | Selected |
|--------|-------------|----------|
| Gleiche Namen/Props, eigener Code | Schnittstellen wie Münster | ✓ |
| Frei gestalten | Nur Ideengeber | |

| Option | Description | Selected |
|--------|-------------|----------|
| Eigene Ostbevern-Farben | Eigene Palette als WA- und ECharts-Theme | ✓ |
| Wie Münster | Farben/Typo übernehmen | |
| Neutral, später festlegen | WA-Standard bis Phase 5 | |

| Option | Description | Selected |
|--------|-------------|----------|
| MIT + Dank an CfM im README | MIT-Lizenz, Inspirationshinweis | ✓ |
| Andere Lizenz | EUPL/GPL/Apache | |
| Noch offen | Bis Phase 7 offen | |

**User's choice:** Neu schreiben mit gleichen Namen und Props. In Phase 1 nur die Basiskomponenten, dazu eigene Farben und MIT-Lizenz.

---

## Jahrgangskonfiguration

| Option | Description | Selected |
|--------|-------------|----------|
| TOML: pipeline/jahrgaenge/2026.toml | tomllib, Kommentare möglich | ✓ |
| YAML | PyYAML nötig, Typfallen | |
| JSON | Keine Kommentare | |

| Option | Description | Selected |
|--------|-------------|----------|
| Alles PDF-Spezifische | Jahr, Pfad, Spalten, Seitenbereiche, Kopfzeilen-Muster, Anzahlen | ✓ |
| Minimal (nur SETUP-05) | Jahr, Spalten, Seiten, Pfad | |
| Auch Sollwerte | Sollwerte mit in die Datei | |

| Option | Description | Selected |
|--------|-------------|----------|
| Eigene Datei je Jahrgang | 2026_sollwerte.toml | ✓ |
| Direkt in den Tests | Konstanten im Testcode | |

| Option | Description | Selected |
|--------|-------------|----------|
| --jahr mit Standard 2026 | Option je Skript, Standard an einer Stelle | ✓ |
| Umgebungsvariable | OSTBEVERN_JAHR | |

**User's choice:** TOML mit allem PDF-Spezifischen, Sollwerte in einer eigenen Datei, Auswahl per `--jahr`.

---

## Pipeline-Aufbau

| Option | Description | Selected |
|--------|-------------|----------|
| Nummerierte Skripte + Bibliothek | Wie Spez. 5.2, Logik in ostbevern/ | ✓ |
| Ein typer-CLI mit Unterbefehlen | `uv run ostbevern …` | |

| Option | Description | Selected |
|--------|-------------|----------|
| Umbenennen, Duplikat weg, normal in Git | raw_data/haushalt-2026.pdf | ✓ |
| Git LFS | Schlankes Repo, LFS in CI | |
| Name unverändert lassen | Leerzeichen-Name bleibt | |

| Option | Description | Selected |
|--------|-------------|----------|
| Rauchtest Konfig + PDF | Konfig lädt, PDF hat 400 Seiten | ✓ |
| Nur Platzhaltertest | Trivialer Test | |

| Option | Description | Selected |
|--------|-------------|----------|
| 3.12 | Spez.-Untergrenze | ✓ |
| 3.13 | Neuer | |

**User's choice:** Alle empfohlenen Optionen.

---

## CI & Tooling

| Option | Description | Selected |
|--------|-------------|----------|
| ruff (lint + format) | Gegenstück zu ESLint | ✓ |
| ruff + mypy/pyright | Strenger | |
| Nur pytest | Wie Roadmap | |

| Option | Description | Selected |
|--------|-------------|----------|
| Ein ci.yml, zwei Jobs | Pipeline- und App-Job parallel | ✓ |
| Getrennte Workflows mit Pfadfiltern | Nur bei Änderungen | |

| Option | Description | Selected |
|--------|-------------|----------|
| .claude/CLAUDE.md erweitern | Eine Quelle, GSD liest sie | ✓ |
| Neue Root-CLAUDE.md | Wie Spez. 7 | |

| Option | Description | Selected |
|--------|-------------|----------|
| Node 22 LTS, npm, Prettier | .nvmrc, format:check in CI | ✓ |
| Node 22, npm, ohne Prettier | Nur ESLint | |

| Option | Description | Selected |
|--------|-------------|----------|
| Workflow schreiben, Repo legst du an | CI lokal verifizieren, Push durch den Nutzer | ✓ |
| Repo in Phase 1 per gh anlegen | Executor legt Repo an | |

**User's choice:** Alle empfohlenen Optionen.

---

## Claude's Discretion

- .gitignore, .gitkeep, ob `daten/zwischen/` eingecheckt wird
- Umfang von App-Shell und Routen-Gerüst
- Konkrete Farbwerte, ESLint- und ruff-Regelsätze, Modulaufteilung von `ostbevern/`

## Deferred Ideas

Keine.
