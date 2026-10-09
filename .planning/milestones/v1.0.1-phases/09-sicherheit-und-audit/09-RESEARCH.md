# Phase 9: Sicherheit und Audit - Research

**Researched:** 2026-10-08
**Domain:** Nacharbeit an Planungsartefakten (Security-Register, Re-Verifikation, Milestone-Audit, STATE-Bereinigung) auf einem Python-Pipeline- plus Vue-App-Repo mit GSD-Tooling
**Confidence:** HIGH (Tooling, Baseline und Evidenzpfade in dieser Sitzung ausgeführt), MEDIUM (Inhalt des Audits, weil er erst entsteht)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Security-Prüfung Phase 4 (SEC-01)**
- **D-01:** **Jede Bedrohung wird mit Code und Testlauf belegt.** Der Eintrag im Register nennt die Fundstelle im aktuellen Code (`Datei:Zeile`) und mindestens einen Testnamen. Dieser Test muss in einem echten Lauf grün sein, eine Analyse allein reicht nicht. Die Belege aus den Phase-4-Plänen werden nicht ungeprüft übernommen. Das betrifft vor allem T-04-16 (Ziffernregel in `pruefe_text`, in Phase 8 verschärft, D-01 der Phase 8) und T-04-18 (`jahr`-Kürzel und `jahr.*`-Platzhalter, in Phase 8 erweitert, D-02 bis D-04 der Phase 8).
- **D-02:** **Nur die 21 Bedrohungen aus den Phase-4-Plänen, keine neuen IDs.** Hat Phase 8 den Code einer Bedrohung geändert, steht das als Vermerk mit Commit-Verweis bei der Bedrohung. Die Phase-8-Änderungen selbst deckt `.planning/phases/08-fixes-und-triage/08-SECURITY.md` ab (`threats_open: 0`). T-04-SC steht in allen sechs Plänen und wird **einmal** geführt.
- **D-03:** **Die Bewertungen `accept` werden geprüft und bestätigt, nicht hochgestuft.** T-04-11 (Stellenplan ohne Personennamen): Es wird geprüft, ob der Namens-Scan `stellenplan.csv` und `stellenplan.json` heute noch erfasst. T-04-20 (pytest startet `node` aus `app/node_modules`): Es wird geprüft, ob der Aufruf weiterhin eine feste Argumentliste ohne Shell nutzt, nur JSON über stdin bekommt und ohne Netz läuft. Beide kommen in den Abschnitt „Accepted Risks“.
- **D-04:** **Eine offene Bedrohung wird in Phase 9 mit Test behoben, und zwar vor dem Audit.** Der Commit nennt die ID, z. B. `04/T-04-07`. Danach wird die Bedrohung als mitigated mit diesem Commit eingetragen.
- **D-05:** Die Namens-Tests für `app/src/data/*.json` und `daten/manuell/meta.json` müssen im Lauf grün sein und dürfen nicht übersprungen werden (Roadmap-Kriterium 1). Kandidaten sind `test_keine_personennamen_in_app_daten` (`pipeline/tests/test_app_daten.py`), `test_keine_personennamen` (`pipeline/tests/test_produkte.py:198`) und `test_meta_json_gueltig` bzw. `test_meta_json_bricht_ab` (`pipeline/tests/test_manuell.py:471,517`). Brauchen sie das PDF unter `raw_data/`, muss es vorhanden sein. Ein Skip gilt nicht als Beleg.

**Milestone-Audit (AUD-01)**
- **D-06:** **Gegenstand sind v1.0 und v1.0.1 zusammen:** die Phasen 1–9, die Anforderungen aus `.planning/milestones/v1.0-REQUIREMENTS.md` und die aus `.planning/REQUIREMENTS.md` (v1.0.1), alles geprüft auf dem Endstand. Für v1.0.1 ist danach kein eigenes Audit mehr nötig.
- **D-07:** **Es gibt eine Datei, `.planning/v1.0-MILESTONE-AUDIT.md`** (Name laut Roadmap). Ihr Kopf sagt ausdrücklich, dass v1.0.1 (Phasen 8 und 9) mit abgedeckt ist. Es gibt keine zweite Datei `v1.0.1-MILESTONE-AUDIT.md`.
- **D-08:** **Das Archiv wird direkt gelesen.** Der Audit-Workflow (`.claude/gsd-core/workflows/audit-milestone.md`) sucht unter `.planning/phases/*`. Die v1.0-Phasen liegen aber unter `.planning/milestones/v1.0-phases/`. Der Auditor bzw. der Integration-Checker bekommt beide Orte ausdrücklich als Eingabe. Es wird nichts verschoben oder kopiert.
- **D-09:** **Nyquist-Befunde werden gemeldet und zurückgestellt.** Gemeint sind `04-VALIDATION.md` (`status: draft`) und `05-VALIDATION.md` (`nyquist_compliant: false`). Sie stehen im Audit als `tech_debt` mit Begründung „deferred“. In dieser Phase läuft kein validate-phase.
- **D-10:** **Schwelle für den Lückenschluss:** Alles, was die Kernaussage betrifft, wird in Phase 9 mit Test behoben. Dazu gehören falsche oder unbelegte Zahlen, falsche Texte, Barrierefreiheit und Datenschutz (Personennamen). Reine Doku- oder Prozesslücken werden mit Begründung zurückgestellt (deferred bzw. v2-Backlog).
- **D-11:** **Das Audit läuft als letzter inhaltlicher Plan**, nach Security, Re-Verifikation und Aufräumen. SEC-01, AUD-02 und AUD-03 sind dann belegbar. AUD-01 führt der Bericht als „durch diesen Bericht erfüllt“.

**Re-Verifikation (AUD-02)**
- **D-12:** **Ablauf: Re-Verify → Audit → Fix → Nachlauf → Abschlusslauf.** Behebt ein Fix aus dem Audit eine Lücke, werden danach die betroffenen VERIFICATION-Dateien und der Audit-Status aktualisiert (z. B. `gaps_found` → `passed`, mit Fix-Commit als Beleg). Zum Schluss läuft die Querschnittsbedingung (Roadmap-Kriterium 5).
- **D-13:** **Volle Re-Verifikation aller sieben Phasen.** Für jede der Phasen 1–7 gibt es einen vollständigen Goal-Backward-Lauf (gsd-verifier) gegen den aktuellen Code, auch für Phasen, die Phase 8 nicht berührt hat. Jede Datei bekommt einen `re_verification`-Block mit vorherigem Status und Score, geschlossenen Lücken und Regressionen. Die Dateien bleiben im Archiv unter `.planning/milestones/v1.0-phases/`. Danach meldet keine Phase mehr „stale“.
- **D-14:** **Phase 7: `status: passed`, Human-Items vom Nutzer bestätigt.** Der Nutzer hat am 2026-10-08 erklärt, dass er Deploy und Gerätecheck selbst erledigt hat (grüner Actions-Lauf samt Deploy, öffentliche URL, Gerätecheck bei 360–1280 px). Die beiden `human_verification`-Items in `07-VERIFICATION.md` bleiben stehen und werden als **vom Nutzer bestätigt (2026-10-08)** gekennzeichnet. Der Verifier markiert sie nicht als selbst geprüft. Der Widerspruch zwischen Frontmatter (`passed`) und Text („human_needed“) wird aufgelöst, beide sagen dann dasselbe.
- **D-15:** **`08-VERIFICATION.md` wird nur erneuert, wenn Phase 9 Code ändert**, also bei einem Security- oder Audit-Fix außerhalb von `.planning/`. Ohne Code-Änderung bleibt die Datei unverändert.

**Aufräumen der Planungsdokumente (AUD-03)**
- **D-16:** **Aus „Blockers/Concerns“ in `STATE.md` fallen weg:** die Einträge zu `02-REVIEW.md` und `04-REVIEW-DISPOSITION.md` (beide Ledger stehen schon auf `open: 0`, geprüft am 2026-10-08), `/gsd-secure-phase 04` und „Kein Milestone-Audit / stale“. **Stehen bleibt** der Hinweis zur Scratch-Kopie (`app/node_modules` mit macOS-Binaries). Jeder andere Hinweis bleibt nur, wenn er nachweislich noch zutrifft.
- **D-17:** **Die Archive bekommen einen Nachtrag und werden nicht umgeschrieben.** In `.planning/MILESTONES.md` kommt unter v1.0 ein datierter Nachtrag dazu: „Audit und Re-Verifikation in v1.0.1 / Phase 9 nachgeholt“, mit Verweis auf `.planning/v1.0-MILESTONE-AUDIT.md`. Der bisherige Text („Kein Milestone-Audit“, „7 Phasen stale“) bleibt als historischer Stand stehen. `.planning/milestones/v1.0-ROADMAP.md` und `.planning/RETROSPECTIVE.md` bleiben unverändert.
- **D-18:** In `.planning/REQUIREMENTS.md` bleibt die Zeile „Deploy-/Gerätecheck aus Phase 7“ unter Out of Scope stehen und bekommt den Vermerk „vom Nutzer erledigt, 2026-10-08“.
- **D-19:** **Der Meilenstein v1.0.1 wird in Phase 9 nicht abgeschlossen.** Die Phase endet mit Audit und Abschlusslauf. `/gsd-complete-milestone` ruft der Nutzer danach selbst auf.

### Claude's Discretion
- Wie die Pläne zugeschnitten und in Wellen geordnet werden, innerhalb der Reihenfolge aus D-12. Die sieben Re-Verifikationen dürfen parallel laufen.
- Ob die Security-Prüfung über `/gsd-secure-phase`-Logik (gsd-security-auditor) oder als eigener Plan mit denselben Prüfschritten läuft. Bedingung: Das Ergebnis hat das Format der vorhandenen SECURITY-Dateien.
- Das genaue Frontmatter von `04-SECURITY.md` (z. B. ob `block_on` und `register_authored_at_plan_time` wie bei 02 und 03 gesetzt werden).
- Der genaue Wortlaut der Nachträge in MILESTONES.md und REQUIREMENTS.md.

### Deferred Ideas (OUT OF SCOPE)
- Nyquist-Validierung für Phase 4 (`04-VALIDATION.md` draft) und Phase 5 (`nyquist_compliant: false`): im Audit als tech_debt deferred (D-09), ein eigener `/gsd-validate-phase`-Lauf ist für später möglich.
- Abschluss von v1.0.1 (`/gsd-complete-milestone`): nach Phase 9 durch den Nutzer (D-19).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| SEC-01 | Für Phase 4 liegt `04-SECURITY.md` mit `threats_open: 0` vor, nach dem Muster der anderen Phasen | Abschnitt „Threat Evidence Worksheet“ (21 Zeilen mit Startpunkten, Tests, Phase-8-Vermerken), Format der Vorlagen, bestätigter Testlauf ohne Skips |
| AUD-01 | Das Milestone-Audit für v1.0 ist durchgeführt. Seine Lücken sind geschlossen oder begründet zurückgestellt | Abschnitt „Audit Playbook“: Eingaben, Frontmatter-Schema, vorab gefundene Kandidaten, Abweichungen des Workflows von D-07/D-08 |
| AUD-02 | Die Verifikationen der Phasen 1–7 sind gegen den aktuellen Stand erneuert, keine steht mehr auf „stale“ | Abschnitt „Re-Verification Playbook“: wie „stale“ berechnet wird, `verification.fingerprint`, Reihenfolge-Falle, Phase-5/7-Widersprüche |
| AUD-03 | „Blockers/Concerns“ in STATE.md stimmt mit der Wirklichkeit überein | Abschnitt „STATE.md Cleanup“: belegte Ist-Lage jedes Eintrags, ein bisher nicht genannter offener Punkt (08-REVIEW-DISPOSITION) |
</phase_requirements>

## Summary

Phase 9 baut keinen Code, sondern vier belegbare Planungsartefakte (04-SECURITY.md, sieben erneuerte VERIFICATION-Dateien, bereinigtes STATE.md, v1.0-MILESTONE-AUDIT.md) und beendet mit einem Abschlusslauf. Die technische Basis ist in dieser Sitzung vollständig grün gemessen: `pytest` 681 bestanden und kein Skip (347 s), `alle.py --jahr 2026` in 29 s byte-identisch mit Regeln 1–10 grün, ruff sauber, App-Kette in einer Scratch-Kopie grün (type-check, lint, format:check, vitest, build) und Playwright über `scripts/e2e-wie-ci.sh` 89 bestanden in 35 s. Die Umgebung kann die gesamte CI-Kette lokal nachstellen, auch das Docker-Image und die Schriftdatei sind vorhanden.

Drei Dinge sind nicht aus CONTEXT.md ableitbar und prägen die Planung. (1) `gsd-tools verification.status` meldet alle sieben v1.0-Phasen aktuell als `stale`; die Berechnung ist ein Inhalts-Digest (`covered_digest`) über die in `covered_files` genannten Dateien plus alle PLAN/SUMMARY der Phase. Jede spätere Codeänderung in Phase 9 macht dadurch bereits erneuerte Berichte wieder „stale“, deshalb müssen die Digests als letzter Schritt vor dem Abschlusslauf neu berechnet werden. (2) `08-REVIEW-DISPOSITION.md` steht auf `open: 9` von 10 (darunter zwei Warnungen). Das steht weder in CONTEXT.md noch in STATE.md und wird das Audit als Lücke melden. (3) Zwei Belege aus den Phase-4-Plänen lassen sich auf dem Endstand nicht wörtlich wiederholen: T-04-19 (Diff gegen `f9e085d` ist durch spätere Phasen legitim verändert) und T-04-20 (der Plan nennt „der Test überspringt sich bei fehlendem node“, ein Skip zählt nach D-05/D-01 aber nicht als Beleg).

**Primary recommendation:** Fünf Wellen in der Reihenfolge Security (04-SECURITY.md) → sieben parallele Re-Verifikationen mit einem gemeinsamen, einmal gefahrenen Basislauf → Aufräumen (STATE, MILESTONES, REQUIREMENTS) → Audit (inkl. Triage der Lücken, Fixes mit Test) → Nachlauf (Digests aller betroffenen VERIFICATION-Dateien per `verification.fingerprint` neu berechnen) und Abschlusslauf der vollen CI-Kette. Keine Verifier und keine Fixes dürfen parallel `alle.py` ausführen.

## Architectural Responsibility Map

Die Phase ändert keine Anwendungsschicht; die Tabelle ordnet die Prüfgegenstände ihrem Besitzer zu, damit Belege am richtigen Ort gesucht werden.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Plausibilität der Zahlen (Regeln 1–10, 1-€-Toleranz) | Pipeline (`pipeline/ostbevern/pruefung.py`) | CI (Reproduzierbarkeits-Diff) | Prüfregeln leben in der Pipeline, CI wiederholt sie |
| Keine Personennamen in ausgelieferten Daten | Pipeline (Allowlist-Schreiber, `lies_personennamen`-Test) | App-Daten (`app/src/data/*.json`) | Entfernung beim Extrahieren, Test scannt `daten/` und `app/src/data/` |
| Text-Integrität (Ziffernregel, Platzhalter, Jahreskürzel) | Pipeline (`texte.py`) | App (`format.ts::formatiere`) | Pipeline validiert Text, App formatiert ausschließlich |
| Rendering ohne Roh-HTML | App (Vue-Templates, `quelltext.test.ts`) | Pipeline (`pruefe_text` verbietet `<`/`>`) | Zwei Schichten, beide belegen T-04-17 |
| Reproduzierbarkeit der Ausgaben | CI (`ci.yml`, Schritt „Pipeline reproduzierbar (D-24)“) | Pipeline (atomare Schreiber) | Der CI-Diff ist der letzte Wächter |
| Verifikationsstatus „stale“ | GSD-Tooling (`verification.cjs`) | Planungsdateien | Digest über Dateiinhalt, nicht über Zeitstempel (bei Berichten mit Fingerprint) |
| Audit-Bericht, STATE, MILESTONES, REQUIREMENTS | Planung (`.planning/`) | — | Reine Dokumentenarbeit, Code nur bei D-04/D-10-Fixes |

## Standard Stack

Es werden keine neuen Pakete installiert. Alles unten ist bereits im Repo oder Werkzeug der Sandbox.

### Core
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| gsd-tools (`.claude/gsd-core/bin/gsd-tools.cjs`) | im Repo installiert | `verification.status`, `verification.fingerprint`, `verification.append-audit`, `find-phase`, `init.phase-op`, `summary-extract`, `commit` | Einzige Quelle für „stale“-Berechnung und Digests; Hand-Berechnung ist ausgeschlossen |
| pytest | über `pipeline/uv.lock` | Testläufe als Belege für Bedrohungen | Projekt-Standard, 681 Tests |
| uv | 0.9.26 [VERIFIED: `uv --version`] | Pipeline-Umgebung (`uv run --directory pipeline …`) | CLAUDE.md-Vorgabe |
| Node | v22.22.1 [VERIFIED: `node --version`], `app/.nvmrc` = `22` | App-Prüfungen in Scratch-Kopie | passt zu `.nvmrc` |
| Docker + Image `mcr.microsoft.com/playwright:v1.63.0-noble` | Docker 29.8.1, Image vorhanden [VERIFIED: `docker image ls`] | `scripts/e2e-wie-ci.sh` | CI-getreuer Playwright-Lauf |

### Supporting
| Tool | Purpose | When to Use |
|------|---------|-------------|
| `gsd-security-auditor` (Agent) | Unabhängige Gegenprüfung der Belege, liefert nur ein Urteil, schreibt die Datei nicht | Optional in der Security-Welle (Claude's Discretion) |
| `gsd-verifier` (Agent) | Goal-Backward-Lauf je Phase 1–7 (D-13) | Welle Re-Verifikation, 7 parallele Läufe |
| `gsd-integration-checker` (Agent) | Phasen-Integration und End-to-End-Flüsse im Audit | Audit-Welle; Prompt anpassen (siehe Audit Playbook) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `/gsd-secure-phase 04` als Ganzes | Eigener Plan mit denselben Schritten | Der Workflow-Kurzschluss für `asvs_level == 1` würde „L1 grep-Tiefe“ genügen lassen (workflows/secure-phase.md, Schritt 3); D-01 verlangt mehr (echter Testlauf). Daher eigener Plan, der das Dateiformat der Vorlage nutzt |
| `/gsd-audit-milestone` unverändert | Workflow-Schritte manuell mit angepassten Pfaden | Der Workflow nimmt `milestone_version = v1.0.1` und sucht in `.planning/phases/*` (siehe Pitfall 6) |

**Installation:** keine. App-Prüfungen: `cp`/`tar` von `app/` ohne `node_modules` in ein Scratch-Verzeichnis, dort `npm ci`.

**Version verification:** Keine Paketempfehlungen, daher keine Registry-Prüfung nötig. `npm audit --omit=dev` in der Scratch-Kopie: 0 Schwachstellen; `npm audit` gesamt: 4 hohe (Paket `braces`, nur Entwicklungswerkzeug) [VERIFIED: ausgeführt]. Das stand bisher in keiner Planungsdatei (`grep -rln "npm audit" .planning` leer) und ist ein Hinweis für den Audit (tech_debt, kein Blocker).

## Package Legitimacy Audit

Diese Phase installiert keine externen Pakete. Gate nicht anwendbar.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
 CONTEXT.md (D-01..D-19)
        |
        v
 Welle 1: SECURITY ------------------------------------------------+
   04-0{1..6}-PLAN.md <threat_model>  --> Register (21)             |
   Code Stand Phase 8 (Datei:Zeile) + Testnamen                     |
   pytest-Lauf (kein Skip) --------------> 04-SECURITY.md           |
   offene Bedrohung? --ja--> Fix + Test (Commit "04/T-04-xx") ------+--> Code-Änderung?
        |                                                           |      (dann D-15, Digests)
        v                                                           |
 Welle 2: RE-VERIFIKATION (7 parallel, gsd-verifier)                |
   gemeinsamer Basislauf (1x: pytest, alle.py, App-Kette, e2e) ----> Evidenzdatei
   je Phase: Goal-Backward ----> 0N-VERIFICATION.md (re_verification-Block)
        |
        v
 Welle 3: AUFRÄUMEN  STATE.md | MILESTONES.md (Nachtrag) | REQUIREMENTS.md (Vermerk)
        |
        v
 Welle 4: AUDIT  Archiv + .planning/phases/ lesen (D-08)
   Anforderungen 85 + 17 (3-Quellen-Abgleich)
   Phasen-Integration + E2E-Flüsse (integration-checker)
   Nyquist (D-09) --> v1.0-MILESTONE-AUDIT.md (Status, Lücken, tech_debt)
        |  Lücke Kernaussage? --ja--> Fix + Test (D-10), betroffene VERIFICATION anpassen (D-12)
        v
 Welle 5: NACHLAUF + ABSCHLUSSLAUF
   verification.fingerprint für alle betroffenen Phasen (letzter Schritt nach letzter Codeänderung)
   verification.status = nicht stale für 01..08
   pytest + ruff + alle.py (Diff leer) + App-Kette (Scratch) + e2e-wie-ci.sh
```

### Recommended Project Structure
```
.planning/
├── v1.0-MILESTONE-AUDIT.md                     # neu (D-07)
├── STATE.md                                    # Blockers/Concerns bereinigt
├── MILESTONES.md                               # Nachtrag unter v1.0 (D-17)
├── REQUIREMENTS.md                             # Vermerk Out-of-Scope-Zeile (D-18)
├── milestones/v1.0-phases/04-.../04-SECURITY.md # neu
├── milestones/v1.0-phases/0{1..7}-*/0?-VERIFICATION.md  # erneuert
└── phases/09-sicherheit-und-audit/             # Pläne, Summaries, Verification der Phase 9
```

### Pattern 1: SECURITY-Datei nach Vorlage
**What:** Frontmatter, Trust Boundaries, Threat Register, Accepted Risks Log, Security Audit Trail, Sign-Off.
**When to use:** 04-SECURITY.md.
**Format der Vorlagen (gelesen):** 03-SECURITY.md Frontmatter lautet verbatim:
```yaml
---
phase: "3"
slug: "details"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-10-02"
---
```
[VERIFIED: `.planning/milestones/v1.0-phases/03-details/03-SECURITY.md:1-11`]. 08-SECURITY.md nutzt dieselben Kopfzeilen ohne `block_on`/`register_authored_at_plan_time` und mit `phase: "08"`; die Register-Spalten lauten dort `Threat ID | Category | Component | Severity | Disposition | Mitigation | Status` [VERIFIED: `08-SECURITY.md` Register-Kopf]. Die Phasen 1, 5, 6, 7 haben keine `block_on`-Zeile. Empfehlung: für 04 `phase: "4"`, `slug: "manuelle-daten-und-app-daten"`, `block_on: high`, `register_authored_at_plan_time: true` (alle sechs Pläne haben einen `<threat_model>`-Block), `created` mit dem Tag der Prüfung.
**Audit Trail** über `gsd_run query verification.append-audit "<datei>" --heading "Security Audit" --rows '{"Threats found": 21, "Closed": 21, "Open": 0}'` (Verb existiert in `workflows/secure-phase.md`, Schritt 6) oder wie 08-SECURITY.md mit Tabelle plus Abschnitt „Security Audit 2026-10-08“.
**Phase-8-Vermerke** gehören in die Mitigation-Zelle der betroffenen Zeile (D-02), nicht in neue IDs.

### Pattern 2: VERIFICATION mit `re_verification`-Block
**What:** Frontmatter `status`, `score`, `covered_files`, `covered_digest`, `behavior_unverified`, `re_verification` (`previous_status`, `previous_score`, `gaps_closed`, `gaps_remaining`, `regressions`), optional `human_verification`.
**Vorlagen:** 02, 03 und 07-VERIFICATION.md (CONTEXT). Zulässige Werte für `status` im Bericht sind genau `passed`, `gaps_found`, `human_needed` [VERIFIED: `.claude/gsd-core/bin/lib/verification.cjs` `VERIFIER_STATUSES`]. `stale` ist reiner Lesezustand und darf nie in einen Bericht geschrieben werden.

### Pattern 3: Audit-Datei
Frontmatter laut Workflow (Schritt 6): `milestone`, `audited`, `status: passed | gaps_found | tech_debt`, `scores` (requirements, phases, integration, flows), `gaps` (requirements, integration, flows), `tech_debt` (Liste je Phase). Der Kopf nennt nach D-07 ausdrücklich v1.0 und v1.0.1.

### Anti-Patterns to Avoid
- **`covered_digest` von Hand oder aus dem Gedächtnis schreiben.** Immer `verification.fingerprint` ausführen und Ausgabe übernehmen.
- **Beleg „Test existiert“ ohne Lauf.** D-01/D-05 verlangen einen grünen Lauf; `-rs` muss null Skips zeigen.
- **Neue Bedrohungs-IDs für Phase-8-Änderungen.** D-02 verbietet es.
- **Archiv umschreiben.** MILESTONES.md und die Roadmap-Archive bekommen nur Nachträge (D-17).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| `covered_digest` und `covered_files` | eigenes Hashing oder Pfadliste | `node .claude/gsd-core/bin/gsd-tools.cjs query verification.fingerprint <phase-dir> <dateien…>` | Gibt `covered_files` (inkl. aller PLAN/SUMMARY der Phase automatisch) und `v3:sha256:…` aus [VERIFIED: ausgeführt für Phase 4] |
| Stale-Prüfung | Zeitstempel vergleichen | `… query verification.status <phase-dir>` | Gleiche Funktion, die auch `gsd-progress` nutzt; eigene Logik würde abweichen |
| Audit-Trail-Zeile in SECURITY | Zeile von Hand anhängen | `verification.append-audit` | Überspringt Duplikate bei unverändertem Register |
| Requirement-Abdeckung je Plan | grep über SUMMARYs | `query summary-extract <summary> --fields requirements_completed --pick requirements_completed` | Für alle 85 v1.0-IDs getestet, siehe Audit Playbook |
| Personennamen-Suche | eigener Scraper | die vorhandenen Tests (`lies_personennamen`) | Nadeln stammen aus dem PDF, nicht aus einer Liste |
| Playwright-Umgebung | eigener Container-Aufruf | `scripts/e2e-wie-ci.sh <scratch>/app` | Fixiert Schriftpaket per SHA-256 (G-07-2) |

**Key insight:** In dieser Phase entsteht Vertrauen aus reproduzierbaren Läufen und Tool-Ausgaben. Jede Zahl im Bericht (Anzahl Tests, Regelzähler, Digests) soll aus einem Lauf stammen, nicht aus einer früheren Zusammenfassung.

## Threat Evidence Worksheet (SEC-01)

Register laut `<threat_model>`-Blöcken der sechs Pläne [VERIFIED: gelesen]. 20 Einzel-IDs (T-04-01 bis T-04-20) plus T-04-SC, einmal geführt = 21. Severity und Disposition stammen aus den Plänen. Spalte „Startpunkt“ ist ein Hinweis aus Grep bzw. Lesen in dieser Sitzung, der Executor liest die Stelle vor dem Eintrag neu (D-01: Belege aus den Plänen nicht ungeprüft übernehmen). Alle genannten Tests liefen in dieser Sitzung grün (siehe Testlauf unten), sofern nicht anders vermerkt.

| ID | Sev | Disp | Startpunkt im Code | Tests (Namen) | Phase-8-Vermerk / Besonderheit |
|----|-----|------|--------------------|---------------|-------------------------------|
| T-04-01 | high | mitigate | `pruefung.py` `_pruefe_regel5` (:1412), `_pruefe_regel4_b4` (:870); Sollwerte `pipeline/jahrgaenge/2026_sollwerte.toml` | `test_regel5_stufe_a_erkennt_tippfehler` (test_manuell.py:129), `test_regel4_b4_erkennt_tippfehler_in_steuerarten` (test_pruefung.py:466) | keine Änderung in Phase 8 an `pruefung.py` [VERIFIED: `git diff --stat 93b0a61..HEAD -- pipeline/ostbevern`] |
| T-04-02 | med | mitigate | `pruefung.py` `_wende_befunde_an` (:484, Aufruf :2746); `daten/pruefberichte/befunde.md` | `test_veralteter_befund_wenn_abweichung_nicht_mehr_passt` (:783), `test_veralteter_befund_ohne_passende_abweichung` (:814), `test_veralteter_befund_macht_bericht_nicht_gruen` (:833) alle test_pruefung.py; `alle.py` meldet „Veraltete Befunde: 0“ [VERIFIED: Lauf] | — |
| T-04-03 | high | mitigate | `app_daten.py` `APP_PRODUKT_SCHLUESSEL` (:417), Auswahl :492; Scan `test_app_daten.py:134-152` | `test_keine_personennamen_in_app_daten` | `beispieldaten.json` wurde in Phase 8 gelöscht (96a23de), der Scan nimmt `rglob("*.json")`, deckt also weiter alle JSON-Dateien |
| T-04-04 | med | mitigate | `schema.py` `schreibe_produkte_json` atomar „temp-Datei + os.replace“ (:366-393); CI-Schritt „Pipeline reproduzierbar (D-24)“ in `.github/workflows/ci.yml` [VERIFIED: gelesen] | `test_app_json_deterministisch` (test_app_daten.py:98), `test_haushalt_json_eingecheckt_aktuell` (:120) | `ci.yml` in Phase 8 nur Kommentar geändert [VERIFIED: `git diff 93b0a61 HEAD -- .github/workflows/ci.yml`, 3 Kommentarzeilen]; `alle.py --jahr 2026` byte-identisch [VERIFIED: Lauf] |
| T-04-05 | high | mitigate | `manuell.py` `_META_TOP_SCHLUESSEL` (:28), `_META_SATZUNG_SCHLUESSEL = ("beschluss", "ausfertigung")` (:44), `lies_meta_json` (:114-150, gelesen); `daten/manuell/README.md` Hinweis (:93-94) | `test_meta_json_gueltig` (test_manuell.py:471), `test_meta_json_bricht_ab` (:517, 9 Fälle), `test_keine_personennamen` (test_produkte.py:198) | `meta.json` hat die Schlüssel `['einwohner','flaeche','hebesaetze','kreisumlage','satzung','vorbericht_werte']` und `satzung` nur `beschluss`/`ausfertigung` [VERIFIED: Lauf]. Achtung: Der Namens-Scan arbeitet mit Nadeln aus den Personenfeldern der Produktinformationen; die Namen auf PDF S. 9 (Satzung) sind nicht in der Nadelmenge. Der Beleg für `meta.json` ist daher die strikte Allowlist plus Test, nicht der Scan allein. Im Register so formulieren |
| T-04-06 | high | mitigate | `pruefung.py` `_pruefe_regel5_eigenkapital_summe` (:1583), `_pruefe_regel5_satzung_paragraf4` (:1681), `_pruefe_regel5_ve_uebersicht` (:1769), `pruefe_regel5_schulden_ruecklagen_ve` (:1873) | `test_regel5_d11_gruen` (test_manuell.py:655), `test_regel5_ve_uebersicht_luecke_bei_fehlendem_paar` (:674), `test_schema_verbindlichkeiten_kanonisch` (:616), `test_schema_eigenkapital_kanonisch` (:624), `test_schema_ve_uebersicht_kanonisch` (:636) | Phase-8-Änderung an `pruefung.py`: keine |
| T-04-07 | med | mitigate | `pruefung.py` `pruefe_eckwerte_konsumiert` (:1318), Aufruf in `pruefe_alles` (:2664) | `test_eckwerte_ohne_pruefung_bricht_ab` (test_manuell.py:554) | — |
| T-04-08 | med | mitigate | `pruefung.py` `TOLERANZ_EURO = 1` (:85), `TOLERANZ_JE_REGEL = {9: 0, 10: 0}` (:92), `toleranz_fuer` (:95-97) | `test_toleranz_je_regel` (test_manuell.py:526) | 1-€-Toleranz unverändert; Regelzähler Lauf: Regel 1 6593, 2 7994, 3 114, 4 259, 5 150, 6 1964, 7 1152, 8 820, 9 12, 10 19 [VERIFIED: `alle.py`-Ausgabe] |
| T-04-09 | high | mitigate | `stellenplan.py` `_TOP_TOLERANZ = 8.0` (:40), `_ordne_werte` (:135), Insgesamt-Abgleich (:363-380); `pruefung.py` `_pruefe_regel10` (:2046), `_pruefe_regel9` (:1997) | `test_stellenplan_manipulierte_insgesamt_bricht_ab` (test_stellenplan.py:318), `test_stellenplan_wert_ohne_gruppe_innerhalb_toleranz_bricht_ab` (:335), `test_stellenplan_uebersicht_manipulierte_summe_zeile_bricht_ab` (:408), `test_stellenplan_csv_eingecheckt_aktuell` (:350), `test_regel10_gruen_wenn_summen_uebereinstimmen` (test_pruefung.py:2087) | Der Plan nennt „fixed 8.0-pt bound and unique minimum“; Executor prüft, dass der Code das noch tut |
| T-04-10 | med | mitigate | `stellenplan.py` `lies_stellen_hundertstel` (:51-72, gelesen): arbeitet auf der Zeichenkette, `StellenplanFehler` bei ungültigem Text | `test_lies_stellen_hundertstel` (test_stellenplan.py:98), `test_lies_stellen_hundertstel_ungueltig` (:103) | — |
| T-04-11 | low | **accept** | Scan `test_produkte.py:198` (rglob über ganz `daten/`, enthält `daten/aufbereitet/stellenplan.csv`) und `test_app_daten.py:134` (rglob `*.json`, enthält `stellenplan.json`). Spaltenkopf der CSV: `teil,position,gruppe,amtsbezeichnung,verguetung,produktbereich,merkmal,jahr,stichtag,stellen_hundertstel,personen,vermerk,pdf_seite`; Schlüssel der JSON: `haushaltsjahr`, `einheit_stellen`, `zeilen` [VERIFIED: Lauf] | beide Namens-Tests | D-03: nur bestätigen. In „Accepted Risks“ mit Nachweis, dass beide Dateien im Scan liegen und keine Namensspalte existiert |
| T-04-12 | high | mitigate | `app_daten.py` `APP_PRODUKT_SCHLUESSEL` (:417), Prüfung (:448-492) | `test_produkte_json_ohne_personenfelder` (test_app_daten.py:665), `test_keine_personennamen_in_app_daten`, `test_keine_personennamen` | Unabhängiger Wortpaar-Scan in dieser Sitzung (206 Wortpaare aus 126 Personenfeldern, 42 Dateien in `daten/` und `app/src/data/`): ein Trefferpaar in `produkte.json` und `erlaeuterungen.csv`, Kontext ist die Einrichtung „Servicestelle Personal“, also keine Person. Deckt sich mit dem Auditvermerk in 03-SECURITY.md |
| T-04-13 | high | mitigate | `app_daten.py` KL-Aufteilung | `test_kl_knoten_gleich_tp_15` (test_app_daten.py:456), `test_kl_knoten_reduziert_kette` (:471), `test_kl_knoten_kinder_gerundet` (:511), `test_zuschussbedarf_summe_top_knoten` (:553), `test_hierarchie_csv_unveraendert` (:610) | Der Plan nennt zusätzlich einen Erhaltungstest und einen Satzungs-Summentest; Executor sucht den genauen Namen (nicht verifiziert) |
| T-04-14 | med | mitigate | `manuell.py` `schuldenstand_euro` (gelesen, Quelle „Σ SCHULDEN_POSTEN … × 1000“), Fortschreibung in `app_daten.py` | `test_investitionen_schuldenstand_fortschreibung` (test_app_daten.py:711), `test_schuldenstand_fortschreibung_schreibt_ab_letztem_gedrucktem_stand_fort` (:862), `test_schuldenstand_fortschreibung_ohne_gedruckten_stand_vor_dem_jahr_bricht_ab` (:875) | — |
| T-04-15 | med | mitigate | `texte.py` `loese_auf` (:619-650, gelesen) | `test_unbekannter_platzhalter_bricht_schritt_07_ab` (test_app_daten.py:836), `test_loese_auf_unbekannter_schluessel_bricht_ab` (test_texte.py:777), `test_loese_auf_lehnt_ungueltiges_festes_jahr_ab` (:579) | **Phase 8 hat den Auflösepfad erweitert.** Neben `schluessel in werte` gilt jetzt `festes_jahr(schluessel)` (`_FESTES_JAHR_MUSTER = re.compile(r"^jahr\.fest_((?:19|20)\d{2})$")`, texte.py:50, Commit 7d4be31) und `_pruefe_jahrbezug` (e8e25d5). Weiterhin kein `eval`/`getattr`; unbekannter Schlüssel wirft `TexteFehler`. Als Vermerk eintragen |
| T-04-16 | high | mitigate | `texte.py` `pruefe_text` (:208-261, gelesen) | `test_pruefe_text_ungueltig` (test_texte.py:430), `test_pruefe_text_lehnt_getippte_jahreszahl_ab` (:445), `test_pruefe_text_1990er_trifft_die_allgemeine_ziffernregel` (:455), `test_erklaerungen_keine_nackten_ziffern` (:846), `test_glossar_keine_nackten_ziffern` (:954) | **Phase 8 verschärft:** Jahreszahlen sind keine Ausnahme der Ziffernregel mehr (27e0be7, 7d4be31, 57063a0 Test RED), Titel werden geprüft (`pruefe_titel`), Division durch 0 (c1da62e). Kommentar im Code: „Jahreszahlen sind keine Ausnahme mehr (D-01)“ |
| T-04-17 | med | mitigate | `texte.py:221-222` „`if "<" in text or ">" in text: raise TexteFehler(…)`“ (gelesen). App: `grep -rn "v-html" app/src` liefert nur Testdateien (kein Template); `quelltext.test.ts:71-76` `ROH_HTML`, :149 Test | `test_pruefe_text_ungueltig` (Parameter `"<b>fett</b>"`, `"ein Text mit > Zeichen"`), vitest `quelltext.test.ts` („erkennt die Roh-HTML-Direktive“) | vitest-Lauf in Scratch-Kopie ist grün [VERIFIED: Lauf], Testnamen im Detail vom Executor aus der Ausgabe holen |
| T-04-18 | high | mitigate | `format.ts` `jahr()` (:90-92), `FormatKuerzel` (:141), `case 'jahr'` (:169, gelesen); `texte.py` `FORMATKUERZEL` (:31), Namensraumregel „`if schluessel.startswith("jahr.") and format_kuerzel != "jahr"`“ (gelesen) | `test_cr01_gruppiertes_haushaltsjahr_wird_erkannt` (test_formatiere.py:441), `test_erklaerungen_rendern_korrekt` (:421), `test_texte_json_rendert_korrekt` (:433), `test_port_wie_format_ts` (:456), `test_formatkuerzel_wie_format_ts` (test_texte.py:989), `test_pruefe_text_jahr_platzhalter_braucht_formatkuerzel_jahr` (:1037) | **Phase 8 erweitert:** `jahr.*`-Namensraum und `jahr.fest_JJJJ` (7d4be31, e8e25d5), `test_formatiere.py` kennt `jahr.fest_JJJJ` (c27904b), `format.ts` rd.-Regel (dde7341). Optionaler Starkbeleg: Mutationsprobe in einer tmp-Kopie (`jahr` → `zahl` im Platzhalter), Tests müssen rot werden; ohne Repo-Änderung |
| T-04-19 | med | mitigate | Abnahmediff gegen `f9e085d` nach Suffix-Normalisierung | siehe Besonderheit | **Wörtliche Wiederholung auf HEAD unmöglich**, weil `erklaerungen.md` und `texte.json` seitdem legitim wuchsen (Diff 110 bzw. 499 Zeilen gegen HEAD). Stattdessen am Abschlusscommit der Phase-4-Änderung prüfen: Beide Dateien sind bei `52b3d3b` nach `sed 's/{{jahr\.haushaltsjahr\|jahr}}/{{jahr.haushaltsjahr\|zahl}}/g'` identisch mit `f9e085d` [VERIFIED: ausgeführt, beide „identical“]. Spätere Commits (fb6959a Phase 5, 319ef84 Phase 6, 7d4be31/e8e25d5 Phase 8) gehören zu deren eigenen Registern. Im Register als „geschlossen am 52b3d3b, historisch“ formulieren |
| T-04-20 | low | **accept** | `test_formatiere.py:497-506` „`subprocess.run(["node", "--input-type=module", "-e", _NODE_SKRIPT, str(app_wurzel)], input=json.dumps(paare), capture_output=True, text=True, encoding="utf-8", check=False, timeout=120)`“ (gelesen). Skript `_NODE_SKRIPT` (:320-331) liest `format.ts` und stdin, kein Netz, kein Shell | `test_port_wie_format_ts` (:456) | **Skip-Falle:** Der Test enthält `pytest.skip` bei fehlendem `node` (:461) oder `app/node_modules/typescript` (:463). D-05/D-01: Skip ist kein Beleg. In der Sandbox sind beide vorhanden, der Lauf mit `-rs` zeigte null Skips [VERIFIED: Lauf]. Die Ausgabe `-rs` im Nachweis aufbewahren |
| T-04-SC | high | mitigate | Keine Abhängigkeitsdatei im Phase-4-Commitbereich `3973d86..7f605fd` geändert (`git log … -- pipeline/pyproject.toml pipeline/uv.lock app/package.json app/package-lock.json` leer) [VERIFIED: ausgeführt]; seit Phase-8-Basis `93b0a61` ebenfalls leer [VERIFIED: `git diff --stat`] | — | Spätere Paketänderungen (z. B. vitest `ed9798c`, Playwright `fdab3d5`) gehören zu den Registern von 05 und 07. Phase 4 hat gar keine Abhängigkeit installiert |

**Ergebnis der Vorabprüfung:** Keine der 21 Bedrohungen ist erkennbar offen. D-04 (Fix mit Test) tritt nach heutigem Stand nicht ein, die Planung soll den Fall aber als bedingte Aufgabe vorsehen.

**Testlauf als Beleg:** Ein gezielter Lauf der oben genannten Tests plus `test_formatiere.py` und `test_texte.py` ergab `150 passed in 16.34s` ohne Skips [VERIFIED: `uv run pytest -p no:cacheprovider -rs -q …`]. Der volle Lauf `681 passed in 347.44s (0:05:47)`, `-rs` ohne Skip-Zeile [VERIFIED: Lauf]. Der gezielte Lauf (16 s) reicht für das Register, der volle Lauf gehört in den Abschlusslauf.

**Format-Hinweise für die Mitigation-Zellen:** Vorlagen nennen `Datei:Zeile` in Backticks und Testnamen; Wiederverwendung des Satzes „Tests `a`, `b`“ wie in 03-SECURITY.md. Accepted Risks als Tabelle `Risk ID | Threat Ref | Rationale | Accepted By | Date` mit `AR-04-01` (T-04-11) und `AR-04-02` (T-04-20) und der Fußzeile „Accepted risks do not resurface in future audit runs.“ [VERIFIED: Format aus 03-SECURITY.md und 08-SECURITY.md].

**Nicht-blockierende Härtungshinweise** (Vorlage 03-SECURITY.md kennt den Abschnitt „Non-blocking hardening candidates“, 07 den Abschnitt „Hinweise aus dem Audit (ändern keinen Status)“): Der Namens-Scan ist whole-value-basiert (03-SECURITY.md nennt 38 von 126 Werten mit mehreren Personen ohne Trenner). Der unabhängige Wortpaar-Scan dieser Sitzung fand keinen Personennamen, das kann als Auditvermerk ohne Statusänderung stehen.

## Re-Verification Playbook (AUD-02)

### Wie „stale“ entsteht (belegt)
`verification.status` auf jeden der sieben Archivordner meldet heute `"status": "stale"` [VERIFIED: ausgeführt für 01 bis 07]; Phase 8 meldet `passed`. Zwei Mechanismen, `verification.cjs` (:1360-1455, gelesen):
1. **Bericht mit Fingerprint** (`covered_files` und/oder `covered_digest` im Frontmatter): Digest wird neu berechnet und verglichen. Version v3 hasht `covered_files` vereinigt mit allen `*-PLAN.md`/`*-SUMMARY.md` der Phase (`phaseArtifactPaths`); Berichte selbst sind ausgeschlossen. v2-Berichte (heute 01 bis 06 laut `covered_digest: "v2:sha256:…"`) prüfen zusätzlich, ob jede Plan/Summary-Datei der Phase in `covered_files` steht.
2. **Bericht ohne Fingerprint:** Zeitvergleich, ob ein SUMMARY neuer ist als der Bericht (CONTEXT „Established Patterns“).
Die Berichte der Phasen 02 bis 04 listen teils noch alte Pfade `.planning/phases/04-…` (Archivierung hat sie verschoben, siehe Frontmatter von 04-VERIFICATION.md). Ein neu erzeugter Fingerprint mit `verification.fingerprint <archiv-ordner> <dateien>` löst Pfade im Archiv korrekt auf [VERIFIED: Lauf für Phase 4, Ausgabe `.planning/milestones/v1.0-phases/04-…/04-01-PLAN.md` etc. und `v3:sha256:0a42…`].

### Ablauf je Phase (D-13)
1. `gsd-verifier` mit Archivordner, Phase-Ziel aus `.planning/milestones/v1.0-ROADMAP.md`, Anforderungs-IDs der Phase und den Evidenzlauf als Eingabe.
2. Neuer Bericht mit `re_verification`-Block: `previous_status`, `previous_score`, `gaps_closed`, `gaps_remaining`, `regressions`.
3. Fingerprint erzeugen mit den vom Verifier tatsächlich geprüften Quelldateien; `covered_files` und `covered_digest` in den Kopf übernehmen.
4. `verification.status <ordner>` muss `passed` liefern (nicht `stale`).

### Vorab gefundene Inkonsistenzen, die der Verifier auflösen muss
| Phase | Befund | Stand heute [VERIFIED: gelesen] | Lösung |
|-------|--------|-------------------------------|--------|
| 07 | Frontmatter `status: passed`, `score: 4/5 must-haves verified`, Text „**Status:** human_needed“ (07-VERIFICATION.md :67) und zwei `human_verification`-Items (Deploy, Gerätecheck) | Widerspruch | D-14: `passed`, Items stehen lassen und mit „vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft“ kennzeichnen. Das vierte-von-fünf-Kriterium im Score explizit erklären (Score zählt weiter 4/5 Verifier-geprüft plus Nutzerbestätigung). Der Statuswert `human_needed` bleibt als Verifier-Wert zulässig, hier gilt `passed` per Nutzerentscheidung |
| 05 | Frontmatter `status: passed`, Text „**Status:** human_needed“ (:173), `behavior_unverified: 5`, zwölf `human_verification`-Einträge, darunter Fußzeilen-Platzhalter `.invalid` | gleicher Widerspruch wie 07, **nicht in CONTEXT genannt** | `05-UAT.md` ist `complete` (8 pass), `app/src/config.ts` enthält heute keine Platzhalter mehr (`KONTAKT_EMAIL = 'mail@thomas-manthey.de'`, `ORIGINAL_PDF_URL = 'https://www.ostbevern.de/…'`) [VERIFIED: gelesen]. Der Verifier soll jede Human-Zeile entweder durch UAT/Playwright belegen oder als „Nutzer/UAT bestätigt“ kennzeichnen und `behavior_unverified` neu zählen. Der Verifier darf nichts als selbst geprüft ausgeben, was nur UAT belegt |
| 01 | `re_verification` mit Trigger „stale“ und `files_changed_since_previous` | gültig, muss aktualisiert werden | neuer Block über Stand nach Phase 8 (u. a. `konfiguration.py`: negative `anzahlen.*` abgelehnt, 4c105ff) |
| 02, 03 | Bericht nennt Digest v2 | stale | neu fingerprinten; 02 und 03 sind laut Frontmatter bereits Re-Verifikationen, `previous_*` auf den heutigen Stand setzen |
| 04 | `covered_files` mit alten Pfaden; Hinweis „REQUIREMENTS.md-Tracking … stale Bookkeeping“ (:141) | Tracking in `v1.0-REQUIREMENTS.md` zeigt heute alle 85 als `[x]`/Complete [VERIFIED: gelesen, 0 offene] | Hinweis als erledigt vermerken |
| 06 | `re_verification.human_items_resolved` bereits durch UAT | gültig | übernehmen |

### Basislauf einmal, nicht siebenmal
Jede der sieben Verifikationen braucht dieselben Läufe (pytest, `alle.py`, App-Kette, e2e). Parallel gestartete `alle.py`-Läufe schreiben in dieselben Verzeichnisse `daten/`, `app/src/data/` und `app/public/quellen` und würden sich gegenseitig stören oder die Byte-Gleichheit vortäuschen. **Empfehlung:** Ein Vorlauf-Plan fährt die Basis einmal und schreibt eine Evidenzdatei (`.planning/phases/09-sicherheit-und-audit/09-BASISLAUF.md` oder im Scratchpad) mit Befehl, Exit-Code, Zählern und Dauer; die Verifier lesen sie, führen höchstens read-only-Checks aus (`git diff`, `grep`, gezielte pytest-Auswahl wie oben) und starten **nie** `alle.py`. App-Prüfungen: je Verifier eine eigene Scratch-Kopie (npm ci dauerte 2 s, siehe Environment).

### Reihenfolge-Falle (wichtigste für AUD-02)
Der Digest deckt Codedateien (z. B. `app/src/charts/format.ts`, `pipeline/ostbevern/texte.py`, `app/src/data/texte.json`). Jede Codeänderung in Phase 9 (D-04, D-10-Fix) macht alle Berichte stale, die diese Datei überdecken, auch bereits erneuerte. Lösung: Der Digest wird im **Nachlauf** (Welle 5) nach der letzten Codeänderung neu berechnet und eingetragen. Der Berichtsinhalt (Prosa, Score, `re_verification`) kann vorher stehen. Zusätzlich: Eine Änderung an Code, den `08-VERIFICATION.md` deckt, erzwingt nach D-15 die Erneuerung von 08 (Digest und Eintrag der Änderung); `08-VERIFICATION.md` listet 41 `covered_files` darunter `DatenTabelle.vue`, `texte.py`, `format.ts`, `texte.json` [VERIFIED: gelesen].

## Audit Playbook (AUD-01)

### Abweichungen des Workflows von den Entscheidungen (belegt)
- `init.milestone-op` liefert `milestone_version: "v1.0.1"`, `phase_count: 2` [VERIFIED: ausgeführt]. Der Workflow würde `v1.0.1-MILESTONE-AUDIT.md` anlegen und nur die Phasen 8 und 9 sehen. D-07/D-08 verlangen den Namen `.planning/v1.0-MILESTONE-AUDIT.md` und beide Orte. Der Plan führt die Workflow-Schritte deshalb von Hand aus und gibt dem Integration-Checker die Ordnerliste explizit.
- `gsd-integration-checker` hat `disallowedTools: Write, Edit, MultiEdit` und liefert nur einen Bericht [VERIFIED: Agent-Datei gelesen]; der Auditor schreibt die Datei. Der Agent ist für Auth, API-Routen und Formulare geschrieben; das Projekt hat weder Backend noch Auth. Der Prompt muss die relevanten Flüsse nennen (siehe unten), und Auth- und API-Abdeckung als „nicht zutreffend, kein Backend“ führen.

### Eingaben
- 85 v1.0-Anforderungen: alle `[x]`, Tabelle „Complete“, alle 85 IDs kommen in `requirements_completed` mindestens einer SUMMARY vor [VERIFIED: Lauf mit `summary-extract`, `comm` ergab 0 fehlende].
- 17 v1.0.1-Anforderungen: 13 Complete (TXT, A11Y, TRI); SEC-01 und AUD-01..03 „Pending“ [VERIFIED: gelesen]. Diese vier belegt der Bericht selbst (D-11), und erst am Ende kann er sie als erfüllt melden.
- Drei SUMMARYs ohne `requirements_completed` (01-01, 04-06, 07-05): Das ist Rauschen und keine Lücke, weil der 3-Quellen-Abgleich je Anforderung läuft (MANU-08 steht in 04-05). Im Bericht erwähnen, damit es niemand als Gap meldet.
- Nyquist (D-09): 04 `status: draft`, `nyquist_compliant: false`, `wave_0_complete: false`; 05 `status: validated`, `nyquist_compliant: false`; 01, 02, 03, 06, 07, 08 `validated`/`true` [VERIFIED: gelesen]. Die Klassifikation laut Workflow ist für 04 NOT-VALIDATED, für 05 PARTIAL.

### Vorab gefundene Audit-Kandidaten (Triage nach D-10)
| # | Kandidat | Beleg | Empfehlung |
|---|----------|-------|-----------|
| 1 | **`08-REVIEW-DISPOSITION.md`: `open: 9`, `total: 10`** (WR-01, WR-02, IN-01 bis IN-07 außer WR-03 fixed). In CONTEXT und STATE nicht genannt | [VERIFIED: gelesen, Frontmatter `open: 9`] | Planung muss das behandeln, sonst meldet der Audit eine offene Review-Lücke, und STATE-Bereinigung wäre unvollständig. Nach D-10: **WR-02** (`DatenTabelle` mit leerer `beschriftung` verliert `tabindex`, Tastaturnutzer erreichen den Scrollbereich nicht, WCAG 2.1.1) ist Barrierefreiheit, aber nur über den Pflichtprop `beschriftung: string` erreichbar (gelesen: Prop-Typ in `DatenTabelle.vue:20`); es gibt rund 30 Aufrufer (per grep gezählt), ob jeder einen nicht leeren Wert übergibt, hat diese Recherche nicht Zeile für Zeile geprüft [ASSUMED]. Vorschlag: mit kleinem Test beheben (Fallback `props.beschriftung.trim() || 'Tabelle'` oder DEV-Fehler). **WR-01** (Tests, die nie rot werden können) ist Testqualität, billig durch reine Funktion zu beheben. IN-01 bis IN-07 sind Test-Nits und Doku, mit Begründung `deferred`. Wird Code geändert, gilt D-15 (`08-VERIFICATION.md` erneuern). Die Entscheidung trifft der Nutzer, siehe Open Question 1 |
| 2 | Nyquist 04/05 | siehe oben | `tech_debt`, Begründung „deferred“ (D-09) |
| 3 | Phase 7 CR-01: Unterschriften auf `app/public/quellen/s009.webp` (öffentliche Satzung, Amtsträger in amtlicher Funktion) | `07-REVIEW-DISPOSITION.md` :121 „deferred … Nutzerentscheidung 2026-10-07“, `REQUIREMENTS.md` Out of Scope | In den Audit als `tech_debt` mit Verweis auf die ausdrückliche Nutzerentscheidung aufnehmen. D-10 zählt Datenschutz zur Kernaussage, die Nutzerentscheidung vom 2026-10-07 hat aber Vorrang und wird nicht neu geöffnet (Open Question 2) |
| 4 | `npm audit`: 4 hohe Funde (`braces`, nur Dev-Werkzeug), Produktion 0 | [VERIFIED: ausgeführt] | `tech_debt`/Hinweis, keine Lücke der Kernaussage; Maßnahme gehört ins Backlog |
| 5 | Phase-5-VERIFICATION `human_needed` im Text | siehe Re-Verification | wird in Welle 2 aufgelöst, danach kein Audit-Befund |
| 6 | Untracked im Arbeitsbaum: `.planning/phases/08-fixes-und-triage/08-PATTERNS.md`, `.planning/state.json`, `.planning/ui-reviews/` | `git status` zu Sitzungsbeginn | Hygiene: entscheiden, ob versioniert werden soll; `.claude/` ist Werkzeug-Installation. Beim Commit nur explizit benannte Pfade stagen (CLAUDE.md) |

### Integration und Flüsse (Vorschlag für den Prompt des Integration-Checkers)
Phasen-Kopplungen (Daten, kein API): `raw_data/haushalt-2026.pdf` → Schritte 01–08 in `alle.py` → `daten/{zwischen,aufbereitet,manuell,pruefberichte}` → `app/src/data/*.json` (`haushalt`, `investitionen`, `produkte`, `stellenplan`, `texte`, `quellen`) → `app/src/data/daten.ts`/`typen.ts` → `app/src/lib/*` → Seiten (`router/index.ts`: `/`, `/einnahmen`, `/ausgaben`, `/produkt/:code`, `/geldfluss`, `/entwicklung`, `/investitionen`, `/rat-entscheidet`, `/stellenplan`, `/glossar`, `/ueber`, Catch-all) → Quellenbelege (`app/public/quellen`, 231 Dateien) → CI/Deploy.
Flüsse: (F1) Zahl auf der Startseite → Quelle anzeigen → Beleg-Seite im PDF; (F2) Ausgaben-Drilldown bis Produktseite und zurück (URL-Parameter `pb`, `jahr`); (F3) Geldfluss/Sankey ↔ Ausgaben; (F4) Glossarbegriff-Link aus Erklärtext → Glossar-Sprung; (F5) Rat-entscheidet/Entwicklung/Investitionen/Stellenplan mit „berechnet“-Kennzeichnung; (F6) Mobiles Menü (Drawer) schließt bei Navigation; (F7) Pipeline-Prüfregeln rot → `alle.py` Exit 1 → CI rot → kein Deploy (`ci.yml` `deploy.needs: [pipeline, app]`). Die Playwright-Specs `app/e2e/{smoke,interaktion,mobil,quelle,kacheln,textliste,inventar}.spec.ts` decken Teile davon ab (89 Tests im Projekt `ci`, grün) und sind die stärkste Evidenz für Flüsse; Lücken benennen.

### Status-Regel
Jede `unsatisfied`-Anforderung erzwingt `gaps_found` (Workflow 5e). Erwartung: `tech_debt` oder `passed`, abhängig von Triage-Ergebnis zu Kandidat 1.

## STATE.md Cleanup (AUD-03)

Ist-Lage der Einträge unter „Blockers/Concerns“ [VERIFIED: STATE.md gelesen und gegen Dateien geprüft]:
| Eintrag | Zutreffend? | Maßnahme |
|---------|-------------|----------|
| `app/node_modules` mit macOS-Binaries, Scratch-Kopie | ja, steht in CLAUDE.md; Scratch-Weg funktioniert (in dieser Sitzung benutzt) | bleibt (D-16) |
| Code-Review-Restbefunde 02-REVIEW.md / 04-REVIEW-DISPOSITION.md | nein, beide `open: 0` (02: total 5, 04: total 9) | entfernen |
| `/gsd-secure-phase 04` steht aus | erledigt nach Welle 1 | entfernen |
| Kein Milestone-Audit / stale | erledigt nach Wellen 2, 4, 5 | entfernen |
| **neu:** `08-REVIEW-DISPOSITION.md` offene Befunde | ja, solange nicht triagiert | nach Triage entfernen oder als echter offener Punkt führen |
Weitere Felder in STATE.md, die nicht in „Blockers/Concerns“ liegen, aber veralten: `status`, `stopped_at`, „Operator Next Steps“, „Deferred Items“ (Tabelle leer; D-09 zurückgestellte Nyquist-Punkte könnten dort stehen). Änderungen am Ende der Phase, per `Edit`.

MILESTONES.md: der Nachtrag steht unter dem v1.0-Abschnitt direkt nach dem „Closeout“-Block, datiert, ohne den historischen Text zu ändern (D-17). REQUIREMENTS.md: in der Tabelle Out of Scope an die Zeile „Deploy-/Gerätecheck aus Phase 7 (Human-Items 07-VERIFICATION)“ den Vermerk „vom Nutzer erledigt, 2026-10-08“ anhängen (D-18). Die Checkboxen SEC-01, AUD-01..03 und die Traceability-Zeilen auf „Complete“ setzen erst am Phasenende.

## Common Pitfalls

### Pitfall 1: Bereits erneuerte VERIFICATION wird durch Phase-9-Codeänderung wieder „stale“
**What goes wrong:** Ein D-04- oder D-10-Fix ändert z. B. `DatenTabelle.vue`; alle Berichte, die diese Datei in `covered_files` führen, fallen zurück auf `stale`.
**Why it happens:** Digest hasht Dateiinhalt (verification.cjs :1380-1455).
**How to avoid:** Digests im Nachlauf nach der letzten Codeänderung berechnen; am Ende `verification.status` für 01 bis 08 prüfen.
**Warning signs:** `verification.status` meldet `stale` direkt nach einem Fix-Commit.

### Pitfall 2: Skip als Beleg
**What goes wrong:** `test_port_wie_format_ts` überspringt sich bei fehlendem `node`/`typescript` und zählt als „passed“-ähnlich grün.
**How to avoid:** `pytest -rs` im Nachweis, null Skips; in der Sandbox sind node und `app/node_modules/typescript/package.json` vorhanden [VERIFIED].

### Pitfall 3: T-04-19 wörtlich nachstellen wollen
**What goes wrong:** Der Plan-Befehl „Diff gegen f9e085d ist leer“ schlägt auf HEAD fehl, obwohl nichts kaputt ist (Phase 5/6/8 haben Texte ergänzt).
**How to avoid:** Nachweis am Commit `52b3d3b`, im Register ausdrücklich „historisch geschlossen“ (siehe Worksheet).

### Pitfall 4: Parallele Läufe von `alle.py`/`pytest` in derselben Arbeitskopie
**What goes wrong:** Mehrere Verifier schreiben gleichzeitig `daten/` und `app/src/data/`; Byte-Gleichheit wird verfälscht, Git-Diff zeigt Phantomänderungen.
**How to avoid:** Ein Basislauf, Verifier arbeiten read-only; `alle.py` nur im Basislauf und im Abschlusslauf.

### Pitfall 5: Namens-Scan-Nadeln decken `meta.json`-Namen nicht ab
**What goes wrong:** T-04-05 wird mit „Scan über `daten/`“ belegt, obwohl die Nadeln nur aus den Personenfeldern der Produktinformationen stammen (`lies_personennamen`, produkte.py:799-830 gelesen), nicht aus der Satzungsseite S. 9.
**How to avoid:** Belege sind die Allowlist (`manuell.py:44`, :114-150) plus `test_meta_json_bricht_ab` (unbekannte Schlüssel brechen ab); der Scan ergänzt nur.

### Pitfall 6: Audit-Workflow ohne Anpassung
**What goes wrong:** Es entsteht `v1.0.1-MILESTONE-AUDIT.md` und nur Phasen 8/9 werden gelesen; `find-phase` hingegen löst Archivordner korrekt auf [VERIFIED: `find-phase 4` liefert `.planning/milestones/v1.0-phases/04-…`].
**How to avoid:** Pfade und Dateinamen im Plan festschreiben (D-07/D-08).

### Pitfall 7: Zeitgrenzen der Werkzeuge
**What goes wrong:** Der volle pytest-Lauf dauert 347 s; das Foreground-Limit der Bash-Werkzeuge liegt bei 600 s.
**How to avoid:** Den vollen Lauf im Hintergrund starten und per Dateiausgabe prüfen; gezielte Auswahl (16 s) für Zwischenstände.

### Pitfall 8: Commit-Hygiene
**What goes wrong:** `git add -A` nimmt `.claude/`-Installationsdateien und die untracked-Planungsdateien mit.
**How to avoid:** Nach CLAUDE.md nur explizit benannte Pfade stagen; Fix-Commits mit Phasenpräfix und ID (`04/T-04-xx`, `09/…`).

## Code Examples

### Stale-Status prüfen (alle acht Phasen)
```bash
# Source: .claude/gsd-core/bin/gsd-tools.cjs (in dieser Sitzung ausgeführt)
G=.claude/gsd-core/bin/gsd-tools.cjs
for d in .planning/milestones/v1.0-phases/*/ .planning/phases/08-fixes-und-triage; do
  echo "$d: $(node $G query verification.status "$d" | grep '"status"')"
done
```

### Fingerprint für den Berichtskopf erzeugen
```bash
# Source: verification.cjs cmdVerificationFingerprint (:1660-1780); Ausgabe ist JSON mit covered_files und covered_digest
node .claude/gsd-core/bin/gsd-tools.cjs query verification.fingerprint \
  .planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten \
  app/src/charts/format.ts pipeline/ostbevern/texte.py   # weitere geprüfte Dateien anhängen
```
Die Phase-Pläne und -Summaries ergänzt das Werkzeug selbst; ein fehlender oder unlesbarer Pfad lässt den ganzen Aufruf scheitern (fail closed).

### Gezielter Evidenzlauf für SEC-01 (16 s, ohne Skips)
```bash
# Source: in dieser Sitzung ausgeführt, 150 passed
cd pipeline && uv run pytest -p no:cacheprovider -rs -q \
  tests/test_formatiere.py tests/test_texte.py \
  "tests/test_app_daten.py::test_keine_personennamen_in_app_daten" \
  "tests/test_app_daten.py::test_app_json_deterministisch" \
  "tests/test_app_daten.py::test_haushalt_json_eingecheckt_aktuell" \
  "tests/test_app_daten.py::test_produkte_json_ohne_personenfelder" \
  "tests/test_app_daten.py::test_unbekannter_platzhalter_bricht_schritt_07_ab" \
  "tests/test_produkte.py::test_keine_personennamen" \
  "tests/test_manuell.py::test_meta_json_gueltig" "tests/test_manuell.py::test_meta_json_bricht_ab" \
  "tests/test_manuell.py::test_toleranz_je_regel" "tests/test_manuell.py::test_eckwerte_ohne_pruefung_bricht_ab" \
  "tests/test_manuell.py::test_regel5_stufe_a_erkennt_tippfehler" \
  "tests/test_pruefung.py::test_regel4_b4_erkennt_tippfehler_in_steuerarten"
```
Für weitere Zeilen (Stellenplan, KL-Knoten, Schuldenstand, befunde) die Namen aus dem Worksheet anhängen.

### Abschlusslauf (identisch zu CLAUDE.md „CI lokal nachstellen“)
```bash
# Pipeline
(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)   # ~6 Minuten, im Hintergrund
uv run --directory pipeline python alle.py --jahr 2026 \
  && git diff --stat --exit-code -- daten app/src/data \
  && test -z "$(git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen)"      # ~30 s
# App in Scratch-Kopie (macOS-Binaries in app/node_modules)
S=<scratchpad>/scratch; mkdir -p $S && tar --exclude=node_modules --exclude=dist --exclude=test-results \
  --exclude=playwright-report -cf - app | tar -xf - -C $S
(cd $S/app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run test && npm run build)
scripts/e2e-wie-ci.sh $S/app                                                                              # ~35 s, Docker
```
Gemessene Basis: ruff beide grün; `alle.py` Exit 0 nach 29 s, Diff leer, `git status` für `daten app/src/data app/public/quellen` leer; App-Schritte je 1–5 s; e2e „89 passed (31.8s)“ [VERIFIED: Läufe dieser Sitzung].

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Stale per Zeitstempel (SUMMARY neuer als VERIFICATION) | Inhalts-Digest `covered_digest`, v3 hasht deklarierte Dateien plus PLAN/SUMMARY der Phase | in gsd-core #4155/#4623/#5095 (Kommentare in `verification.cjs`) | Re-Verifikation heißt: Fingerprint neu erzeugen, nicht Datei anfassen |
| Jahreszahlen im Text als Ausnahme der Ziffernregel | Nur als Platzhalter `{{jahr.…\|jahr}}` | Phase 8 (27e0be7, 7d4be31) | T-04-16 und T-04-18 prüfen den Stand nach der Verschärfung |

**Deprecated/outdated:** Die Beleg-Befehle in `04-06-PLAN.md` (Diff gegen `f9e085d`) sind für den Endstand nicht mehr gültig.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Die Vorabprüfung genügt für „keine Bedrohung offen“; für T-04-06, T-04-09, T-04-13 wurden Code und Tests in dieser Sitzung nur per Grep und Testnamen, nicht Zeile für Zeile gelesen | Threat Evidence Worksheet | Eine der drei kann sich beim Lesen als schwächer als dokumentiert erweisen, dann greift D-04 (Fix mit Test) |
| A2 | `gsd-security-auditor` ist für eine zusätzliche Gegenprüfung geeignet, und `asvs_level: 1` mit L1-Kurzschluss würde reichen, wenn D-01 nicht strenger wäre | Standard Stack, Alternatives | Gering; Entscheidung liegt bei Claude's Discretion |
| A3 | Die Behandlung von Phase 5 `human_needed`-Text (UAT/Playwright als Beleg, Rest als Nutzerbestätigung) entspricht dem Willen des Nutzers; CONTEXT regelt nur Phase 7 (D-14) | Re-Verification Playbook | Der Nutzer könnte für Phase 5 eine eigene Aussage wollen (Open Question 3) |
| A4 | Die vier hohen `npm audit`-Funde sind reine Entwicklungswerkzeuge; geprüft wurde nur `npm audit --omit=dev` (0) | Standard Stack | Gering; Dev-Abhängigkeit läuft nicht im ausgelieferten Bundle |
| A5 | Die Workflow-Dateien `secure-phase.md` und `audit-milestone.md` entsprechen der installierten GSD-Version, die auch `verification.fingerprint` bereitstellt | Playbooks | Gering |

## Open Questions

1. **Was geschieht mit den 9 offenen Befunden in `08-REVIEW-DISPOSITION.md`?**
   - What we know: Frontmatter `open: 9`, `total: 10`; zwei Warnungen (WR-01 Test kann nicht rot werden, WR-02 leere `beschriftung` entfernt `tabindex`), sieben Infos. CONTEXT und STATE nennen das nicht.
   - What's unclear: Ob der Nutzer sie in Phase 9 triagieren will (Phase 8 hat dasselbe für 01/05/06 getan, Muster `fixed | skipped | deferred` mit Begründung).
   - Recommendation: Als eigene kleine Aufgabe vor dem Audit einplanen (Triage mit D-10-Schwelle, WR-02 und WR-01 mit Test beheben, Infos begründet `deferred`), das Ergebnis in den Audit und in STATE übernehmen. Der Nutzer sollte das vor der Planung bestätigen, weil es Code berührt und dadurch D-15 auslöst.

2. **Bleibt Phase-7-CR-01 (Unterschriften auf `s009.webp`) im Audit unverändert zurückgestellt?**
   - What we know: Nutzerentscheidung 2026-10-07 `deferred`; D-10 zählt Datenschutz zur Kernaussage.
   - Recommendation: Als `tech_debt` mit Zitat der Nutzerentscheidung führen, nicht neu öffnen.

3. **Phase 5: Wie werden die zwölf `human_verification`-Einträge und der Widerspruch `passed`/`human_needed` behandelt?**
   - What we know: Nur Phase 7 ist in D-14 geregelt. UAT 05 ist complete; Playwright und axe laufen grün über 11 Routen.
   - Recommendation: Gleiches Prinzip wie D-14: Der Verifier kennzeichnet, was UAT/Nutzer bestätigt hat, und markiert nichts als selbst geprüft, was er nicht prüfen konnte. Falls der Nutzer das anders will, vor Welle 2 klären.

4. **Soll der Basislauf als Datei im Repo (`09-BASISLAUF.md`) oder nur im Scratchpad liegen?**
   - Recommendation: Als kurze Evidenzdatei im Phasenordner, damit VERIFICATION 09 und der Audit darauf verweisen können.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| uv | Pipeline-Läufe | ja | 0.9.26 | — |
| Python (uv-verwaltet) | pytest, alle.py | ja | `pipeline/.python-version`, `uv sync --locked` ohne Änderung | — |
| Node / npm | App-Prüfungen | ja | v22.22.1 / npm erreichbar (`npm view vue version` lieferte 3.5.43) | — |
| `raw_data/haushalt-2026.pdf` | Namens-Tests, alle.py | ja (9.1 MB, in Git getrackt) | — | — |
| Docker | `scripts/e2e-wie-ci.sh` | ja | 29.8.1; Image `mcr.microsoft.com/playwright:v1.63.0-noble` lokal vorhanden | — |
| Schriftpaket `fonts-dejavu-core_2.37-8_all.deb` | e2e | ja, im Cache `~/.cache/ostbevern-money` | SHA-256 vom Skript geprüft | — |
| GitHub-Netz (github.io, Actions-API) | Deploy-Check Phase 7 | nein (Sandbox-Firewall) | — | Nutzerbestätigung (D-14) |

**Missing dependencies with no fallback:** keine.
**Missing dependencies with fallback:** GitHub-Zugriff, ersetzt durch D-14.

## Validation Architecture

(`workflow.nyquist_validation: true` in `.planning/config.json` [VERIFIED: gelesen].)

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (Pipeline, 681 Tests), vitest (App-Einheiten), Playwright + axe (89 Tests im Projekt `ci`) |
| Config file | `pipeline/pyproject.toml` (`testpaths=["tests"]`, `pythonpath=["."]` laut 04-VALIDATION.md), `app/vite.config`/`playwright.config` |
| Quick run command | gezielte Auswahl aus „Code Examples“ (16 s) |
| Full suite command | Abschlusslauf-Block (Pipeline ~6 min, App ~15 s, e2e ~35 s) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SEC-01 | 21 Bedrohungen mit Beleg, Namens-Tests grün ohne Skip | pytest gezielt + Dateiprüfung | gezielter Lauf (siehe Code Examples); `grep -E '^(status\|threats_open\|asvs_level):' …/04-SECURITY.md` | Tests vorhanden; Datei fehlt (Wave 1) |
| AUD-02 | alle acht Phasen nicht stale | Tool | Schleife `verification.status` (Code Examples), erwartet 8× `passed` | Tool vorhanden |
| AUD-03 | STATE.md-Blockers stimmen | Textprüfung | `grep -n "02-REVIEW\|04-REVIEW-DISPOSITION\|secure-phase 04\|Kein Milestone-Audit" .planning/STATE.md` ohne Treffer | vorhanden |
| AUD-01 | Audit-Datei mit Frontmatter und Abdeckung | Dateiprüfung + Tool | `test -f .planning/v1.0-MILESTONE-AUDIT.md`; Frontmatter `status`, `scores`; jede Lücke mit Disposition | Datei fehlt (Wave 4) |
| Querschnitt | byte-identisch, Regeln 1–10 grün, CI-Kette grün | Lauf | Abschlusslauf | vorhanden, Basis grün |

### Sampling Rate
- **Per task commit:** gezielte pytest-Auswahl oder Dateiprüfung des betroffenen Artefakts.
- **Per wave merge:** `verification.status` über alle Phasen; bei Codeänderung zusätzlich volle Pipeline- und App-Kette.
- **Phase gate:** Abschlusslauf vollständig grün vor `/gsd-verify-work`.

### Wave 0 Gaps
None — bestehende Testinfrastruktur deckt alles ab. Falls WR-01/WR-02 aus Open Question 1 behoben werden, entstehen neue vitest-Tests in `app/src/components/__tests__/` bzw. `datenTabelle.ts`.

## Security Domain

`security_enforcement` ist nicht abgeschaltet (Config: `security_enforcement: true`, `security_asvs_level: 1`, `security_block_on: high`) [VERIFIED: `.planning/config.json`].

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | nein | kein Backend, keine Konten |
| V3 Session Management | nein | statische Seite |
| V4 Access Control | nein | öffentliche Daten |
| V5 Input Validation | ja (Phase-4-Gegenstand) | strikte Allowlist-Schreiber, `pruefe_text`, `lies_meta_json`, Hash-Router-Allowlist |
| V6 Cryptography | nein | nur SHA-256-Prüfsumme für Schriftpaket (Fremdwerkzeug) |
| V8/V14 Datenschutz, Lieferkette | ja | Namensscans, Lockfile-Disziplin |

### Known Threat Patterns for diesen Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Falsche Zahl in Bürgerinfo | Tampering | Prüfregeln 1–10, Sollwerte, 1-€-Toleranz |
| Personennamen in ausgelieferten Daten | Information Disclosure | Allowlist-Schlüssel, Namens-Scan, Schwärzung der Beleg-Bilder (Phase 7) |
| Roh-HTML aus Texten | Tampering/XSS | `pruefe_text` plus kein `v-html` |
| Lieferkette | Tampering | Lockfiles, `npm ci`, `uv sync --locked`, gepinnte Actions-SHAs in `ci.yml` |
| Subprozess aus Test | Elevation | Argumentliste ohne Shell, stdin-JSON, kein Netz (T-04-20) |

## Sources

### Primary (HIGH confidence)
- Repo-Dateien dieser Sitzung gelesen: `09-CONTEXT.md`, `STATE.md`, `REQUIREMENTS.md`, `ROADMAP.md` (Phase 9), `MILESTONES.md`, die sechs `04-0N-PLAN.md` (`<threat_model>`), `03-SECURITY.md`, `08-SECURITY.md`, `04-VERIFICATION.md`, `05/06/07-VERIFICATION.md` (Frontmatter), `07-REVIEW-DISPOSITION.md`, `08-REVIEW-DISPOSITION.md`, `08-REVIEW.md`, `texte.py`, `manuell.py`, `stellenplan.py` (Ausschnitte), `format.ts`, `test_formatiere.py`, `ci.yml`, `scripts/e2e-wie-ci.sh`, `app/src/config.ts`
- GSD-Tooling: `.claude/gsd-core/bin/lib/verification.cjs`, `workflows/secure-phase.md`, `workflows/audit-milestone.md`, `agents/gsd-integration-checker.md`
- Ausgeführte Läufe dieser Sitzung (Zahlen oben): pytest voll und gezielt, `alle.py`, ruff, App-Kette in Scratch-Kopie, `scripts/e2e-wie-ci.sh`, `verification.status`/`fingerprint`, `init.phase-op`, `init.milestone-op`, `summary-extract`, `npm audit`

### Secondary (MEDIUM confidence)
- Erwartete Audit-Inhalte (Flüsse, Triage) leiten sich aus gelesenen Verifikationsberichten ab, nicht aus dem noch nicht geschriebenen Audit

### Tertiary (LOW confidence)
- keine

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Werkzeuge ausgeführt, Versionen gemessen
- Architecture/Wellen: HIGH — durch D-11/D-12 und die Digest-Mechanik begründet
- Pitfalls: HIGH für Digest-, Skip-, T-04-19-Falle (alle ausgeführt oder gelesen); MEDIUM für Audit-Kandidaten
- Threat-Startpunkte: MEDIUM — Executor liest jede Stelle neu (A1)

**Research date:** 2026-10-08
**Valid until:** 2026-11-07 (Repo-Stand ändert sich nur durch Phase-9-Arbeit; bei Codeänderungen in Phase 9 die Zeilenangaben neu prüfen)
