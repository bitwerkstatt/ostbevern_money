# Roadmap: Ostbevern Money

## Milestones

- ✅ **v1.0 MVP** — Phases 1-7 (shipped 2026-10-07) — [Archiv](milestones/v1.0-ROADMAP.md)
- 🚧 **v1.0.1 Restpunkte** — Phases 8-9 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-7) — SHIPPED 2026-10-07</summary>

- [x] Phase 1: Setup (5/5 plans) — completed 2026-10-01
- [x] Phase 2: Kernzahlen (5/5 plans) — completed 2026-10-01
- [x] Phase 3: Details (5/5 plans) — completed 2026-10-02
- [x] Phase 4: Manuelle Daten und App-Daten (6/6 plans) — completed 2026-10-04
- [x] Phase 5: Leitfragen-Seiten (16/16 plans) — completed 2026-10-05
- [x] Phase 6: Kontext-Seiten (17/17 plans) — completed 2026-10-06
- [x] Phase 7: Feinschliff und Veröffentlichung (14/14 plans) — completed 2026-10-07

</details>

### 🚧 v1.0.1 Restpunkte (In Progress)

**Milestone Goal:** Die offenen Qualitätspunkte aus v1.0 abschließen, ohne neue Funktionen. Zahlen, Texte und Barrierefreiheit stimmen auch in Grenzfällen, jeder Review-Befund hat eine Disposition, Phase 4 ist sicherheitsgeprüft, und v1.0 ist auditiert und gegen den aktuellen Stand verifiziert.

**Querschnittsbedingung (gilt für jede Phase dieses Meilensteins):**
- `uv run --directory pipeline python alle.py --jahr 2026` erzeugt `daten/` und `app/src/data/` byte-identisch. Ändert ein Befund bewusst eine Ausgabe, steht die Begründung im Commit.
- Prüfregeln 1–10 bleiben grün, die 1-€-Toleranz bleibt unverändert.
- App-Prüfungen (type-check, lint, format:check, test, build, Playwright) laufen in einer Scratch-Kopie von `app/`, weil `app/node_modules` im gemounteten Repo macOS-Binaries enthält.
- Ein Commit, der einen Review-Befund behebt, nennt dessen ID mit Phasenpräfix (z. B. `05/IN-06`). So kann die Triage am Ende von Phase 8 ihn als Beleg zitieren.

- [ ] **Phase 8: Fixes und Triage** - Zahlen, Texte und Barrierefreiheit stimmen in Grenzfällen, Hygiene-Befunde sind erledigt oder begründet zurückgestellt, die Ledger 01, 05 und 06 stehen auf `open: 0`
- [ ] **Phase 9: Sicherheit und Audit** - `04-SECURITY.md` mit `threats_open: 0`, Milestone-Audit für v1.0, erneuerte Verifikationen der Phasen 1–7, bereinigte Blocker-Liste in STATE.md

## Phase Details

### Phase 8: Fixes und Triage

**Goal**: Alles, was die App in Worten über Zahlen sagt, stimmt auch in Grenzfällen, und Datentabellen und das mobile Menü funktionieren für Screenreader und Touch ohne Lücken. Jeder der 28 offenen Review-Befunde aus den Phasen 1, 5 und 6 ist behoben, übersprungen oder begründet zurückgestellt, und das ist im jeweiligen Ledger belegt. Reihenfolge in der Phase: zuerst die Fixes an Zahlen und Texten, dann Barrierefreiheit und Hygiene, zum Schluss die Ledger auf `open: 0`.
**Depends on**: Phase 7 (v1.0 abgeschlossen)
**Requirements**: TXT-01, TXT-02, TXT-03, TXT-04, TXT-05, TXT-06, A11Y-01, A11Y-02, A11Y-03, TRI-01, TRI-02, TRI-03, TRI-04
**Success Criteria** (what must be TRUE):
  1. Sätze über Zahlen stimmen in Grenzfällen. Die Lesehilfe auf `/geldfluss` sagt „gleichen sich … genau aus“ nur für ein Jahr, in dem Erträge und Aufwendungen tatsächlich gleich sind; schließt erst der globale Minderaufwand die Lücke, sagt der Satz genau das. Der Minderaufwand-Hinweis auf `/ausgaben` zeigt in keinem Jahr einen negativen Betrag. Die Regel „rd.“ plus Betrag mit geschütztem Leerzeichen ist an genau einer Stelle umgesetzt (`EuroBetrag` bzw. eine gemeinsame Hilfsfunktion), die fünf Altkopien sind entfernt. vitest deckt die Grenzfälle ab.
  2. Jahreszahlen, abgeleitete und fehlende Werte sind erkennbar. `pruefe_text` lehnt eine handgetippte Zahl zwischen 1900 und 2099 mit klarer Fehlermeldung ab (pytest-Fall); Jahreszahlen sind nur über einen `jahr.…`-Platzhalter mit Kürzel `jahr` zulässig, und auffällige Bestandstexte sind begründet auf Platzhalter umgestellt. Jede abgeleitete Summe auf den Kontextseiten (z. B. „Zusammen rd. …“ auf `/rat-entscheidet`) trägt das Etikett „berechnet“, die Quellzeile einer Kachel auf `/stellenplan` nennt nur deren eigene PDF-Seiten, und `EbenenTabelle` auf `/ausgaben` meldet eine fehlende Einwohnerzahl, statt die Pro-Kopf-Spalte wegzulassen.
  3. Der scrollbare Container von `DatenTabelle` hat immer Rolle und zugänglichen Namen, auch ohne `beschriftung`, und keine Datentabelle trägt ihren Namen doppelt (Region-Label und `<caption>`). Tippst du bei 360 px im geöffneten Menü auf den Link der Seite, auf der du gerade bist, schließt sich das Menü. vitest, der axe-Smoke-Test und ein Playwright-Test bestätigen das.
  4. `01-REVIEW-DISPOSITION.md`, `05-REVIEW-DISPOSITION.md` und `06-REVIEW-DISPOSITION.md` unter `.planning/milestones/v1.0-phases/` stehen auf `open: 0`, jede Zeile nennt Commit oder Begründung. Nebenbei behobene Befunde (z. B. 05/IN-09, Platzhalter-Kontaktdaten, erledigt mit D-17 in Phase 7) sind mit Beleg auf fixed gesetzt, 06/WR-01 (Rücklagen-Fußnote) ist mit der Begründung aus UAT 06 erfasst. Jeder reine Hygiene-Befund (Duplikate, toter Code, Hex-Fallbacks, Kopplung, Test-Nits, Doku-Drift) ist behoben, wenn das wenig kostet, sonst auf deferred mit Begründung in der Source-Spalte.
  5. Die Querschnittsbedingung hält: `alle.py --jahr 2026` ist byte-identisch oder begründet geändert, Prüfregeln 1–10 sind grün, die CI-Kette von Pipeline und App (Scratch-Kopie, inkl. axe-Smoke und 360-px-Prüfungen) ist grün.

**Plans**: 12 plans in 5 waves

Plans:
**Wave 1**
- [ ] 08-01-PLAN.md — Jahreszahlen nur als Platzhalter: pruefe_text, Titelprüfung, jahr.-Schlüssel, sieben Abschnitte, istJahrneutral (TXT-03; Welle 1)
- [ ] 08-02-PLAN.md — rd./rund-Regel in format.ts, Lesehilfe in vier Fällen, gemeinsame Minderaufwand-Regel (TXT-01, TXT-02, TXT-04; Welle 1)
- [ ] 08-03-PLAN.md — Stellenplan-Kacheln berechnet mit eigenen Seiten, einwohnerZahl() wirft laut (TXT-05, TXT-06; Welle 1)

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 08-04-PLAN.md — zwölf rd.-Altkopien durch EuroBetrag bzw. betragMitHinweis ersetzt (TXT-04; Welle 2)
- [ ] 08-05-PLAN.md — Zusammen-Zeile der Zuschüsse mit Kennzeichen, Prüfauftrag D-12, Filtersumme gekennzeichnet (TXT-05, TXT-04; Welle 2)

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 08-06-PLAN.md — DatenTabelle mit Rolle und einem Namen, Drawer schließt bei jedem Link, menueVersatz im Browser (A11Y-01..03; Welle 3)
- [ ] 08-07-PLAN.md — Wächter-Test der rd.-Regel, Token-Wächter-Grenzen, begründete Quelltext-Tests (TXT-04, TRI-04; Welle 3)
- [ ] 08-08-PLAN.md — Pipeline- und Doku-Hygiene: Formelfehler, Glossar-Invariante, pdf_relativ, Anzahlen, CI-Doku (TRI-04; Welle 3)
- [ ] 08-09-PLAN.md — Warn-Icon und verwaiste Beispieldaten, eine Flächenfarbe, alsRgb, Markup-Nits (TRI-04; Welle 3)
- [ ] 08-10-PLAN.md — gemeinsame Jahr-Helfer, postenEintrag, anzahlText, Vorzeichen-Kommentar (TRI-04; Welle 3)

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 08-11-PLAN.md — schlankes Modul hilfsfunktionen.ts, Maßnahmenfilter einmal je Seite (TRI-04; Welle 4)

**Wave 5** *(blocked on Wave 4 completion)*
- [ ] 08-12-PLAN.md — Ledger 01/05/06 auf open: 0 mit Belegen, Abschlusslauf der Querschnittsbedingung (TRI-01..04; Welle 5)

**Cross-cutting constraints:**
- Alle Zahlen bleiben gleich: volle vitest-Suite grün, alle.py byte-identisch

**UI hint**: yes

### Phase 9: Sicherheit und Audit

**Goal**: Phase 4 (manuelle Daten und App-Daten) ist wie alle anderen v1.0-Phasen nachweislich sicherheitsgeprüft, v1.0 ist nachträglich auditiert, die Verifikationen aller sieben v1.0-Phasen beschreiben den Endstand nach den Restpunkten, und STATE.md nennt nur noch echte offene Punkte. Reihenfolge in der Phase: zuerst die Sicherheitsprüfung von Phase 4 gegen den Code nach Phase 8, zuletzt Audit und Re-Verifikation gegen den Endstand.
**Depends on**: Phase 8
**Requirements**: SEC-01, AUD-01, AUD-02, AUD-03
**Success Criteria** (what must be TRUE):
  1. `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md` liegt vor, mit Frontmatter `status: verified`, `threats_open: 0` und `asvs_level: 1`, aufgebaut wie die SECURITY-Dateien der Phasen 1–3 und 5–7. Alle 21 Bedrohungen aus den Threat-Registern der Phase-4-Pläne (T-04-01 bis T-04-20 und T-04-SC) sind als mitigated mit Beleg im aktuellen Code oder als accepted mit Begründung geschlossen, die Namens-Tests für `app/src/data/*.json` und `daten/manuell/meta.json` laufen grün. Eine offene Bedrohung wird vor dem Audit mit Test behoben.
  2. `.planning/v1.0-MILESTONE-AUDIT.md` liegt vor und deckt Anforderungen, Phasen-Integration und End-to-End-Flüsse ab. Jede darin gemeldete Lücke ist in diesem Meilenstein geschlossen oder mit Begründung zurückgestellt (deferred bzw. v2-Backlog).
  3. Die `*-VERIFICATION.md` der Phasen 1–7 sind gegen den Endstand erneuert, keine Phase meldet mehr „stale“. Die Human-Items aus `07-VERIFICATION.md` (Deploy- und Gerätecheck) bleiben als Aufgabe des Nutzers ausgewiesen und gelten nicht als bestanden.
  4. „Blockers/Concerns“ in STATE.md stimmt mit der Wirklichkeit überein. Die veralteten Einträge zu `02-REVIEW.md` und `04-REVIEW-DISPOSITION.md` sind entfernt (beide Ledger stehen schon auf `open: 0`), ebenso die in diesem Meilenstein erledigten Punkte (Security Phase 4, Milestone-Audit, stale-Verifikationen). Nur zutreffende Hinweise bleiben, z. B. die Scratch-Kopie für App-Prüfungen.
  5. Ein Abschlusslauf bestätigt die Querschnittsbedingung auf dem Endstand: `alle.py --jahr 2026` ist byte-identisch, Prüfregeln 1–10 sind grün, die CI-Kette von Pipeline und App ist grün.

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 8 → 9

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Setup | v1.0 | 5/5 | Complete | 2026-10-01 |
| 2. Kernzahlen | v1.0 | 5/5 | Complete | 2026-10-01 |
| 3. Details | v1.0 | 5/5 | Complete | 2026-10-02 |
| 4. Manuelle Daten und App-Daten | v1.0 | 6/6 | Complete | 2026-10-04 |
| 5. Leitfragen-Seiten | v1.0 | 16/16 | Complete | 2026-10-05 |
| 6. Kontext-Seiten | v1.0 | 17/17 | Complete | 2026-10-06 |
| 7. Feinschliff und Veröffentlichung | v1.0 | 14/14 | Complete | 2026-10-07 |
| 8. Fixes und Triage | v1.0.1 | 0/12 | Planned | - |
| 9. Sicherheit und Audit | v1.0.1 | 0/TBD | Not started | - |
