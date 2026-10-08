# Requirements: Ostbevern Money

**Defined:** 2026-10-07
**Core Value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen gegen den Gesamtplan und die Satzung belegt. Die beiden Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.

## v1.0.1 Requirements

Meilenstein „Restpunkte“: offene Qualitätspunkte aus v1.0 abschließen, keine neuen Funktionen. Quellen der Befunde: `.planning/milestones/v1.0-phases/{01,05,06}-*/…-REVIEW.md` und `…-REVIEW-DISPOSITION.md`.

Querschnittsbedingung für alle Anforderungen: `alle.py --jahr 2026` erzeugt `daten/` und `app/src/data/` weiterhin byte-identisch, außer ein Befund ändert bewusst eine Ausgabe (dann im Commit begründet). Prüfregeln 1–10 bleiben grün, 1-€-Toleranz unverändert.

### Triage

- [x] **TRI-01**: Alle 5 offenen Befunde in `01-REVIEW-DISPOSITION.md` stehen auf fixed, skipped oder deferred, jeweils mit Begründung bzw. Commit
- [x] **TRI-02**: Alle 13 offenen Befunde in `05-REVIEW-DISPOSITION.md` haben eine Disposition. Nebenbei schon behobene Befunde (z. B. Platzhalter-Kontaktdaten) sind mit Beleg als fixed markiert
- [x] **TRI-03**: Alle 10 offenen Befunde in `06-REVIEW-DISPOSITION.md` haben eine Disposition. Die Rücklagen-Fußnote (WR-01) ist mit der Begründung aus UAT 06 erfasst
- [x] **TRI-04**: Reine Hygiene-Befunde (Duplikate, toter Code, Hex-Fallbacks, Kopplung, Test-Nits) werden behoben, wenn das wenig kostet, sonst begründet auf deferred gesetzt

### Zahlen und Texte

- [x] **TXT-01**: Die Lesehilfe sagt nur dann „gleichen sich genau aus“, wenn Erträge und Aufwendungen tatsächlich ausgeglichen sind. Schließt nur der Minderaufwand die Lücke, sagt sie das
- [x] **TXT-02**: Der Minderaufwand-Hinweis zeigt nie einen negativen Betrag
- [x] **TXT-03**: Die Ziffernregel in `pruefe_text` erkennt auch handgetippte Zahlen zwischen 1900 und 2099. Jahreszahlen sind nur über den Platzhalter mit Kürzel `jahr` erlaubt
- [x] **TXT-04**: Die Regel für „rd.“ und den Betrag mit geschütztem Leerzeichen (`EuroBetrag`) ist überall gleich umgesetzt, ohne parallele Altkopien
- [x] **TXT-05**: Eine abgeleitete Summe auf den Kontextseiten trägt die Kennzeichnung „berechnet“, und die Quellzeile einer Kachel nennt nur deren eigene Seiten
- [x] **TXT-06**: Die Ebenen-Tabelle (`EbenenTabelle`) meldet eine fehlende Einwohnerzahl, statt die Pro-Kopf-Spalte stillschweigend wegzulassen

### Barrierefreiheit

- [x] **A11Y-01**: Der scrollbare Container der Daten-Tabelle (`DatenTabelle`) hat immer Rolle und Namen, auch ohne `beschriftung`
- [x] **A11Y-02**: Das mobile Menü schließt sich auch, wenn du auf den Link der aktuellen Seite tippst
- [x] **A11Y-03**: Datentabellen werden von Screenreadern nicht doppelt beschriftet

### Sicherheit

- [ ] **SEC-01**: Für Phase 4 liegt `04-SECURITY.md` mit `threats_open: 0` vor, nach dem Muster der anderen Phasen

### Audit

- [ ] **AUD-01**: Das Milestone-Audit für v1.0 ist durchgeführt. Seine Lücken sind entweder in diesem Meilenstein geschlossen oder begründet zurückgestellt
- [ ] **AUD-02**: Die Verifikationen der Phasen 1–7 sind gegen den aktuellen Stand erneuert, keine steht mehr auf „stale“
- [ ] **AUD-03**: Die Liste „Blockers/Concerns“ in STATE.md stimmt mit der Wirklichkeit überein. Die veralteten Einträge zu Phase 2 und 4 sind entfernt

## Future Requirements

Bleiben im Backlog (siehe `milestones/v1.0-REQUIREMENTS.md`, Abschnitt v2):

- **SPIEL-01…05**: Planspiel, „Was kostet …?“, Schätzduell, Teaser auf der Startseite, `planspiel.json`
- **ERW-01**: Eigene Seite für BBO und TEO AöR
- **ERW-02**: Kennzeichnung „Ortsteil Brock“
- **ERW-03**: Haushalt 2027 mit derselben Pipeline

## Out of Scope

| Feature | Reason |
|---------|--------|
| Deploy-/Gerätecheck aus Phase 7 (Human-Items 07-VERIFICATION) | Macht der Nutzer selbst; Sandbox-Firewall blockiert github.io und Actions-API |
| Neue Funktionen jeder Art | Reiner Nacharbeits-Meilenstein |
| Kämmerei informieren | Organisatorische Entscheidung, keine Code-Arbeit |
| CR-01 Phase 7 (Unterschriften auf s009.webp) | Bereits als deferred entschieden (Nutzerentscheidung 2026-10-07) |
| Backend, Nutzerkonten, CSV im Browser, Personennamen | Unverändert aus v1.0 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TXT-01 | Phase 8 | Complete |
| TXT-02 | Phase 8 | Complete |
| TXT-03 | Phase 8 | Complete |
| TXT-04 | Phase 8 | Complete |
| TXT-05 | Phase 8 | Complete |
| TXT-06 | Phase 8 | Complete |
| A11Y-01 | Phase 8 | Complete |
| A11Y-02 | Phase 8 | Complete |
| A11Y-03 | Phase 8 | Complete |
| TRI-01 | Phase 8 | Complete |
| TRI-02 | Phase 8 | Complete |
| TRI-03 | Phase 8 | Complete |
| TRI-04 | Phase 8 | Complete |
| SEC-01 | Phase 9 | Pending |
| AUD-01 | Phase 9 | Pending |
| AUD-02 | Phase 9 | Pending |
| AUD-03 | Phase 9 | Pending |

**Coverage:**
- v1.0.1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0 ✓

---
*Requirements defined: 2026-10-07*
*Last updated: 2026-10-07 after roadmap revision (zwei Phasen, 8–9)*
