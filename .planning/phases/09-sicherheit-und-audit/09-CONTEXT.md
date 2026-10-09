# Phase 9: Sicherheit und Audit - Context

**Gathered:** 2026-10-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Nacharbeit ohne neue Funktionen. Vier Ergebnisse:

1. **SEC-01:** `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md` mit `status: verified`, `threats_open: 0`, `asvs_level: 1`. Aufbau wie die SECURITY-Dateien der Phasen 1–3 und 5–8. Alle 21 Bedrohungen (T-04-01 bis T-04-20 und T-04-SC) sind geschlossen, und zwar gegen den Code nach Phase 8 geprüft.
2. **AUD-02:** Die `*-VERIFICATION.md` der Phasen 1–7 sind gegen den Endstand erneuert, keine Phase meldet mehr „stale“.
3. **AUD-03:** „Blockers/Concerns“ in `STATE.md` nennt nur noch echte offene Punkte.
4. **AUD-01:** `.planning/v1.0-MILESTONE-AUDIT.md` deckt Anforderungen, Phasen-Integration und End-to-End-Flüsse ab. Jede gemeldete Lücke ist geschlossen oder begründet zurückgestellt.

Reihenfolge (Roadmap und D-12): Security Phase 4 → Re-Verifikation → Aufräumen → Audit → ggf. Fixes und Nachlauf → Abschlusslauf.

Querschnittsbedingung (gilt unverändert): `uv run --directory pipeline python alle.py --jahr 2026` erzeugt `daten/` und `app/src/data/` byte-identisch, Ausnahmen nur mit Begründung im Commit. Prüfregeln 1–10 bleiben grün, die 1-€-Toleranz bleibt unverändert. App-Prüfungen laufen in einer Scratch-Kopie von `app/`. Fix-Commits nennen die Befund- oder Bedrohungs-ID mit Phasenpräfix.

</domain>

<decisions>
## Implementation Decisions

### Security-Prüfung Phase 4 (SEC-01)
- **D-01:** **Jede Bedrohung wird mit Code und Testlauf belegt.** Der Eintrag im Register nennt die Fundstelle im aktuellen Code (`Datei:Zeile`) und mindestens einen Testnamen. Dieser Test muss in einem echten Lauf grün sein, eine Analyse allein reicht nicht. Die Belege aus den Phase-4-Plänen werden nicht ungeprüft übernommen. Das betrifft vor allem T-04-16 (Ziffernregel in `pruefe_text`, in Phase 8 verschärft, D-01 der Phase 8) und T-04-18 (`jahr`-Kürzel und `jahr.*`-Platzhalter, in Phase 8 erweitert, D-02 bis D-04 der Phase 8).
- **D-02:** **Nur die 21 Bedrohungen aus den Phase-4-Plänen, keine neuen IDs.** Hat Phase 8 den Code einer Bedrohung geändert, steht das als Vermerk mit Commit-Verweis bei der Bedrohung. Die Phase-8-Änderungen selbst deckt `.planning/phases/08-fixes-und-triage/08-SECURITY.md` ab (`threats_open: 0`). T-04-SC steht in allen sechs Plänen und wird **einmal** geführt.
- **D-03:** **Die Bewertungen `accept` werden geprüft und bestätigt, nicht hochgestuft.** T-04-11 (Stellenplan ohne Personennamen): Es wird geprüft, ob der Namens-Scan `stellenplan.csv` und `stellenplan.json` heute noch erfasst. T-04-20 (pytest startet `node` aus `app/node_modules`): Es wird geprüft, ob der Aufruf weiterhin eine feste Argumentliste ohne Shell nutzt, nur JSON über stdin bekommt und ohne Netz läuft. Beide kommen in den Abschnitt „Accepted Risks“.
- **D-04:** **Eine offene Bedrohung wird in Phase 9 mit Test behoben, und zwar vor dem Audit.** Der Commit nennt die ID, z. B. `04/T-04-07`. Danach wird die Bedrohung als mitigated mit diesem Commit eingetragen.
- **D-05:** Die Namens-Tests für `app/src/data/*.json` und `daten/manuell/meta.json` müssen im Lauf grün sein und dürfen nicht übersprungen werden (Roadmap-Kriterium 1). Kandidaten sind `test_keine_personennamen_in_app_daten` (`pipeline/tests/test_app_daten.py`), `test_keine_personennamen` (`pipeline/tests/test_produkte.py:198`) und `test_meta_json_gueltig` bzw. `test_meta_json_bricht_ab` (`pipeline/tests/test_manuell.py:471,517`). Brauchen sie das PDF unter `raw_data/`, muss es vorhanden sein. Ein Skip gilt nicht als Beleg.

### Milestone-Audit (AUD-01)
- **D-06:** **Gegenstand sind v1.0 und v1.0.1 zusammen:** die Phasen 1–9, die Anforderungen aus `.planning/milestones/v1.0-REQUIREMENTS.md` und die aus `.planning/REQUIREMENTS.md` (v1.0.1), alles geprüft auf dem Endstand. Für v1.0.1 ist danach kein eigenes Audit mehr nötig.
- **D-07:** **Es gibt eine Datei, `.planning/v1.0-MILESTONE-AUDIT.md`** (Name laut Roadmap). Ihr Kopf sagt ausdrücklich, dass v1.0.1 (Phasen 8 und 9) mit abgedeckt ist. Es gibt keine zweite Datei `v1.0.1-MILESTONE-AUDIT.md`.
- **D-08:** **Das Archiv wird direkt gelesen.** Der Audit-Workflow (`.claude/gsd-core/workflows/audit-milestone.md`) sucht unter `.planning/phases/*`. Die v1.0-Phasen liegen aber unter `.planning/milestones/v1.0-phases/`. Der Auditor bzw. der Integration-Checker bekommt beide Orte ausdrücklich als Eingabe. Es wird nichts verschoben oder kopiert.
- **D-09:** **Nyquist-Befunde werden gemeldet und zurückgestellt.** Gemeint sind `04-VALIDATION.md` (`status: draft`) und `05-VALIDATION.md` (`nyquist_compliant: false`). Sie stehen im Audit als `tech_debt` mit Begründung „deferred“. In dieser Phase läuft kein validate-phase.
- **D-10:** **Schwelle für den Lückenschluss:** Alles, was die Kernaussage betrifft, wird in Phase 9 mit Test behoben. Dazu gehören falsche oder unbelegte Zahlen, falsche Texte, Barrierefreiheit und Datenschutz (Personennamen). Reine Doku- oder Prozesslücken werden mit Begründung zurückgestellt (deferred bzw. v2-Backlog).
- **D-11:** **Das Audit läuft als letzter inhaltlicher Plan**, nach Security, Re-Verifikation und Aufräumen. SEC-01, AUD-02 und AUD-03 sind dann belegbar. AUD-01 führt der Bericht als „durch diesen Bericht erfüllt“.

### Re-Verifikation (AUD-02)
- **D-12:** **Ablauf: Re-Verify → Audit → Fix → Nachlauf → Abschlusslauf.** Behebt ein Fix aus dem Audit eine Lücke, werden danach die betroffenen VERIFICATION-Dateien und der Audit-Status aktualisiert (z. B. `gaps_found` → `passed`, mit Fix-Commit als Beleg). Zum Schluss läuft die Querschnittsbedingung (Roadmap-Kriterium 5).
- **D-13:** **Volle Re-Verifikation aller sieben Phasen.** Für jede der Phasen 1–7 gibt es einen vollständigen Goal-Backward-Lauf (gsd-verifier) gegen den aktuellen Code, auch für Phasen, die Phase 8 nicht berührt hat. Jede Datei bekommt einen `re_verification`-Block mit vorherigem Status und Score, geschlossenen Lücken und Regressionen. Die Dateien bleiben im Archiv unter `.planning/milestones/v1.0-phases/`. Danach meldet keine Phase mehr „stale“.
- **D-14:** **Phase 7: `status: passed`, Human-Items vom Nutzer bestätigt.** Der Nutzer hat am 2026-10-08 erklärt, dass er Deploy und Gerätecheck selbst erledigt hat (grüner Actions-Lauf samt Deploy, öffentliche URL, Gerätecheck bei 360–1280 px). Die beiden `human_verification`-Items in `07-VERIFICATION.md` bleiben stehen und werden als **vom Nutzer bestätigt (2026-10-08)** gekennzeichnet. Der Verifier markiert sie nicht als selbst geprüft. Der Widerspruch zwischen Frontmatter (`passed`) und Text („human_needed“) wird aufgelöst, beide sagen dann dasselbe.
- **D-15:** **`08-VERIFICATION.md` wird nur erneuert, wenn Phase 9 Code ändert**, also bei einem Security- oder Audit-Fix außerhalb von `.planning/`. Ohne Code-Änderung bleibt die Datei unverändert.

### Aufräumen der Planungsdokumente (AUD-03)
- **D-16:** **Aus „Blockers/Concerns“ in `STATE.md` fallen weg:** die Einträge zu `02-REVIEW.md` und `04-REVIEW-DISPOSITION.md` (beide Ledger stehen schon auf `open: 0`, geprüft am 2026-10-08), `/gsd-secure-phase 04` und „Kein Milestone-Audit / stale“. **Stehen bleibt** der Hinweis zur Scratch-Kopie (`app/node_modules` mit macOS-Binaries). Jeder andere Hinweis bleibt nur, wenn er nachweislich noch zutrifft.
- **D-17:** **Die Archive bekommen einen Nachtrag und werden nicht umgeschrieben.** In `.planning/MILESTONES.md` kommt unter v1.0 ein datierter Nachtrag dazu: „Audit und Re-Verifikation in v1.0.1 / Phase 9 nachgeholt“, mit Verweis auf `.planning/v1.0-MILESTONE-AUDIT.md`. Der bisherige Text („Kein Milestone-Audit“, „7 Phasen stale“) bleibt als historischer Stand stehen. `.planning/milestones/v1.0-ROADMAP.md` und `.planning/RETROSPECTIVE.md` bleiben unverändert.
- **D-18:** In `.planning/REQUIREMENTS.md` bleibt die Zeile „Deploy-/Gerätecheck aus Phase 7“ unter Out of Scope stehen und bekommt den Vermerk „vom Nutzer erledigt, 2026-10-08“.
- **D-19:** **Der Meilenstein v1.0.1 wird in Phase 9 nicht abgeschlossen.** Die Phase endet mit Audit und Abschlusslauf. `/gsd-complete-milestone` ruft der Nutzer danach selbst auf.

### Nachträge nach der Recherche (2026-10-09)
- **D-20:** **`08-REVIEW-DISPOSITION.md` (open: 9 von 10) wird in Phase 9 triagiert.** WR-01 (Test kann nie rot werden) und WR-02 (leere `beschriftung`) werden mit Test behoben, der Commit nennt die ID (`08/WR-01`, `08/WR-02`). Die Info-Befunde werden mit Begründung `deferred`, danach steht das Ledger auf `open: 0`. Das ist eine Codeänderung, also wird `08-VERIFICATION.md` nach D-15 erneuert.
- **D-21:** **`05-VERIFICATION.md` wird wie Phase 7 nach D-14 behandelt.** Die Human-Items bleiben stehen. Was durch UAT oder den Nutzer belegt ist, wird so gekennzeichnet, nichts wird als vom Verifier geprüft ausgegeben. Frontmatter und Text sagen danach dasselbe (`behavior_unverified` passend zum Text).
- **D-22:** **Phase-7-Befund CR-01 (Unterschriften auf `s009.webp`) wird nicht neu geöffnet.** Im Audit steht er als `tech_debt` mit Verweis auf die Nutzerentscheidung vom 2026-10-07.
- **D-23:** **Der Basislauf wird als `09-BASISLAUF.md` im Phasenordner abgelegt.** Er ist die gemeinsame Evidenz für die parallelen Verifier, die selbst `alle.py` nicht ausführen.

### Claude's Discretion
- Wie die Pläne zugeschnitten und in Wellen geordnet werden, innerhalb der Reihenfolge aus D-12. Die sieben Re-Verifikationen dürfen parallel laufen.
- Ob die Security-Prüfung über `/gsd-secure-phase`-Logik (gsd-security-auditor) oder als eigener Plan mit denselben Prüfschritten läuft. Bedingung: Das Ergebnis hat das Format der vorhandenen SECURITY-Dateien.
- Das genaue Frontmatter von `04-SECURITY.md` (z. B. ob `block_on` und `register_authored_at_plan_time` wie bei 02 und 03 gesetzt werden).
- Der genaue Wortlaut der Nachträge in MILESTONES.md und REQUIREMENTS.md.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Meilenstein und Anforderungen
- `.planning/ROADMAP.md` § Phase 9 — Ziel, Erfolgskriterien 1–5, Querschnittsbedingung
- `.planning/REQUIREMENTS.md` — SEC-01, AUD-01…03, Out of Scope (Deploy-/Gerätecheck)
- `.planning/milestones/v1.0-REQUIREMENTS.md` — v1.0-Anforderungen (85), Gegenstand des Audits (D-06)
- `.planning/milestones/v1.0-ROADMAP.md` — v1.0-Erfolgskriterien je Phase
- `.planning/PROJECT.md` — Constraints, Key Decisions
- `.planning/STATE.md` § Blockers/Concerns — Ziel von AUD-03
- `.planning/MILESTONES.md` § v1.0 Closeout — Ort des Nachtrags (D-17)

### Security Phase 4
- `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-0{1..6}-PLAN.md` — Threat-Register (`<threat_model>`-Tabellen, T-04-01…20, T-04-SC)
- `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-0{1..6}-SUMMARY.md`, `04-VERIFICATION.md`, `04-REVIEW.md`, `04-REVIEW-DISPOSITION.md` — Umsetzungsbelege der Phase 4
- `.planning/milestones/v1.0-phases/0{1,2,3,5,6,7}-*/0?-SECURITY.md` und `.planning/phases/08-fixes-und-triage/08-SECURITY.md` — Formatvorlage (Frontmatter, Register, Accepted Risks, Audit Trail)
- `.planning/phases/08-fixes-und-triage/08-CONTEXT.md` D-01…D-05 — Phase-8-Änderungen an `pruefe_text` und `jahr.*` (betrifft T-04-16, T-04-18)
- `.claude/gsd-core/workflows/secure-phase.md` — Ablauf der Security-Prüfung

### Audit und Verifikation
- `.claude/gsd-core/workflows/audit-milestone.md` — Audit-Ablauf und Frontmatter-Schema der Audit-Datei. Pfade per D-08 anpassen.
- `.planning/milestones/v1.0-phases/0{1..7}-*/0?-VERIFICATION.md` — die zu erneuernden Dateien
- `.planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-VERIFICATION.md` — Human-Items und Widerspruch passed/human_needed (D-14)
- `.planning/phases/08-fixes-und-triage/08-VERIFICATION.md`, `08-REVIEW-DISPOSITION.md` — Belege für in v1.0.1 geschlossene Lücken
- `.planning/milestones/v1.0-phases/0{1..7}-*/0?-VALIDATION.md` — Nyquist-Stand (D-09)
- `.planning/milestones/v1.0-phases/0{1,2,4,5,6}-*/0?-REVIEW-DISPOSITION.md` — Ledger-Stand (alle `open: 0`)

### Fachliche Spezifikation und Konventionen
- `discussion/SPEZIFIKATION.md` — fachliche Detailquelle, Anhang B (Sollwerte)
- `.claude/CLAUDE.md` — Konventionen, Befehle, lokale Nachstellung der CI (inkl. Reproduzierbarkeitsprüfung und `scripts/e2e-wie-ci.sh`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pipeline/tests/test_app_daten.py`, `test_produkte.py:198`, `test_belegbilder.py`, `test_manuell.py:471,517` — Namens- und meta.json-Tests (D-05)
- `scripts/e2e-wie-ci.sh` — Playwright wie in der CI (Abschlusslauf)
- `.github/workflows/ci.yml` — Jobs `pipeline`, `app`, Reproduzierbarkeits-Diff, e2e. Das ist die Referenz für den Abschlusslauf.

### Established Patterns
- SECURITY-Dateien: Frontmatter (`phase`, `slug`, `status`, `threats_open`, `asvs_level`, `created`), danach Threat-Register, Accepted Risks und Audit Trail.
- VERIFICATION-Dateien: Frontmatter mit `status`, `score`, `re_verification` (previous_status, previous_score, gaps_closed, gaps_remaining, regressions), `human_verification`. Vorlagen mit Re-Verifikation sind `02-VERIFICATION.md`, `03-VERIFICATION.md` und `07-VERIFICATION.md`.
- „stale“ heißt in gsd-tools: Ein SUMMARY ist neuer als die VERIFICATION der Phase (`.claude/gsd-core/bin/lib/roadmap.cjs` ~:1022, `phase.cjs` ~:3317). Eine erneuerte VERIFICATION muss also neuer sein als alle SUMMARYs ihrer Phase.
- App-Prüfungen nur in einer Scratch-Kopie von `app/` mit eigenem `npm ci`, weil `app/node_modules` macOS-Binaries enthält.

### Integration Points
- Alle Ergebnisdateien liegen unter `.planning/`. Code wird nur bei offenen Bedrohungen (D-04) oder Audit-Lücken (D-10) geändert, dann wird `08-VERIFICATION.md` ggf. erneuert (D-15).

</code_context>

<specifics>
## Specific Ideas

- Beim Sichten aufgefallen, gehört ins Audit bzw. in die Re-Verifikation: `07-VERIFICATION.md` hat im Frontmatter `status: passed`, im Text aber „human_needed“. Das löst D-14 auf.
- Der Nutzer bestätigt Deploy und Gerätecheck aus Phase 7 als erledigt (2026-10-08). Das ist eine Nutzerbestätigung, keine Verifier-Prüfung, und wird so gekennzeichnet.

</specifics>

<deferred>
## Deferred Ideas

- Nyquist-Validierung für Phase 4 (`04-VALIDATION.md` draft) und Phase 5 (`nyquist_compliant: false`): im Audit als tech_debt deferred (D-09), ein eigener `/gsd-validate-phase`-Lauf ist für später möglich.
- Abschluss von v1.0.1 (`/gsd-complete-milestone`): nach Phase 9 durch den Nutzer (D-19).

</deferred>

---

*Phase: 09-sicherheit-und-audit*
*Context gathered: 2026-10-08*
