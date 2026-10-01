# Ostbevern Money

Ostbevern Money erklärt dir den Haushalt 2026 der Gemeinde Ostbevern. Die App beantwortet zwei Leitfragen: **Wo kommt das Geld der Gemeinde her?** und **Wofür wird es ausgegeben?** Jede Zahl, die du hier siehst, hat eine Python-Pipeline aus dem veröffentlichten Haushalts-PDF extrahiert und automatisch gegen die Planwerte geprüft. Dies ist ein **inoffizielles Projekt** und steht in keiner Verbindung zur Gemeindeverwaltung.

## Stand

Phase 1: Gerüst für Pipeline, App und CI.

## Aufbau

- `raw_data/` — das Quell-PDF des Haushalts
- `pipeline/` — die Python-Pipeline, die das PDF ausliest und prüft
- `daten/` — von der Pipeline erzeugte und geprüfte Daten
- `app/` — die Vue-3-Webanwendung
- `discussion/SPEZIFIKATION.md` — die fachliche Spezifikation

## Schnellstart

```bash
uv sync --directory pipeline
uv run --directory pipeline pytest
npm --prefix app ci
npm --prefix app run dev
npm --prefix app run build
```

Alle Befehle und Konventionen stehen in [`.claude/CLAUDE.md`](.claude/CLAUDE.md).

## Lizenz

MIT, siehe [`LICENSE`](LICENSE).

## Dank

Inspiriert von [Münster Money (Code for Münster)](https://github.com/codeformuenster/haushalt-muenster-2026). Es wurde kein Code übernommen — die Komponentennamen folgen nur der Vorlage.

Die selbst gehosteten Icons stammen von Font Awesome Free (CC BY 4.0).
