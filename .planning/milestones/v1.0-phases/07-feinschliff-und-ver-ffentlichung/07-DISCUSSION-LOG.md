# Phase 7: Feinschliff und Veröffentlichung - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-06
**Phase:** 07-feinschliff-und-veroeffentlichung
**Areas discussed:** Quellenbelege, Veröffentlichung, Prüfungen (Lighthouse/Playwright), Text- und Aufräumdurchgang

---

## Quellenbelege

| Option | Description | Selected |
|--------|-------------|----------|
| Kennzahlen + alle Tabellenzeilen mit pdf_seite | Ein Mechanismus für jeden Wert mit Seitenbezug | ✓ |
| Nur prominente Werte | Wie Münster, kleinere quellen.json | |
| Du entscheidest | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Ganze Seite, Zeile markiert und hineingescrollt | Eine WebP je Seite, bbox als Overlay | ✓ |
| Nur Ausschnitt um die Zeile | Viele Einzelbilder, weniger Kontext | |
| Seite + Link aufs Original-PDF | Zusätzlich #page=X | |

| Option | Description | Selected |
|--------|-------------|----------|
| Seite ohne Markierung + Hinweis | Pipeline-Bericht listet Werte ohne bbox | ✓ |
| Fehler in der Pipeline | Jeder Wert braucht ein Rechteck | |
| Kein „Quelle anzeigen“ | Nur Seitenverweis als Text | |

| Option | Description | Selected |
|--------|-------------|----------|
| wa-drawer rechts, mobil vollbreit | Fokusfalle, Esc, Fokusrückgabe, kein URL-Zustand | ✓ |
| Drawer + URL-Zustand | ?quelle=… verlinkbar | |
| Du entscheidest | | |

---

## Veröffentlichung

| Option | Description | Selected |
|--------|-------------|----------|
| Persönlicher Account, Repo „ostbevern-money“ | <account>.github.io/ostbevern-money | ✓ |
| Organisation | <org>.github.io/ostbevern-money | |
| Eigene Domain zusätzlich | CNAME | |

**Account:** bitwerkstatt (Freitext)

| Option | Description | Selected |
|--------|-------------|----------|
| Offizielle Gemeinde-Website | Keine eigene Kopie | ✓ |
| Selbst gehostet auf Pages | 9 MB PDF ausliefern | |
| Beides | | |

**PDF-URL (Freitext):** https://www.ostbevern.de/_Resources/Persistent/3/2/6/0/3260f0ed6ed16745ad93c953c061f765866667a6/Haushalt%202026%20komplett.pdf

**Kontakt (Freitext):** mail@thomas-manthey.de

| Option | Description | Selected |
|--------|-------------|----------|
| Seite „Über dieses Projekt“ mit Impressum + Datenschutzsatz | Texte per Checkpoint | ✓ |
| Nur Fußzeile wie heute | | |
| Kläre ich selbst später | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Push auf main, nur wenn CI grün | + workflow_dispatch | ✓ |
| Nur manuell | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Plan legt Repo per gh an, nach Freigabe | | |
| Ich lege es selbst an | Plan liefert Workflow + Anleitung | ✓ |

---

## Prüfungen (Lighthouse/Playwright)

| Option | Description | Selected |
|--------|-------------|----------|
| Playwright in der CI vor dem Deployment | Nur Chromium, gegen vite preview | ✓ |
| Nur lokal | | |

| Option | Description | Selected |
|--------|-------------|----------|
| axe-core im Playwright-Test + einmaliger Lighthouse-Lauf | | ✓ |
| Lighthouse CI in der CI | | |
| Nur einmaliger Lighthouse-Lauf | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Alle Routen + ein Produkt + mobil 360 px | | |
| Alle Routen, nur Desktop | Minimal nach QUAL-02 | ✓ |
| Alle 63 Produktseiten mit | | |

| Option | Description | Selected |
|--------|-------------|----------|
| Checkpoint im Plan vor der Installation | | |
| Diese Liste ist hiermit freigegeben | @playwright/test, @axe-core/playwright, pypdfium2, Pillow | ✓ |

---

## Text- und Aufräumdurchgang

| Option | Description | Selected |
|--------|-------------|----------|
| Automatischer Test + Checkpoint zur Abnahme | | ✓ |
| Nur automatischer Test | | |
| Nur manueller Durchgang | | |

**Restpunkte (Mehrfachauswahl):** Token-Hygiene Phase 5 ✓, Kosmetik Phase 6 ✓, DOM-Test MenueGruppe ✓, Code-Review-Warnungen Phase 2/4 ✓

| Option | Description | Selected |
|--------|-------------|----------|
| Test: jede ChartCard hat eine DatenTabelle | Inventar-Test | ✓ |
| Nur Audit und Lücken schließen | | |

---

## Claude's Discretion

- bbox-Suche und Schema von quellen.json, Zuordnung der Quell-Schlüssel
- Smoke-Test als eigener Job oder Schritt
- Heuristik der Du-Anrede-Prüfung
- Plan-/Wellenreihenfolge

## Deferred Ideas

- Verlinkbare Quellenbelege (URL-Zustand)
- Smoke-Test mobil und für alle Produktseiten
- Lighthouse CI als dauerhaftes Gate
- Eigene Domain
- /gsd-secure-phase 04 steht aus
