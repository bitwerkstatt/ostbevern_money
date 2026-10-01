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

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
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
