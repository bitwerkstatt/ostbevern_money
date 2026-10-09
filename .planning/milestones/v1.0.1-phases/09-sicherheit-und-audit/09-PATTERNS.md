# Phase 9: Sicherheit und Audit - Pattern Map

**Mapped:** 2026-10-09
**Files analyzed:** 17 (3 Code/Test, 14 Planungsartefakte)
**Analogs found:** 17 / 17

Alle Analogpfade sind git-tracked (`.planning/...`, `app/src/...`). Keine Mirror-Pfade.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md` (neu) | security-doc | batch (Register + Testbelege) | `.planning/milestones/v1.0-phases/02-kernzahlen/02-SECURITY.md` (Frontmatter, Audit Trail), `.planning/phases/08-fixes-und-triage/08-SECURITY.md` (Register-Spalten, Accepted Risks, Sign-Off) | exact |
| `.../v1.0-phases/0{1..7}-*/0?-VERIFICATION.md` (erneuern) | verification-doc | batch | `02-kernzahlen/02-VERIFICATION.md`, `07-feinschliff-und-ver-ffentlichung/07-VERIFICATION.md` (`re_verification`-Block) | exact |
| `.../07-VERIFICATION.md` (Widerspruch passed/human_needed, D-14) | verification-doc | batch | selbst (Frontmatter Z. 1-53) plus `human_verification`-Block ab Z. 54 | exact |
| `.../05-VERIFICATION.md` (D-21) | verification-doc | batch | `07-VERIFICATION.md` (Nutzerbestätigung kennzeichnen) | role-match |
| `.planning/phases/08-fixes-und-triage/08-VERIFICATION.md` (nur bei Codeänderung, D-15) | verification-doc | batch | `02-VERIFICATION.md` (Re-Verification-Begründung + Live-Lauf) | exact |
| `.planning/phases/08-fixes-und-triage/08-REVIEW-DISPOSITION.md` (D-20) | review-ledger | CRUD | `.../04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md` (`open: 0`, `fixed`) | exact |
| `.planning/v1.0-MILESTONE-AUDIT.md` (neu) | audit-doc | batch | Schema in `.claude/gsd-core/workflows/audit-milestone.md`; kein Vorgänger im Repo | no analog (Workflow-Schema) |
| `.planning/STATE.md` (Blockers/Concerns, AUD-03) | state | CRUD | selbst | exact |
| `.planning/MILESTONES.md` (Nachtrag, D-17) | doc | CRUD | Abschnitt v1.0 Closeout | exact |
| `.planning/REQUIREMENTS.md` (Vermerk D-18, SEC/AUD-Status) | doc | CRUD | selbst | exact |
| `.planning/phases/09-sicherheit-und-audit/09-BASISLAUF.md` (D-23) | evidence-doc | batch | Live-Verification-Abschnitt in `02-VERIFICATION.md` | role-match |
| `app/src/components/datenTabelle.ts` (08/WR-01 Fix: reine Funktion) | utility | transform | selbst, `rahmenAttribute` (Z. 41-49) | exact |
| `app/src/components/DatenTabelle.vue` (08/WR-02 Fix) | component | request-response | selbst, Z. 127-144 | exact |
| `app/src/components/__tests__/zustaende.test.ts` (WR-01/02 Tests) | test | request-response | selbst, Block `rahmenAttribute` Z. 207-219 | exact |
| `app/src/lib/__tests__/quelltext.test.ts` (Regex-Tests ersetzen, IN-01 deferred oder mit WR-01) | test | transform | selbst Z. 225-250 | exact |
| conditional D-04 Threat-Fix | pipeline/test | n/a | je Bedrohung, `pipeline/tests/test_*.py` | n/a |

## Pattern Assignments

### `04-SECURITY.md` (security-doc)

**Frontmatter** (Vorlage `02-SECURITY.md` Z. 1-11; 08-SECURITY nutzt dieselben Felder ohne `block_on`):
```yaml
---
phase: "4"
slug: "manuelle-daten-und-app-daten"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-10-09"
---
```
Abschnitte in dieser Reihenfolge (08-SECURITY): `## Trust Boundaries` (Boundary | Description | Data Crossing), `## Threat Register`, `## Accepted Risks Log`, `## Security Audit Trail`, `## Sign-Off`.

**Register-Zeile** (08-SECURITY Z. 28-47). Spalten: `Threat ID | Category | Component | Severity | Disposition | Mitigation | Status`. Nach D-01 muss die Mitigation-Zelle `Datei:Zeile` im aktuellen Code plus Testname nennen, Quelle der 21 Bedrohungen sind die `<threat_model>`-Tabellen in `04-0{1..6}-PLAN.md` (Beispiel `04-02-PLAN.md` ab Z. 313). Vermerk bei Phase-8-Änderungen (T-04-16, T-04-18) mit Commit-Verweis. T-04-SC einmal führen.
```markdown
| T-04-16 | Tampering | `pruefe_text` Ziffernregel | medium | mitigate | `pipeline/ostbevern/texte.py:<Z>`; `test_texte.py::<name>` grün; Phase 8 verschärft (Commit <hash>) | closed |
```

**Accepted Risks** (08-SECURITY Z. 60-64): Tabelle `Risk ID | Threat Ref | Rationale | Accepted By | Date` mit AR-04-01 (T-04-11) und AR-04-02 (T-04-20); Schlusszeile `*Accepted risks do not resurface in future audit runs.*`.

**Audit Trail** (08-SECURITY Z. 66-70, 02-SECURITY Z. 69-73):
```markdown
| Audit Date | Threats Total | Closed | Open | Run By |
| 2026-10-09 | 21 | 21 | 0 | secure-phase 04 (...) |
```
Sign-Off-Checkboxen wie 08-SECURITY. Nicht-blockierende Anmerkung als `**Audit note (non-blocking):**` (02-SECURITY Z. 75).

Tests, die laufen und nicht skippen müssen (D-05): `pipeline/tests/test_app_daten.py::test_keine_personennamen_in_app_daten`, `test_produkte.py:198 test_keine_personennamen`, `test_manuell.py:471,517`. Lauf mit `-rs` und prüfen, dass 0 Skips auftreten.

---

### `0?-VERIFICATION.md` Re-Verifikation (verification-doc)

**Analog:** `02-VERIFICATION.md` (Z. 1-20) und `07-VERIFICATION.md` (Z. 1-53).

Frontmatter-Felder: `phase`, `verified`, `status`, `score`, `covered_files` (alle PLAN/SUMMARY plus Code), `covered_digest`, `behavior_unverified`, `overrides_applied`, `re_verification`:
```yaml
re_verification:
  previous_status: passed
  previous_score: "5/5 ..."
  gaps_closed: []
  gaps_remaining: []
  regressions: []
gaps: []
deferred: []
advisory: []
behavior_unverified_items: []
human_verification:
  - test: "..."
```
Textstruktur aus 02-VERIFICATION: `# Phase N: ... Verification Report`, Goal/Verified/Status/Re-Verification, `## Why This Re-Verification Was Needed`, Diff-Inspektion, `### Live Verification (this session, HEAD <hash>)` mit Befehlsausgabe. Hier verweist Live-Verification auf `09-BASISLAUF.md`.

"stale"-Regel: VERIFICATION muss neuer sein als alle SUMMARYs der Phase; `covered_digest` mit `gsd-tools` neu erzeugen (nicht von Hand).

**07 (D-14):** Frontmatter `status: passed` und Text "human_needed" angleichen. Die zwei `human_verification`-Items (ab Z. 54) bleiben; kennzeichnen als "vom Nutzer bestätigt (2026-10-08)". **05 (D-21):** gleich; `behavior_unverified` zum Text passend setzen.

---

### `08-REVIEW-DISPOSITION.md` (review-ledger)

**Analog:** `04-REVIEW-DISPOSITION.md` (Frontmatter Z. 1-30: `findings:` mit `id/severity/disposition/title`, Zählung `open`, `total`, `recorded`).

Ist-Stand `08-REVIEW-DISPOSITION.md`: `open: 9, total: 10`; WR-03 `fixed`, alle anderen `open`. Ziel: WR-01, WR-02 `fixed` (Quelle: Fix-Commit-Hash), IN-01..IN-07 `deferred` mit Begründung in der Source-Zelle (Handzeile laut Fußtext: "Set `deferred` by hand and put the reason in the Source cell"). Frontmatter-Eintrag und Tabellenzeile synchron halten, `open: 0`. Die Datei wird vom Gate (review-gate) regeneriert; Handänderungen wirken nur für `deferred`/`fixed`-Zeilen, danach Gate laufen lassen und prüfen.

Beispielzeile: `| IN-03 | info | deferred | Phase 9 D-20: set-basierte Prüfung ausreichend, Docstring-Präzisierung optional |`

---

### 08/WR-01 Fix: wirkungsloser WR-03-Rendertest (code, transform)

**Befund** (`08-REVIEW.md` Z. 47-54): `renderToString` setzt `ueberlaeuft` nie (nur in `onMounted`), `rahmenAttribute(false,…)` liefert `{}`, die Tests bei `zustaende.test.ts:165-189` bleiben ohne Guard grün.

**Analog für Fix-Form:** reine Funktion in `app/src/components/datenTabelle.ts`, direkt getestet wie `rahmenAttribute` (`zustaende.test.ts:207-219`).

Bestehende Funktion (`datenTabelle.ts:41-49`):
```ts
export function rahmenAttribute(
  ueberlaeuft: boolean,
  captionId: string,
): Record<string, string | number> {
  if (!ueberlaeuft) {
    return {}
  }
  return { tabindex: 0, role: 'region', 'aria-labelledby': captionId }
}
```
Bestehendes Testmuster (`zustaende.test.ts:207-219`):
```ts
describe('rahmenAttribute (A11Y-01, 05/WR-02)', () => {
  it('liefert ohne Überlauf nichts', () => {
    expect(rahmenAttribute(false, 'caption-1')).toEqual({})
  })
  ...
```
Neue Funktion (Vorschlag aus Review): `rahmenSichtbar`/`rahmenSollNamenTragen({ ueberlaeuft, laedt, leer, beschriftung })` in `datenTabelle.ts`; Aufruf in `DatenTabelle.vue:131-136` ersetzt die Inline-Bedingung. Test: `expect(...(true,false,false,'  ')).toBe(false)` und Gegenprobe mit Text `true`. Fail-first: Guard temporär entfernen und Rot nachweisen. Die zwei SSR-Tests (`zustaende.test.ts:165-189`) entfernen oder umbenennen. Testtitel auf Deutsch. Vitest-Lauf nur in Scratch-Kopie von `app/`.

### 08/WR-02 Fix: leere `beschriftung` (component)

**Analog:** `alsZahl` in `DatenTabelle.vue` (Z. 195-200), das bei Inkonsistenz laut wirft:
```ts
function alsZahl(wert: string | number | null | undefined): number {
  if (typeof wert !== 'number') {
    throw new TypeError(`Erwartete Zahl für numerische Spalte, erhalten: ${typeof wert}`)
  }
  return wert
}
```
Aktueller Code, der zu ersetzen ist (`DatenTabelle.vue:127-144`):
```ts
const hatBeschriftung = computed(() => props.beschriftung.trim() !== '')
...
if (import.meta.env.DEV) {
  watchEffect(() => {
    if (!hatBeschriftung.value) {
      console.warn('DatenTabelle: `beschriftung` ist leer, der scrollbare Rahmen bliebe unbenannt.')
    }
  })
}
```
Fix-Optionen (Review): (a) Fallback `props.beschriftung.trim() || 'Tabelle'` für Caption und Rahmen, dann bleibt der Rahmen bei Überlauf fokussierbar (WCAG 2.1.1, `scrollable-region-focusable`); oder (b) werfen statt warnen. Option (a) hält die Tastaturbedienung auch in Produktion; dann entfällt `hatBeschriftung` im Rahmen-Aufruf und die zwei Quelltext-Regex-Tests in `quelltext.test.ts:225-250` müssen angepasst oder entfernt werden (sonst rot, deckt sich mit IN-01). Test über die reine Funktion aus WR-01 (`''` ergibt Fallback-Name, Rahmenattribute weiter gesetzt). Commit-Präfix `fix(09): 08/WR-02 ...`, `test(09): 08/WR-01 ...`. Danach `08-VERIFICATION.md` nach D-15 erneuern.

---

### `STATE.md`, `MILESTONES.md`, `REQUIREMENTS.md` (doc, CRUD)

Kein Codeanalog. Edit-Regeln: STATE.md Blockers/Concerns nach D-16 (Einträge 02-REVIEW, 04-REVIEW-DISPOSITION, `/gsd-secure-phase 04`, "kein Milestone-Audit/stale" entfernen; Scratch-Kopie-Hinweis bleibt). MILESTONES.md: datierten Nachtrag unter v1.0 anhängen, alter Text unverändert (D-17). REQUIREMENTS.md: bei "Deploy-/Gerätecheck aus Phase 7" Vermerk "vom Nutzer erledigt, 2026-10-08" (D-18); SEC-01/AUD-01..03 erst nach Beleg abhaken.

### `09-BASISLAUF.md` (evidence-doc)

**Analog:** Live-Verification-Block in `02-VERIFICATION.md` (Befehl, Ausgabe, HEAD-Hash). Inhalt: HEAD-Hash, `git status` vorher/nachher, CI-Zeilen aus `.claude/CLAUDE.md` (pytest, ruff, `alle.py` plus `git diff --stat --exit-code -- daten app/src/data`, Untracked-Check, App-Checks in Scratch-Kopie, `scripts/e2e-wie-ci.sh`) mit Exit-Codes und Testzahlen.

### `v1.0-MILESTONE-AUDIT.md`

Kein Repo-Analog. Schema aus `.claude/gsd-core/workflows/audit-milestone.md` (Frontmatter und Abschnitte: Anforderungen, Integration, E2E-Flüsse, `tech_debt`). Kopf nennt v1.0 und v1.0.1 (D-07). Eingaben beider Orte (D-08). `tech_debt`-Einträge: 04-VALIDATION (draft), 05-VALIDATION (`nyquist_compliant: false`) als deferred (D-09); Phase-7-CR-01 `s009.webp` (D-22).

## Shared Patterns

### Fix-Commit-Konvention
Format laut `git log`: `fix(08): WR-01 ...`, `fix(08-06): 05/WR-02 ...`, `test(phase-08): ...`. Für Phase 9: `fix(09): 04/T-04-XX ...` bzw. `fix(09): 08/WR-02 ...`. Nur explizit benannte Pfade stagen.

### Querschnittsbedingung
`uv run --directory pipeline python alle.py --jahr 2026` danach `git diff --stat --exit-code -- daten app/src/data` und `test -z "$(git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen)"`. App-Checks nur in Scratch-Kopie (`app/node_modules` hat macOS-Binaries).

### Dateistil
Deutsche Bezeichner ohne Umlaute in Code, Du-Anrede in App-Texten, Kommentare Deutsch, Testtitel Deutsch (IN-01 rügt Mischformen).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `.planning/v1.0-MILESTONE-AUDIT.md` | audit-doc | batch | Erstes Audit im Repo, Schema nur im Workflow `audit-milestone.md` |

## Metadata

**Analog search scope:** `.planning/milestones/v1.0-phases/`, `.planning/phases/08-fixes-und-triage/`, `app/src/components/`, `app/src/lib/__tests__/`
**Files scanned:** about 14 gelesen/gegrept
**Pattern extraction date:** 2026-10-09
**Hinweis:** Konkrete Code-Fundstellen für T-04-xx wurden nicht kartiert (Planer/Auditor ermittelt sie im Lauf, D-01).
