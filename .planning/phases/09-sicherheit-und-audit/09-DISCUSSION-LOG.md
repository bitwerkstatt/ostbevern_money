# Phase 9: Sicherheit und Audit - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-08
**Phase:** 09-sicherheit-und-audit
**Areas discussed:** Security-Prüfung Phase 4, Umfang des Milestone-Audits, Tiefe der Re-Verifikation, Aufräumen der Planungsdokumente

---

## Security-Prüfung Phase 4

**Belege je Bedrohung**

| Option | Description | Selected |
|--------|-------------|----------|
| Code und Testlauf | Datei:Zeile plus Testname, der im Abschlusslauf grün ist | ✓ |
| Nur Fundstelle im Code | Aus Analyse, ohne Testlauf je Bedrohung | |
| Wie bei 01–07 | Gleiche Tiefe wie die vorhandenen SECURITY-Dateien | |

**Neue Bedrohungen aus Phase-8-Änderungen**

| Option | Description | Selected |
|--------|-------------|----------|
| Nur die 21 prüfen | Phase-8-Änderungen vermerken, keine neuen IDs | ✓ |
| Neue IDs ergänzen | T-04-21 … für Phase-8-Effekte | |

**Accepted-Bewertungen (T-04-11, T-04-20)**

| Option | Description | Selected |
|--------|-------------|----------|
| Prüfen und bestätigen | Begründung gegen aktuellen Code prüfen | ✓ |
| Zu mitigate hochstufen | Echte Gegenmaßnahme mit Test | |

**Offene Bedrohung**

| Option | Description | Selected |
|--------|-------------|----------|
| In Phase 9 beheben | Fix mit Test vor dem Audit, Commit nennt ID | ✓ |
| Mich vorher fragen | Fix-Pläne erst nach Freigabe | |

---

## Umfang des Milestone-Audits

**Audit-Umfang**

| Option | Description | Selected |
|--------|-------------|----------|
| v1.0, Endstand nach Phase 8 | Nur Phasen 1–7 und v1.0-Anforderungen | |
| v1.0 und v1.0.1 zusammen | Phase 8/9 und v1.0.1-Anforderungen mit | ✓ |

**Nyquist-Befunde (04 draft, 05 nicht konform)**

| Option | Description | Selected |
|--------|-------------|----------|
| Melden und zurückstellen | tech_debt, deferred | ✓ |
| In Phase 9 schließen | validate-phase für 04 und 05 | |
| Nur 04 schließen | 05 deferred | |

**Schwelle für Lückenschluss**

| Option | Description | Selected |
|--------|-------------|----------|
| Falsche Zahl oder A11y-Fehler | Kernaussage beheben, Doku/Prozess deferred | ✓ |
| Alles, was wenig kostet | Schwelle wie D-13 Phase 8 | |
| Nur melden, dann entscheide ich | Fix-Pläne nach Bericht | |

**Archivpfad**

| Option | Description | Selected |
|--------|-------------|----------|
| Archiv direkt lesen | milestones/v1.0-phases/ als Eingabe, nichts verschieben | ✓ |
| Du entscheidest | Planer wählt | |

**Dateiname (Folgefrage)**

| Option | Description | Selected |
|--------|-------------|----------|
| v1.0-MILESTONE-AUDIT.md | Name laut Roadmap, Kopf nennt v1.0.1-Abdeckung | ✓ |
| Zwei Dateien | Zusätzlich v1.0.1-MILESTONE-AUDIT.md | |

**Zeitpunkt (Folgefrage)**

| Option | Description | Selected |
|--------|-------------|----------|
| Audit ganz am Ende | Nach Security, Re-Verify, Aufräumen | ✓ |
| Audit vor der Re-Verifikation | Phase-9-Anforderungen „in Arbeit“ | |

---

## Tiefe der Re-Verifikation

**Tiefe**

| Option | Description | Selected |
|--------|-------------|----------|
| Volle Re-Verifikation | Goal-Backward je Phase, 7 Verifier-Läufe | ✓ |
| Delta-Check | Nur von Phase 8 berührte Must-haves | |
| Gemischt | Voll für 1/4/5/6, Delta für 2/3/7 | |

**Phase 7 (passed vs. human_needed)**

| Option | Description | Selected |
|--------|-------------|----------|
| status: human_needed | Human-Items bleiben offen | |
| passed mit Override | Nur sinnvoll bei bereits geprüftem Deploy | ✓ |

Folgefrage „Deploy und Gerätecheck schon erledigt?“: **Ja, beides erledigt** (Alternativen: „Nein, noch offen“, „Dann doch human_needed“).
**Notes:** Human-Items werden als vom Nutzer bestätigt (2026-10-08) gekennzeichnet, nicht als vom Verifier geprüft.

**Phase 8 Verifikation**

| Option | Description | Selected |
|--------|-------------|----------|
| Ja, falls Phase 9 Code ändert | Nur bei Code-Fix | ✓ |
| Immer erneuern | In jedem Fall | |
| Nein | Nur 1–7 | |

**Ablauf**

| Option | Description | Selected |
|--------|-------------|----------|
| Re-Verify → Audit → Fix → Nachlauf | Betroffene VERIFICATIONs und Audit-Status danach aktualisieren | ✓ |
| Du entscheidest | Planer schneidet die Wellen | |

---

## Aufräumen der Planungsdokumente

**Archivdokumente**

| Option | Description | Selected |
|--------|-------------|----------|
| Nachtrag, kein Umschreiben | Datierter Nachtrag in MILESTONES.md | ✓ |
| Nur STATE.md | Archive unberührt | |
| Archive korrigieren | Alte Stellen umformulieren | |

**Out-of-Scope-Zeile Deploy-/Gerätecheck**

| Option | Description | Selected |
|--------|-------------|----------|
| Stehen lassen, Status nachtragen | Vermerk „vom Nutzer erledigt, 2026-10-08“ | ✓ |
| Unverändert lassen | | |

**Abschluss v1.0.1**

| Option | Description | Selected |
|--------|-------------|----------|
| Nein, separat | /gsd-complete-milestone durch den Nutzer | ✓ |
| Ja, als letzter Schritt | | |

---

## Claude's Discretion

- Planzuschnitt und Wellen innerhalb der Reihenfolge Re-Verify → Audit → Fix → Nachlauf
- Security-Prüfung über secure-phase-Logik oder eigenen Plan (Format der SECURITY-Dateien bindend)
- Genaues Frontmatter von 04-SECURITY.md
- Wortlaut der Nachträge

## Deferred Ideas

- Nyquist-Validierung Phase 4 und 5
- Abschluss v1.0.1 durch den Nutzer nach Phase 9
