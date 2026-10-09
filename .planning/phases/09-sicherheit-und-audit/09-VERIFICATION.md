---
phase: 09-sicherheit-und-audit
verified: 2026-10-09T10:05:00Z
status: gaps_found
score: 5/6 must-haves verified
covered_files:
  - ".planning/MILESTONES.md"
  - ".planning/REQUIREMENTS.md"
  - ".planning/STATE.md"
  - ".planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-01-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-01-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-02-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-02-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-03-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-03-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-04-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-04-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-05-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-05-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-06-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-06-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-07-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-07-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-08-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-08-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-09-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-09-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-10-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-10-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-11-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-11-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-12-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-12-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-13-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-13-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-14-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-14-SUMMARY.md"
  - ".planning/phases/09-sicherheit-und-audit/09-15-PLAN.md"
  - ".planning/phases/09-sicherheit-und-audit/09-15-SUMMARY.md"
  - ".planning/v1.0-MILESTONE-AUDIT.md"
  - "app/src/components/DatenTabelle.vue"
  - "app/src/components/ErklaerText.vue"
  - "app/src/components/KreisumlageCallout.vue"
  - "app/src/components/__tests__/erklaertext.test.ts"
  - "app/src/components/__tests__/zustaende.test.ts"
  - "app/src/components/datenTabelle.ts"
  - "app/src/lib/__tests__/geldfluss.test.ts"
  - "app/src/lib/__tests__/hilfsfunktionen.test.ts"
  - "app/src/lib/__tests__/kreisumlage.test.ts"
  - "app/src/lib/geldfluss.ts"
  - "app/src/lib/hilfsfunktionen.ts"
  - "app/src/lib/kreisumlage.ts"
  - "app/src/pages/AusgabenPage.vue"
covered_digest: "v3:sha256:94a0084573bfff9a53674144a7d35f3ddf5ee4d8743c77a47cb41d36b5f1295d"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "Die Berichte dieser Phase (Audit, erneuerte 08-VERIFICATION, Übergabe an den Nutzer) nennen nur echte offene Punkte und beschreiben den Endstand (Phasenziel, AUD-01, AUD-03-Geist)"
    status: failed
    reason: "08-UAT.md steht seit 2026-10-08 (dd77df1, 20:36 +0200, vor dem Start von Phase 9) auf status: complete, Test 1 result: pass, pending: 0. Phase 9 führt den Screenreader-Check zu A11Y-03 trotzdem als offen (Test 1 pending), an neun Stellen."
    artifacts:
      - path: ".planning/v1.0-MILESTONE-AUDIT.md"
        issue: "gaps.requirements A11Y-03 partial (Z. 47-53), Phasentabelle Phase 8 (Z. 152), Anforderungszeile v1.0.1 A11Y-03 partial (Z. 297), Lückenliste G-09-11 (Z. 392), Tech Debt Phase 8 (Z. 445): alle behaupten 08-UAT Test 1 pending. Folgefehler: scores.requirements 97/102 müsste 98/102 lauten, fünf partial-Zeilen werden vier."
      - path: ".planning/phases/08-fixes-und-triage/08-VERIFICATION.md"
        issue: "Frontmatter status: passed, aber human_verification enthält den A11Y-03-Punkt mit 'result pending'; die Kopfzeile sagt 'passed (… bleibt ein offener menschlicher Check)', der Abschnitt Gaps Summary sagt 'Der Status ist human_needed'. Gleicher Widerspruch, den Phase 9 für 05 und 07 beseitigen sollte (D-14, D-21). Außerdem steht im Abschnitt 'Offene Punkte' noch die Steuergruppen-Frage, die G-09-03 (448e43d) inzwischen behoben hat."
      - path: ".planning/MILESTONES.md"
        issue: "Nachtrag nennt '97 von 102 Anforderungen ohne Vorbehalt, die übrigen fünf mit … Screenreader-Belegen' (folgt aus dem Audit-Fehler)"
      - path: ".planning/phases/09-sicherheit-und-audit/09-15-SUMMARY.md"
        issue: "Übergabe an den Nutzer nennt G-09-11 (Screenreader-Check in 08-UAT.md) als nächsten Schritt, obwohl der Nutzer ihn bestanden hat; STATE.md sagt dazu selbst 'Screenreader-UAT bestanden'"
    missing:
      - "Audit: A11Y-03 (v1.0.1) auf satisfied (Beleg 08-UAT.md Test 1 pass, 2026-10-08), G-09-11 auf closed/fixed, Tech-Debt-Zeile Phase 8 und gaps.requirements-Eintrag entfernen, scores.requirements 98/102, Phasentabelle Phase 8 anpassen, MILESTONES-Nachtrag auf '98 von 102 … vier' anpassen"
      - "08-VERIFICATION.md: human_verification-Eintrag mit beleg 'UAT 08 Test 1 (pass, Nutzer, 2026-10-08)' kennzeichnen oder entfernen, Status in Frontmatter, Kopfzeile und Gaps Summary vereinheitlichen, Nachtrag zur behobenen Steuergruppen-Frage; danach verification.fingerprint neu schreiben"
      - "09-15-SUMMARY.md: Hinweis an den Nutzer streichen"
deferred: []
advisory:
  - finding: "09-REVIEW.md WR-01: istGroessterEinzelposten wirft bei fehlenden Daten (kreisumlage null) statt auf die neutrale Fassung zurückzufallen. Heute kein Datenfall (haushalt.json: kreisumlage werte in allen sechs Jahren nicht null)."
    category: other
    reason: "Latenter Defekt in einem Fix aus 09-14, im Ledger 09-REVIEW-DISPOSITION.md auf open; wirkt erst bei einem Jahrgang ohne Kreisumlagewert"
    evidence_status: "Code und Daten gelesen, Datenlage geprüft (node), kein Test"
  - finding: "09-REVIEW.md WR-02: seitenText gibt Seitenlisten ungeordnet aus. texte.json hat quelle_seiten [51, 8] (texte.5, glossar.15) und [24, 9, 311] (texte.6); Bürger sehen 'PDF-Seiten 51, 8'."
    category: other
    reason: "Von mir an den Daten nachgezählt (node). Die Reihenfolge war vor 09-14 gleich ('PDF-Seite 51, 8'), also keine Regression, aber ein sichtbar auffälliger Seitenverweis; Ledger open"
    evidence_status: "deterministisch belegt (Daten), kein Test"
  - finding: "G-09-01 steht auf fixed, aber der gleiche Superlativ steht weiter handgeschrieben in daten/manuell/texte/erklaerungen.md (Z. 16, 19: 'der größte Ausgabenposten'). Der Fix betrifft nur KreisumlageCallout.vue."
    category: other
    reason: "Die Aussage stimmt in allen sechs Jahren der Daten (Audit-Check), ist aber nicht aus Daten abgeleitet; die Lückenzeile nennt den Text als Fundstelle, der Fix deckt ihn nicht"
    evidence_status: "grep, Audit-Zeile G-09-01"
  - finding: "Berichte 01, 02, 03, 04, 07 sagen weiter 'seit dem Kopf des Basislaufs 1d0df35 hat sich kein Codepfad geändert (git diff --quiet … Exit 0)'. Seit 09-14 stimmt das nicht mehr (git diff --quiet 1d0df35 HEAD -- pipeline app … endet mit Exit 1)."
    category: other
    reason: "Ihre covered_digest-Werte stimmen weiter (ich habe alle acht mit verification.fingerprint neu berechnet), die geänderten Dateien gehören nicht zu ihren covered_files; nur der Satz ist überholt"
    evidence_status: "git diff und Fingerprint-Lauf"
human_verification: []
---

# Phase 9: Sicherheit und Audit Verification Report

**Phase Goal:** Phase 4 (manuelle Daten und App-Daten) ist wie alle anderen v1.0-Phasen nachweislich sicherheitsgeprüft, v1.0 ist nachträglich auditiert, die Verifikationen aller sieben v1.0-Phasen beschreiben den Endstand nach den Restpunkten, und STATE.md nennt nur noch echte offene Punkte. Reihenfolge: zuerst die Sicherheitsprüfung von Phase 4 gegen den Code nach Phase 8, zuletzt Audit und Re-Verifikation gegen den Endstand.
**Verified:** 2026-10-09T10:05:00Z
**Status:** gaps_found
**Re-verification:** Nein, erste Verifikation der Phase

Die Phase erreicht ihr Ziel in der Sache: 04-SECURITY.md, Audit, die sieben erneuerten Berichte und die Blocker-Liste sind vorhanden und stimmen mit dem Code überein, und die Querschnittsbedingung hält (von mir selbst nachgemessen). Es bleibt ein Dokumentationsfehler in den Berichten dieser Phase: Sie führen einen Screenreader-Check als offen, den der Nutzer schon bestanden hat. Er ändert keine Zahl und keinen Text der App, widerspricht aber dem Teil des Ziels „nur noch echte offene Punkte“ und verfälscht die Scores des Audits. Die Korrektur ist klein.

Vorgehen: SUMMARY-Aussagen wurden nicht übernommen. Ich habe Code, Tests, Digests und Läufe selbst geprüft. Playwright habe ich nicht erneut gestartet (kein Docker in der Sandbox); die Playwright-Zahlen (ci 89, mobil 41) stammen aus 09-BASISLAUF.md und dem Abschlusslauf des Audits.

## Goal Achievement

### Observable Truths

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | SC 1 / SEC-01: `04-SECURITY.md` mit `status: verified`, `threats_open: 0`, `asvs_level: 1`, Aufbau wie die anderen Dateien, 21 Bedrohungen (T-04-01…T-04-20, T-04-SC) geschlossen mit Beleg im aktuellen Code oder als accepted mit Begründung; Namens-Tests laufen grün | ✓ VERIFIED | Datei vorhanden, Frontmatter wie verlangt, Abschnitte Trust Boundaries, Threat Register (21 Zeilen, alle `closed`), Accepted Risks Log (AR-04-01, AR-04-02), Audit Trail, Sign-Off. **Zitierte Codestellen** habe ich selbst gelesen: über 60 `datei:zeile`-Angaben (z. B. `pruefung.py:1412/870/484/277/85/92`, `app_daten.py:417/486/232/552`, `manuell.py:28/44/114/140`, `stellenplan.py:40/47/51/338`, `texte.py:35/45/51/220/245/254`, `format.ts:92/141/169`, `ci.yml:39/46-52/85`): alle treffen die genannte Funktion bzw. Konstante. **Alle 52 Testnamen** der Datei existieren in `pytest --collect-only`; die 49 Funktionsnamen (ohne die drei Dateinamen) liefen bei mir mit `-rs`: **73 passed, 0 skipped**, darunter `test_keine_personennamen_in_app_daten`, `test_keine_personennamen`, `test_meta_json_gueltig`, `test_meta_json_bricht_ab`, `test_port_wie_format_ts` (lief, nicht übersprungen). **Historische Schließungen:** T-04-19: Nach dem Ersetzen von `\|jahr}}` durch `\|zahl}}` sind `erklaerungen.md` und `texte.json` bei 52b3d3b und f9e085d identisch (`diff` leer, beide Dateien). T-04-SC: `git log 3973d86..7f605fd -- pipeline/pyproject.toml pipeline/uv.lock app/package.json app/package-lock.json` ist leer. Alle 18 zitierten Commit-Hashes existieren. Vitest-Titel `erkennt die Roh-HTML-Direktive` und `enthält keine getippte Zahl und keine Roh-HTML-Direktive` stehen in `quelltext.test.ts:149/219`. Keine Bedrohung war offen, also kein Fix nötig (D-04) |
| 2 | SC 2 / AUD-01: `.planning/v1.0-MILESTONE-AUDIT.md` deckt Anforderungen, Phasen-Integration und End-to-End-Flüsse ab; jede gemeldete Lücke ist geschlossen oder mit Begründung zurückgestellt | ✓ VERIFIED (mit Genauigkeitsmangel, siehe Truth 6) | Datei vorhanden (520 Zeilen), Abschnitte Eingaben, Phasen, Anforderungen (102 Zeilen = 85 + 17, keine `unsatisfied`/`orphaned`), Nyquist, Integration (8/8 Glieder mit Datei:Zeile und Lauf), End-to-End-Flüsse F1–F7 (4 complete, 3 partial, mit Playwright-Titeln), Lückenliste G-09-01…G-09-23, Tech Debt, Abschlusslauf. Kein `fix` mehr offen. **Drei Kernaussage-Lücken behoben mit Test-vor-Fix:** 3f944a7 (rot) → f8aef3f, 74fed1c (rot) → ce5880e, b3b2658 (rot) → 448e43d; ich habe `f8aef3f` im Diff gelesen (`istGroessterEinzelposten`, neutraler Satz als Fallback). Status `tech_debt` entspricht der Workflowregel (nur `unsatisfied` erzwingt `gaps_found`, `partial` nicht). Keine zweite Audit-Datei für v1.0.1, kein Verschieben von Phasenverzeichnissen (`git diff 86c56dc HEAD` zeigt in `v1.0-phases` nur Verifikationen und 04-SECURITY.md) |
| 3 | SC 3 / AUD-02: Die `*-VERIFICATION.md` der Phasen 1–7 sind gegen den Endstand erneuert, keine meldet „stale“; Human-Items aus 07 bleiben als Aufgabe des Nutzers ausgewiesen und gelten nicht als bestanden | ✓ VERIFIED | `verification.status` für 01–04, 06, 07 = `passed`, für 05 = `human_needed`, für 08 = `passed`; keiner `stale`. **Digests unabhängig neu berechnet:** für alle acht Verzeichnisse gibt `verification.fingerprint` mit den eingetragenen `covered_files` exakt den eingetragenen `covered_digest` zurück (01, 02, 03, 04, 05, 06, 07, 08). Jeder Bericht hat einen `re_verification`-Block mit `previous_status`/`previous_score`; Frontmatter-Status und Body-Status stimmen in 01–07 überein; `behavior_unverified` = Anzahl der Items (05: 5/5, sonst 0/0); alle geforderten Anforderungs-IDs je Phase (6+10+7+14+23+15+10) stehen als Zeile in der jeweiligen Tabelle; alle sieben zitieren 09-BASISLAUF.md (`head` = 40-stelliger Hash). 05: jedes Human-Item trägt `beleg` und `verifier_geprueft`, Nutzer-/UAT-Belege sind nicht als Verifier-geprüft ausgegeben, Status `human_needed` mit genau den offenen Punkten. 07: beide Items stehen mit `beleg: vom Nutzer bestätigt (2026-10-08), nicht vom Verifier geprüft`, Score-Text trennt 4/5 Verifier und 1/5 Nutzer, CR-01 als deferred (D-22). Status `passed` für 07 folgt der gesperrten Entscheidung D-14 des Nutzers, nicht dem Standardentscheidungsbaum (dort wäre es `human_needed`); das ist dokumentiert |
| 4 | SC 4 / AUD-03: „Blockers/Concerns“ in STATE.md stimmt mit der Wirklichkeit überein; veraltete Einträge entfernt | ✓ VERIFIED | `STATE.md` Abschnitt Blockers/Concerns enthält nur noch die Scratch-Kopie-Notiz zu `app/node_modules` (trifft zu: macOS-Binaries, ich habe in einer Scratch-Kopie mit eigenem `npm ci` gearbeitet). Die Einträge zu 02-REVIEW/04-REVIEW-DISPOSITION, `/gsd-secure-phase 04` und „Kein Milestone-Audit / stale“ sind weg und jeweils durch Belege gedeckt (Ledger auf `open: 0`, 04-SECURITY.md `threats_open: 0`, `verification.status` nicht stale). REQUIREMENTS.md hält den Out-of-Scope-Vermerk „vom Nutzer erledigt, 2026-10-08“. Hinweis: das übrige STATE.md (Frontmatter `status: executing`, 44 %, „Plan 1 of 15“, „Operator Next Steps: Phase 9 planen“) ist Tracking-Stand und wird vom Orchestrator beim Phasenabschluss gesetzt, nicht Teil von AUD-03 |
| 5 | SC 5: Querschnittsbedingung auf dem Endstand: `alle.py --jahr 2026` byte-identisch, Prüfregeln 1–10 grün, CI-Kette von Pipeline und App grün | ✓ VERIFIED | **Selbst gemessen** (Scratch-Kopie von `git archive HEAD`, eigenes `git init`): `alle.py --jahr 2026` Exit 0, Regeln 1–10 grün (6593/7994/114/259/150/1964/1152/820/12/19 Werte), „Veraltete Befunde: 0“, danach `git diff --exit-code -- daten app/src/data` leer und `git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen` leer. Volles `pytest -rs`: **681 passed, 0 skipped**. App in Scratch-Kopie mit `npm ci`: `type-check` Exit 0, `lint` ohne Meldung, `format:check` sauber, vitest **2207 passed in 51 Dateien**, `build-only` erfolgreich (nur Chunk-Hinweise). Codepfade zwischen Abschluss-Lauf-Head 109cfac und HEAD unverändert (`git diff --stat 109cfac HEAD -- pipeline app daten scripts .github` leer). **Nicht selbst wiederholt:** ruff (vom Audit dokumentiert) und Playwright ci/mobil (Docker nötig); diese Zahlen übernehme ich aus 09-BASISLAUF.md und dem Audit-Abschnitt Abschlusslauf, dort mit Befehl und Exit dokumentiert |
| 6 | Abgeleitet aus Phasenziel („nur noch echte offene Punkte“) und AUD-01: Audit, erneuerte 08-VERIFICATION und Übergabe nennen nur Punkte, die wirklich offen sind | ✗ FAILED | `08-UAT.md`: `status: complete`, `updated: 2026-10-08T18:36:09Z`, Test 1 (Screenreader-Ansage, A11Y-03) `result: pass`, `pending: 0` (Commit dd77df1, 2026-10-08 20:36 +0200, einen Tag vor dem Audit). Audit, 08-VERIFICATION, 09-02-SUMMARY, 09-15-SUMMARY und MILESTONES-Nachtrag führen ihn weiter als „pending/offen“. Details im Abschnitt Gaps Summary |

**Score:** 5/6 Truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md` | Register mit 21 Bedrohungen, `threats_open: 0` | ✓ VERIFIED | siehe Truth 1; Aufbau (Frontmatter, fünf Abschnitte) wie `01-SECURITY.md` |
| `.planning/v1.0-MILESTONE-AUDIT.md` | Audit mit Anforderungen, Integration, Flüsse, Lückenliste, Abschlusslauf | ✓ VERIFIED (mit Mangel aus Truth 6) | enthält `## Lückenliste (D-10)` und `## Abschlusslauf` |
| `.planning/milestones/v1.0-phases/0[1-7]-*/0?-VERIFICATION.md` | sieben erneuerte Berichte | ✓ VERIFIED | siehe Truth 3 |
| `.planning/phases/08-fixes-und-triage/08-VERIFICATION.md` und `08-REVIEW-DISPOSITION.md` | erneuert nach D-20, Ledger `open: 0` | ⚠️ PARTIAL | Digest und Status stimmen, Ledger auf `open: 0`; der Bericht enthält aber den Widerspruch aus Truth 6 |
| `app/src/components/datenTabelle.ts` (`tabellenRahmen`) und `DatenTabelle.vue` | D-20-Fix 08/WR-01, 08/WR-02 | ✓ VERIFIED | Fix 78744d4, Test 8b4ae20 (rot); vitest-Suite grün |
| `.planning/phases/09-sicherheit-und-audit/09-BASISLAUF.md` | gepinnte Laufevidenz | ✓ VERIFIED | `head` 40-stellig, von allen sieben Berichten zitiert |
| `.planning/STATE.md`, `.planning/REQUIREMENTS.md`, `.planning/MILESTONES.md` | Blocker-Liste, Häkchen, Nachtrag | ✓ VERIFIED | SEC-01, AUD-01, AUD-02, AUD-03 `[x]` und `Complete`; Nachtrag unter v1.0 mit historischem Text unverändert |

### Key Link Verification

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| 04-SECURITY.md | `pipeline/tests/test_app_daten.py` u. a. | Testnamen in den Mitigation-Zellen | WIRED | alle Namen gesammelt und gelaufen (73 passed) |
| 04-SECURITY.md | `pipeline/ostbevern/texte.py` | `texte.py:NNN` | WIRED | alle zitierten Zeilen treffen |
| 0?-VERIFICATION.md (1–7) | 09-BASISLAUF.md | Abschnitt Live-Evidenz | WIRED | `grep -c` ≥ 3 in jedem Bericht |
| MILESTONES.md | v1.0-MILESTONE-AUDIT.md | Nachtrag nennt die Datei | WIRED | |
| Audit-Lückenliste | git-Historie | `09/G-09-NN` in Commit-Betreffen | WIRED | 6 Commits (3 Test rot, 3 Fix) |
| Audit/08-VERIFICATION | 08-UAT.md | Aussage „Test 1 pending“ | NOT_WIRED / widersprüchlich | die Quelle sagt `pass` |

### Data-Flow Trace (Level 4)

Nicht anwendbar für die Dokumentartefakte. Für die drei Fix-Komponenten (`KreisumlageCallout.vue`, `ErklaerText.vue`, `AusgabenPage.vue`) fließen die Werte aus `haushalt.json`/`texte.json` über `istGroessterEinzelposten`, `seitenText` bzw. `berechnet`; Tests laufen grün. Siehe Advisory zu WR-01/WR-02.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| Namens- und Sicherheitstests aus 04-SECURITY.md | `pytest -rs -k "<49 Namen>"` | 73 passed, 0 skipped | ✓ PASS |
| Volle Pipeline-Suite | `uv run pytest -rs -q` | 681 passed | ✓ PASS |
| Reproduzierbarkeit | `alle.py --jahr 2026` in Scratch-Repo, `git diff`/`git status` | Exit 0, leer | ✓ PASS |
| App-Suite | `npm run test` (Scratch) | 2207 passed | ✓ PASS |
| Digests der acht Berichte | `verification.fingerprint` je Verzeichnis | alle gleich den eingetragenen | ✓ PASS |
| Playwright ci/mobil | nicht ausgeführt (kein Docker) | — | ? SKIP (aus Basislauf/Audit übernommen) |

### Probe Execution

Step 7c: übersprungen. Die Phase deklariert keine `probe-*.sh`; `find scripts -path '*/tests/probe-*.sh'` wurde nicht benötigt, die Verifikation der Phase stützt sich auf pytest, vitest und die Läufe oben.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
| ----------- | ----------- | ----------- | ------ | -------- |
| SEC-01 | 09-01, 09-15 | `04-SECURITY.md` mit `threats_open: 0` | ✓ SATISFIED | Truth 1 |
| AUD-01 | 09-02, 09-12, 09-13, 09-14, 09-15 | Milestone-Audit v1.0 durchgeführt, Lücken geschlossen oder begründet zurückgestellt | ✓ SATISFIED (mit Genauigkeitsmangel, Truth 6) | Truth 2 |
| AUD-02 | 09-03 bis 09-10, 09-15 | Verifikationen der Phasen 1–7 erneuert, keine „stale“ | ✓ SATISFIED | Truth 3 |
| AUD-03 | 09-02, 09-11, 09-15 | Blockers/Concerns in STATE.md stimmt | ✓ SATISFIED | Truth 4 |

Alle vier Phasen-IDs (SEC-01, AUD-01, AUD-02, AUD-03) stehen in PLAN-Frontmatter, in `REQUIREMENTS.md` (Zeilen `[x]`, Traceability `Phase 9 / Complete`) und in der ROADMAP. Keine verwaisten Anforderungen für Phase 9 (die Tabelle ordnet genau diese vier Phase 9 zu). 09-02 führt AUD-01 und AUD-03 im Frontmatter (D-20-Fix und Ledger 08); das ist plausibel, weil das Ledger die Voraussetzung für ein ehrliches Audit ist.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| `app/src/lib/kreisumlage.ts` | 88-141 | Fallback wirft bei fehlenden Daten (09-REVIEW WR-01) | ⚠️ Warning | latent, kein Datenfall 2024–2029 |
| `app/src/lib/hilfsfunktionen.ts` | 25-34 | `seitenText` ungeordnet (09-REVIEW WR-02), Daten mit `[51, 8]` | ⚠️ Warning | sichtbar auffälliger Seitenverweis, keine Regression |
| 8 Codedateien der Fixes (`datenTabelle.ts`, `DatenTabelle.vue`, `KreisumlageCallout.vue`, `ErklaerText.vue`, `kreisumlage.ts`, `hilfsfunktionen.ts`, `geldfluss.ts`, `AusgabenPage.vue`) | — | `TBD`/`FIXME`/`XXX`/`TODO`/`HACK` | ℹ️ Info | grep ohne Treffer, kein Debt-Marker-Blocker |

### Human Verification Required

Keine. Der Gerätecheck/Deploy (Phase 7) und der Screenreader-Check (A11Y-03) sind Sache der Phasen 7 und 8, nicht Wahrheiten dieser Phase; der Screenreader-Check ist laut `08-UAT.md` bereits bestanden.

### Gaps Summary

**Eine Lücke, rein dokumentarisch (Truth 6).** `08-UAT.md` (Nutzer, 2026-10-08, `result: pass`, `pending: 0`) hat den Screenreader-Check zu A11Y-03 bereits abgeschlossen. STATE.md hält das selbst fest („Screenreader-UAT bestanden“). Phase 9 hat es trotzdem aus dem Text von `08-VERIFICATION.md` (Frontmatter `human_verification`, „result pending“) übernommen und daraus im Audit eine `partial`-Anforderung (A11Y-03 v1.0.1), die Lückenzeile G-09-11, einen Tech-Debt-Eintrag, den Score 97/102 und die Aufgabe an den Nutzer in `09-15-SUMMARY.md` gemacht. `08-VERIFICATION.md` widerspricht sich dabei selbst (Frontmatter `passed`, Gaps Summary „Status ist human_needed“) und führt die Steuergruppen-Frage weiter als offen, obwohl G-09-03 sie behoben hat.

Der Fehler ist konservativ (er meldet zu viel offen, versteckt nichts) und verändert keine Zahl und keinen Text der App. Er verfehlt aber das Ziel „nur echte offene Punkte“ und macht den Audit-Score falsch. Zwei Wege: (a) die vier Dokumente korrigieren, `verification.fingerprint` für Phase 8 neu schreiben, oder (b) den Mangel bewusst als Tech Debt akzeptieren. Meine Empfehlung ist (a), der Aufwand ist klein.

**Nicht blockierend, offen im Ledger `09-REVIEW-DISPOSITION.md` (6 × open):** WR-01 (Wurf statt Fallback), WR-02 (ungeordnete Seitenliste, an den Daten bestätigt), WR-03 (Quellenseiten des Superlativs), IN-01 bis IN-03. Sie sind Advisory, keine Verfehlung eines Phasen-Erfolgskriteriums. WR-02 würde ich vor dem Meilensteinabschluss ansehen, weil Bürger „PDF-Seiten 51, 8“ lesen.

Positiv festzuhalten: Die Phase hat nichts an Prüfregeln, Toleranz oder Daten geschwächt (`alle.py` byte-identisch bei mir), keine archivierte Historie umgeschrieben (`v1.0-ROADMAP.md`, `RETROSPECTIVE.md` unverändert, MILESTONES nur um einen datierten Nachtrag ergänzt) und den Meilenstein v1.0.1 nicht abgeschlossen (D-19; ROADMAP führt ihn weiter in Arbeit).

---

_Verified: 2026-10-09T10:05:00Z_
_Verifier: Claude (gsd-verifier)_
