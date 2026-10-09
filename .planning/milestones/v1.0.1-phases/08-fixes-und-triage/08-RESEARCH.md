# Phase 8: Fixes und Triage - Research

**Researched:** 2026-10-07
**Domain:** Fix/triage phase on an existing Vue 3 + Python pipeline codebase (text correctness, a11y, hygiene, review-ledger bookkeeping). No new packages, no new features.
**Confidence:** HIGH for codebase facts and test/CI mechanics (read and executed this session); MEDIUM for screen-reader behaviour (not testable in this sandbox).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Jahreszahlen in Texten (TXT-03, 05/IN-10)
- **D-01:** `pruefe_text` lehnt jede handgetippte Zahl zwischen 1900 und 2099 ab und gibt eine klare Fehlermeldung aus. Die Ausnahme `_JAHR_MUSTER` (`pipeline/ostbevern/texte.py:44`) fällt weg. Jahreszahlen sind nur noch als `{{jahr.…|jahr}}` erlaubt. Dazu kommt ein pytest-Fall. Der Test `pipeline/tests/test_texte.py:388`, der „im Jahr 2026“ heute als gültig führt, wird umgedreht.
- **D-02:** **Gemischtes Schema für Jahres-Platzhalter.** Jahre, die sich auf das Haushaltsjahr beziehen (Vorjahr, Planjahre), werden relativ geschrieben, also über die bestehenden Schlüssel `jahr.haushaltsjahr`, `jahr.vorjahr`, `jahr.letztes_jahr` plus neue Schlüssel wie `jahr.haushaltsjahr_plus_1` oder `jahr.vorvorjahr`. Echte Ereignisjahre bekommen einen ausdrücklich festen Schlüssel, z. B. `{{jahr.fest_2022|jahr}}`. Das betrifft die Gewerbesteuer-Historie 2022/2023 und die Rücklagen „2020 bis 2024“. Jede Jahreszahl ist damit bewusst gesetzt, und ein fester Schlüssel wandert beim nächsten Jahrgang nicht mit. Die Schlüsselnamen legt der Planer fest.
- **D-03:** Alle 7 Abschnitte in `daten/manuell/texte/erklaerungen.md` mit getippten Jahren werden umgestellt: `schluesselzuweisung` (:7), `gewerbesteuer` (:13), `kreisumlage` (:19), `schulden` (:49), `verpflichtungsermaechtigungen` (:55), `ueberschuss_pb_11` (:93) und `ueberschuss_ruecklage` (:109). Für jeden Abschnitt wird geprüft, ob das Jahr relativ (D-02) oder fest ist. `glossar.md` enthält keine getippten Jahre. Die Änderung erzeugt einen bewussten Diff in `app/src/data/texte.json` (`absaetze` und `werte`), der im Commit begründet wird. Die CSVs unter `daten/aufbereitet/` dürfen sich nicht ändern.
- **D-04:** **`jahr.*`-Platzhalter binden einen Text nicht an das Haushaltsjahr.** `istJahrneutral` (`app/src/lib/texte.ts:62-64`) ignoriert sie, denn sie hängen am Haushaltsjahr und nicht am gewählten Jahr. Nur Platzhalter mit Beträgen binden einen Text weiterhin. Ohne diese Regel würden `ueberschuss_ruecklage` (nur 2024 sichtbar) und `ueberschuss_pb_*` nach der Umstellung verschwinden. Ein vitest-Fall sichert das ab.
- **D-05:** Auch die `Titel:`-Zeilen in `erklaerungen.md` und `glossar.md` laufen durch `pruefe_text`, bisher waren es nur die Absätze. Heute enthält kein Titel eine Zahl, es ist also eine reine Absicherung.

#### Lesehilfe und Minderaufwand (TXT-01, TXT-02, 05/IN-06, 05/IN-07)
- **D-06:** `lesehilfeSatz` (`app/src/lib/geldfluss.ts:655-685`) sagt „Erträge und Aufwendungen gleichen sich in diesem Jahr genau aus.“ nur noch, wenn es weder Defizit noch Überschuss noch Minderaufwand gibt. Kommt das Ergebnis erst durch den globalen Minderaufwand auf genau 0, lautet der Satz sinngemäß: „Die Aufwendungen sind höher als die Erträge. Erst der globale Minderaufwand von rund {Betrag} gleicht beide Seiten aus.“ Der Betrag kommt aus den Daten. vitest deckt beide Grenzfälle mit konstruierten Daten ab, denn mit den echten Daten tritt keiner davon ein.
- **D-07:** Der statische Text `geldfluss_lesehilfe` („Beide Seiten sind gleich groß.“) bleibt unverändert. Die Sankey-Seiten weichen wegen Druckrundungen um 1 bis 2 € voneinander ab (2024: 2 €, 2028: 1 €). Das liegt innerhalb der Toleranz, und der dynamische Satz sagt ohnehin „rund“. `texte.json` ändert sich dadurch nicht. Der Planer kann optional einen erklärenden Satz in `befunde.md` ergänzen.
- **D-08:** Ein positiver Minderaufwand (Z. 27 > 0) ist ein Datenfehler und wird einheitlich behandelt. `/geldfluss` (heute schon `geldfluss.ts:260-262`) und `/ausgaben` (`minderaufwandHinweis`, `app/src/lib/aufwandsarten.ts:173`) werfen dann beide mit einer klaren Meldung. Bei 0 erscheint kein Hinweis, das ist legitim (2024). TXT-02 („nie negativ angezeigt“) ist in Commit 53b96ac schon erfüllt. 05/IN-07 wird mit diesem Commit auf fixed gesetzt, der Vereinheitlichungs-Commit kommt als Beleg dazu.

#### Fehlende und abgeleitete Werte (TXT-05, TXT-06, 05/IN-08, 06/IN-07)
- **D-09:** **Eine fehlende oder ungültige Einwohnerzahl bricht laut ab.** Es gibt eine gemeinsame Hilfsfunktion `einwohnerZahl()`, die mit klarer Meldung wirft (Muster „… fehlt in haushalt.json“). Sie ersetzt die beiden privaten Duplikate in `lib/kennzahlen.ts:60-66` und `lib/produkt.ts:157-163` und wird auch von `EbenenTabelle` genutzt (heute `EbenenTabelle.vue:29,58`: Spalte bleibt, jede Zelle zeigt „–“). Damit ist auch das Einwohner-Duplikat aus 06/IN-03 erledigt. Ein sichtbarer Hinweis auf der Seite ist ausdrücklich nicht gewünscht.
- **D-10:** **Alle Summen der Stellenplan-Kacheln tragen das Etikett „berechnet“**, nicht nur die Differenzen. Grund: Es gibt keine gedruckte Gesamtzahl, die Werte sind Zeilensummen (`StellenplanPage.vue:66-69`). Heute setzt Kachel 2 `berechnet: false`. Die Quellenleiste nennt, woraus summiert wurde (P7 D-03).
- **D-11:** **Die Quellzeile einer Kachel nennt nur die PDF-Seiten der Zeilen, aus denen ihr Wert stammt**, und nur für Jahre, die einen Wert haben. Beispiel: Vorjahr und besetzt stehen auf S. 284–286, das Haushaltsjahr auf S. 284–289. Dazu liefert `stellenSummen()` (`lib/stellen.ts:122-133`) die Seiten je Kachel getrennt statt als Vereinigung. Das gilt auch für `nachwuchs()` (`lib/stellen.ts:187-200`) und `nachwuchsSatz`. Die `seitenBeleg`-Schlüssel bleiben gleich, damit `quellen.json` sich nicht ändert.
- **D-12:** **„Zusammen rd. …“ in `ZuschussListe.vue:84` trägt „berechnet“ nur, wenn die Summe tatsächlich berechnet wurde.** `zusammen()` (`lib/zuschuesse.ts:138-144`) liefert dazu `{ wert, berechnet }`. Eine gedruckte Summe bleibt ohne Etikett. Die Gruppe `transfer` hat nie eine gedruckte Summe und ist daher immer berechnet. Danach wird geprüft, ob weitere abgeleitete Summen auf Kontextseiten ohne Etikett sind.

#### Hygiene und Triage (TRI-01 bis TRI-04)
- **D-13:** **Schwelle für „kostet wenig“: Alle trivialen und kleinen Befunde werden behoben,** jeweils mit Befund-ID im Commit. Das sind 01/IN-02, 01/IN-04 (Rest: `>= 0` für `anzahlen.*`), 05/IN-01 (Ansatz mit zwei Markern), 05/IN-03, 05/IN-04, 05/IN-11 (Rest: CLAUDE.md-CI-Block mit Reproduzierbarkeit und Playwright, Kopfkommentar in `ci.yml` zum Remote, Glossar-Invariante `absaetze[0]`), 06/IN-01 (Rest: Surface-Konstante aus `echartsTheme.ts`), 06/IN-02 (`ausgleichsruecklageAufgebrauchtJahr` entfernen oder auf `haushaltsjahrIndex()` umstellen, Planer entscheidet), 06/IN-03 (Helfer in `lib/jahr.ts`, `postenEintrag()`, `anzahlText`), 06/IN-04 (schlankes Modul für `quellenZeile`, `jahreListe`, `klickIndex`), 06/IN-05 (Filter nur einmal instanziieren), 06/IN-06 und 06/IN-08 (`ZeroDivisionError`-Schutz mit `TexteFehler`). `deferred` bekommt nur, was ein neues Paket oder einen größeren Umbau bräuchte, und dann mit Begründung in der Source-Spalte. Die Daten bleiben byte-identisch.
- **D-14:** **06/IN-09 (Tests prüfen Quelltext statt Verhalten) wird ohne neues Paket gelöst.** Das Verhalten von `menueVersatz` (Versatz bzw. `style.left` nach einem Resize) wird per Playwright geprüft, und die betroffenen `?raw`-Prüfungen werden entfernt (`menueVersatz.test.ts:5-8,152-155`, `ruecklagen.test.ts:307`). Weitere `?raw`-Tests, die bewusst Konventionen absichern (Token-Wächter, Du-Anrede, Inventar), bleiben, bekommen aber einen Kommentar mit dem Grund. Disposition: fixed. happy-dom und `@vue/test-utils` kommen **nicht** ins Projekt.
- **D-15:** **01/IN-03: Das Flag `beispieldaten` an `ChartCard` bleibt**, denn es ist die Regel aus CLAUDE.md und ein Schutz für spätere Seiten. Im `warning`-Callout wird das Icon `triangle-exclamation` statt `circle-info`. Die verwaiste Datei `app/src/data/beispieldaten.json` aus Phase 1 wird gelöscht. Die Pipeline erzeugt sie nicht und nichts importiert sie. Die Löschung wird im Commit als bewusste Änderung unter `app/src/data/` begründet.
- **D-16:** **05/IN-02: Der Slot-Modus von `DatenTabelle` wird entfernt** (Default-Slot bei `:44`, Slot-Zweige). Alle 29 Aufrufe übergeben `:zeilen`. Das ist eine bewusste Abweichung von der Konvention „Basiskomponenten behalten die Münster-Props“, und der Nutzer hat sie so entschieden. Der Commit und ein Kommentar in der Komponente halten die Abweichung fest. — **Reversibility:** costly — wer später Slot-Inhalte braucht, muss den Modus samt Re-Observe-Logik neu bauen.
- **D-17:** **Dispositionen ohne Code-Arbeit:**
  - 01/IN-01 → fixed (1c14077, `bars.svg` wird im Menüknopf genutzt)
  - 05/IN-07 → fixed (53b96ac, siehe D-08)
  - 05/IN-09 → fixed (1ab6b4b, b29be89, f4fad93)
  - 06/WR-01 → skipped, Begründung: UAT 06 Test 1 und PROJECT.md:138 („Beträge-Lesart ergibt die gedruckten 1,77 %; Vorzeichen-Zusatz nicht nötig“). Die beiden „plus“-Kommentare (`lib/ruecklagen.ts:91`, `ruecklagen.test.ts:212-213`) werden trotzdem klarer formuliert, weil das trivial ist.
- **D-18:** Die Ledger werden am Ende der Phase von Hand gepflegt: Disposition setzen, Commit oder Begründung in die Source-Spalte, `open:` im Frontmatter auf 0. Das Ledger-Format (siehe Fußtext jeder DISPOSITION-Datei) bleibt erhalten.

#### Barrierefreiheit (A11Y-01 bis A11Y-03, 05/WR-02, 01/IN-05, 05/IN-05) — Voreinstellung, vom Nutzer übernommen
- **D-19:** **`beschriftung` wird bei `DatenTabelle` Pflicht** (`string`, nicht optional). Alle 29 Aufrufe übergeben sie schon. `components/__tests__/zustaende.test.ts` wird angepasst. Ein scrollbarer Rahmen (`tabindex` bei Überlauf) hat damit immer `role="region"` und einen Namen.
- **D-20:** **Jede Tabelle hat genau einen Namen.** Die Caption bekommt eine `id`, und der Region-Rahmen verweist per `aria-labelledby` darauf, statt eines zweiten `aria-label`. Der Text existiert also nur einmal. Ob ein Screenreader die Region und die Caption trotzdem nacheinander ansagt, prüft der Planer bzw. die Recherche. Falls ja, ist die Alternative erlaubt, in der nur eine der beiden Beschriftungen den Namen trägt. Belege: vitest, der axe-Smoke-Test und ein Playwright-Test bei 360 px.
- **D-21:** **Das mobile Menü schließt sich bei jedem Klick auf einen Link im Drawer** (`@click` an den `RouterLink`s, `App.vue:172,177`), auch beim Link der aktuellen Seite. Der Watcher auf die Route bleibt. Beim Klick auf die aktuelle Seite springt der Fokus nicht zum Menüknopf zurück, analog zu `schliesstDurchSeitenwechsel`. Ein Playwright-Test im Projekt `mobil` (360 px) belegt das. Die vorhandenen Drawer-Tests liegen in `e2e/interaktion.spec.ts:175,276` und `e2e/mobil.spec.ts:194`.

#### „rd.“-Regel (TXT-04, 05/WR-01)
- **D-22:** Die Regel „rd.“ plus Betrag mit geschütztem Leerzeichen ist an genau einer Stelle umgesetzt. `RD_PRAEFIX` und `betragMitHinweis` ziehen aus `lib/geldfluss.ts` in `charts/format.ts` um. Damit ist auch die Kopplung `EuroBetrag` → `geldfluss` aus 06/IN-04 aufgelöst. Templates nutzen `EuroBetrag`, `.ts`-Code nutzt `betragMitHinweis` bzw. eine Kurzvariante für `euroKurz`. Zu entfernen sind alle Altkopien. Das sind die fünf aus dem Review (`SteuerZeitreihe.vue:147`, `lib/drilldown.ts:201,360`, `lib/zeitreihen.ts:246`, `AufwandTreemap.vue:53`, `EbenenTabelle.vue:79`) und die weiteren Fundstellen (`PostenZeitreihe.vue:153`, `AusgabenPage.vue:347`, `EinnahmenPage.vue:336,409`, `ZuschussListe.vue:65,84,89`, `NichtBeeinflussbarBlock.vue:52`, `KreisumlageCallout.vue:70`). Die Tests werden angepasst (`quelltext.test.ts:151`, `zeitreihen.test.ts:232`, `drilldown.test.ts:337`), und ein Wächter-Test verhindert neue Kopien. Der veraltete Doc-Kommentar in `EuroBetrag.vue:5-8` wird korrigiert.

### Claude's Discretion
- Die genauen Namen der neuen `jahr.`-Schlüssel (relativ und fest), und ob feste Jahre als Schlüssel in `jahrgaenge/2026.toml` oder direkt in `texte.py` aufgelöst werden. Jahrgangsregel: Werte, die vom Jahrgang abhängen, gehören in die TOML.
- Der genaue Wortlaut des Minderaufwand-Satzes im Rahmen von D-06 (Du-Anrede, „rund“ mit `RD`-Regel).
- Ob eine Kurzvariante (z. B. `kurzMitHinweis`) für `euroKurz` entsteht oder `RD_PRAEFIX` direkt genutzt wird.
- Ob 06/IN-02 durch Entfernen oder Umstellen gelöst wird.
- Wie die Pläne zugeschnitten und in Wellen geordnet werden, innerhalb der Roadmap-Reihenfolge Texte → A11Y/Hygiene → Ledger.

### Deferred Ideas (OUT OF SCOPE)
None — die Diskussion blieb im Phasenumfang. Neue Pakete wurden bewusst abgelehnt (DOM-Testumgebung, D-14).

### Approved UI contract (locked, treat as part of constraints)
`08-UI-SPEC.md` is approved (status: approved 2026-10-07). Its `[Default]` items are listed under "Offene Annahmen" there; the planner adopts them or justifies a deviation. Sections of this RESEARCH.md that contradict a UI-SPEC statement are collected in "Corrections to upstream premises" below and need a planner decision, not silent deviation.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TXT-01 | Lesehilfe says "genau aus" only when truly balanced | `lesehilfeSatz` is a pure function of a `Geldfluss` object, so constructed-data vitest cases are straightforward (Section "Per-requirement implementation map"). |
| TXT-02 | Minderaufwand hint never negative | Already met by 53b96ac; D-08 adds throw-on-positive. `minderaufwandHinweis` reads module-level `haushalt`, so a pure shared helper is needed to test the positive case without mutating data. |
| TXT-03 | `pruefe_text` rejects typed years 1900-2099 | After deleting `_JAHR_MUSTER` the generic "Nackte Ziffer" error would already fire, but with a poor message; a dedicated year check before it gives the "klare Fehlermeldung". Resolver and fixture constraints documented. |
| TXT-04 | One implementation of "rd." + NBSP | Complete inventory of 17 copy sites with file:line; target API in `charts/format.ts`; guard-test approach. |
| TXT-05 | Derived sums carry "berechnet"; tile source lines cite own pages | `stellenSummen`, `nachwuchs`, `zusammen`, `ZuschussListe` analysed; real data has identical page sets for all three tiles, so tests need constructed `Stellenplan` input. |
| TXT-06 | `EbenenTabelle` reports missing Einwohnerzahl | Three Einwohner code paths found (two helpers + `EbenenTabelle`); shared helper placement and lazy call recommended. |
| A11Y-01 | Scroll container always has role and name | `DatenTabelle` rewrite plan; vitest SSR cannot see overflow-state attributes, so extract a pure helper. |
| A11Y-02 | Mobile menu closes on tap of current-page link | Reproduced the bug; discovered and prototyped the real fix including a wa-drawer focus-restore pitfall. |
| A11Y-03 | No doubled table naming | Chromium accessibility-tree evidence collected; screen-reader behaviour remains an assumption (A1). |
| TRI-01..TRI-04 | Ledgers to `open: 0` | Full 28-finding table with disposition, work needed and evidence; orphaned older 05 findings flagged. |
</phase_requirements>

## Summary

This phase is a bounded clean-up of an already shipped static app. Every locked decision (D-01 to D-22) maps to concrete code that I read this session. The environment can run the full verification chain: pipeline checks run in place (the real `pipeline/.venv` is Linux aarch64), app checks must run in a scratch copy of `app/` (the real `app/node_modules` holds macOS binaries), and Playwright runs through the project's own docker script against the scratch build. I executed the baseline: vitest 1968 tests green, type-check/lint/prettier/build green, Playwright `ci` project 81 tests green (35 s), `mobil` project 14 green, `alle.py --jahr 2026` exit 0 in 29 s with a clean `git diff` for `daten/`, `app/src/data/` and `app/public/quellen`, and pytest 645 passed / 1 skipped (the skip disappears when the scratch app `node_modules` is linked into the scratch repo).

Four findings change how the planner should write tasks, because they contradict a premise in CONTEXT/UI-SPEC (details under "Corrections to upstream premises"): (1) the drawer focus problem is bigger than "also close on current-page click": Web Awesome 3.14 restores focus to the menu button with `setTimeout` after every drawer close, so today even a normal page navigation from the drawer ends with focus on the menu button, not the `h1`; I prototyped and verified a fix. (2) The UI-SPEC says the axe smoke test covers `landmark-unique` at 360 px and 1280 px; it does not (desktop only, WCAG tags only). (3) The D-11 example page ranges do not occur in the real data (all three tiles are on S. 284-286). (4) Chromium's accessibility tree names both the region and the table in both the `aria-label` and the `aria-labelledby` variants, so D-20 reduces duplicated attribute text but cannot be proven to remove a double announcement without a real screen reader.

**Primary recommendation:** Execute in the roadmap order in three waves (texts and numbers; a11y and hygiene; ledgers), keep every plan file-disjoint inside a wave (conflict matrix below), verify with the scratch-copy chain after every task group, and treat the drawer focus fix (`setTimeout` after `wa-after-hide`) and the extracted pure `DatenTabelle` attribute helper as the two non-obvious implementation details.

## Project Constraints (from CLAUDE.md)

Source: `/Users/thma/repos/bitwerkstatt/ostbevern_money/.claude/CLAUDE.md` (project) and `/Users/thma/repos/bitwerkstatt/CLAUDE.md` (sandbox). Treat with the authority of locked decisions.

- Pipeline stack: Python >= 3.12, uv, pdfplumber, polars, typer, pytest, ruff. App stack: Vue 3, TypeScript, Vite, Web Awesome 3 (components imported individually in `app/src/main.ts`, icons self-hosted under `app/public/icons`), ECharts 6 via vue-echarts 8 (only modules registered in `app/src/charts/echartsTheme.ts`), ESLint flat config + Prettier, Node 22.
- Pipeline commands from repo root: `uv sync --directory pipeline`, `uv run --directory pipeline pytest`, `uv run --directory pipeline ruff check .`, `uv run --directory pipeline ruff format .`, `uv run --directory pipeline python alle.py --jahr 2026`. A bare `uv run pipeline/SKRIPT.py` does not use the pipeline env, always pass `--directory pipeline`.
- App commands: `npm --prefix app ci|run dev|build|type-check|lint|format:check|test`.
- German identifiers without umlauts in code and data. Amounts are int euros; formatting only through `app/src/charts/format.ts`. Only 1-based PDF pages (`pdf_seite`).
- No Jahrgang values in code: year, PDF path, column heads, page ranges, header patterns, expected counts live in `pipeline/jahrgaenge/{jahr}.toml` / `{jahr}_sollwerte.toml`, read only through `ostbevern.konfiguration.lade_jahrgang` / `lade_sollwerte`. Every pipeline script takes `--jahr`.
- Du-Anrede throughout all app texts. Numbers in texts come from data, never typed by hand; every explanatory text with a number cites a PDF page.
- Fachliche Regeln (Zeilenformeln, Minderaufwand-Zeilen, Ausschluss TP 27/28) stay in code. Generated data under `daten/` is checked in.
- Base components keep Münster names and props (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `format.ts`, `echartsTheme.ts`, `bildschirm.ts`); D-16/D-19 are the user-approved exceptions for `DatenTabelle`.
- Colours only via `--wa-*` tokens, chart colours only from `echartsTheme.ts`. Project CSS classes carry the prefix `om-`. Example values only behind the `ChartCard` flag `beispieldaten`. No third-party requests at runtime.
- **When committing, stage only explicitly named paths** (never `git add -A`/`.`). This matters because `.claude/` and `.planning/state.json` are untracked/modified in the working tree.
- Accuracy: deviations over 1 EUR against plan values are errors unless documented in `befunde.md`. Lighthouse a11y >= 95, `prefers-reduced-motion`, responsive from 360 px.
- GSD workflow enforcement: all edits go through a GSD command (this phase's execute step).
- Sandbox note: shell completions must never be added to `/etc/sandbox-persistent.sh`.

## Architectural Responsibility Map

This is a static site with a build-time Python pipeline; "tiers" here are build-time pipeline, app logic layer (pure TS), app presentation layer (Vue), browser/E2E verification, and planning docs.

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Year-number rule in texts (TXT-03) | Pipeline (`texte.py`, `pruefe_text`) | App logic (`istJahrneutral` in `lib/texte.ts`) | The "no hand-typed numbers" gate is a build-time validator; the app only decides visibility per chosen year. |
| Lesehilfe sentence, Minderaufwand rule (TXT-01/02) | App logic (`lib/geldfluss.ts`, `lib/aufwandsarten.ts`) | App presentation (`GeldflussPage`, `AusgabenPage`) | Sentence is a pure function of data; pages only render it. |
| "rd." + NBSP rule (TXT-04) | App logic (`charts/format.ts`) | App presentation (`EuroBetrag.vue`) | One formatting authority per CLAUDE.md; component wraps it for templates. |
| "berechnet" label, tile source lines (TXT-05) | App logic (`lib/stellen.ts`, `lib/zuschuesse.ts`) | App presentation (`StellenplanPage`, `ZuschussListe`, `BerechnetEtikett`) | Data layer decides what is derived and which pages belong; presentation places the label. |
| Missing Einwohnerzahl (TXT-06) | App logic (shared `einwohnerZahl()`) | App presentation (`EbenenTabelle`) | Data errors throw loudly in the logic layer (established pattern). |
| Scroll container role/name (A11Y-01/03) | App presentation (`DatenTabelle.vue`) | Browser E2E | Needs layout (overflow) knowledge, only available in the browser. |
| Drawer closing and focus (A11Y-02) | App presentation (`App.vue`) | Third-party `wa-drawer` behaviour | The app must compensate for the drawer's own focus restore. |
| Ledger dispositions (TRI-*) | Planning docs (`.planning/milestones/v1.0-phases/*-REVIEW-DISPOSITION.md`) | Git history as evidence | Hand-maintained records. |

## Standard Stack

No new libraries. Everything below is already in the repo; versions read from `app/package.json` and `pipeline/uv.lock` / `pyproject.toml` this session.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| vitest | 5.0.3 (`app/package.json`) | Unit tests, `environment: 'node'`, SSR `renderToString` | Existing runner; `include: ['src/**/__tests__/*.test.ts']` (`vitest.config.ts`). |
| @playwright/test | 1.63.0 | Browser tests (`ci`, `mobil`, `texte` projects) | Existing; image `mcr.microsoft.com/playwright:v1.63.0-noble` is already pulled in this sandbox. |
| @axe-core/playwright | 4.13.0 | axe in smoke test | Existing (`e2e/smoke.spec.ts`). |
| pytest | 9.1.1 (installed in `pipeline/.venv`) | Pipeline tests | Existing. |
| ruff | 0.16.9 | Lint/format for pipeline | Existing. |
| @awesome.me/webawesome | 3.14.0 | `wa-drawer`, `wa-callout`, `wa-tag` | Existing; its drawer behaviour matters for A11Y-02. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Playwright for DOM behaviour | happy-dom + @vue/test-utils | Explicitly rejected by D-14 (no new packages). |
| Parsing fixed years from the key name (`jahr.fest_2022`) | A `[texte]` table in `jahrgaenge/2026.toml` | See Pattern 2; key-name parsing needs no TOML and no Jahrgang value in code. |

**Installation:** none. No `npm install` / `uv add` in this phase.

**Version verification:** `npm view` was not needed because no package is added; installed versions were read from `app/package.json` and the scratch `npm ci` (283 packages, exit 0) [VERIFIED: scratch `npm ci` log].

## Package Legitimacy Audit

No external package is installed or recommended in this phase (D-14 explicitly rejects happy-dom and `@vue/test-utils`; the Lighthouse script installs `lighthouse@13.5.0` in its own scratch directory behind an existing human gate from phase 7 and is optional here).

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | - | - | - | - | - | - |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
daten/manuell/texte/{erklaerungen,glossar}.md
   |  lies_erklaerungen / lies_glossar            (texte.py)
   v
pruefe_text(absatz)  <-- D-01: year rule, D-05: also Titel lines (reject placeholders in titles)
   |
   v
textwerte(haushalt, investitionen, produkte, texte)  -- jahr.* keys incl. new relative keys
   |  loese_auf(texte, werte)  -- must also resolve jahr.fest_<JJJJ>
   v
app/src/data/texte.json  (absaetze + werte)  --- only intended data diff of the phase
   |
   v
lib/texte.ts: rendereAbsatz / istJahrneutral / textFuerJahr   (D-04)
   |
   +--> ErklaerText.vue, GlossarListe.vue, AusgabenPage.vue    (text on pages)

app/src/data/haushalt.json, stellenplan.json  (unchanged)
   |
   +--> lib/geldfluss.ts  lesehilfeSatz (D-06), Minderaufwand throw (D-08)
   +--> lib/aufwandsarten.ts minderaufwandHinweis (D-08)
   +--> lib/stellen.ts stellenSummen/nachwuchs per-tile pages (D-11)
   +--> lib/zuschuesse.ts zusammen() -> {wert, berechnet} (D-12)
   +--> lib/einwohner (new) einwohnerZahl() (D-09)
   |        all amounts -> charts/format.ts (RD_PRAEFIX, betragMitHinweis, kurzMitHinweis)  (D-22)
   v
Vue components (EuroBetrag, KennzahlKachel, ZuschussListe, EbenenTabelle, DatenTabelle, App.vue drawer)
   |
   v
vite build -> dist -> Playwright (ci 1280x800, mobil 360x640) + axe
```

### Recommended Project Structure (touch points only)

```
pipeline/ostbevern/texte.py            # D-01, D-02 keys, D-05, 01/IN-.., 06/IN-08, 05/IN-11 (lies_glossar invariant)
pipeline/ostbevern/konfiguration.py    # 01/IN-04 (>= 0 for anzahlen)
pipeline/alle.py                       # 01/IN-02
pipeline/tests/test_texte.py           # D-01 inversion, new cases
daten/manuell/texte/erklaerungen.md    # D-03 (7 sections)
app/src/charts/format.ts               # D-22 (RD_PRAEFIX, betragMitHinweis, kurz variant), jahreListe (06/IN-04)
app/src/lib/{geldfluss,aufwandsarten,stellen,zuschuesse,kennzahlen,produkt,jahr,texte,ruecklagen,investitionen,schulden,bindungsgrad,entwicklung}.ts
app/src/components/{DatenTabelle,EuroBetrag,EbenenTabelle,ZuschussListe,ChartCard,...}.vue
app/src/pages/StellenplanPage.vue, App.vue
app/e2e/mobil.spec.ts (+ optional interaktion.spec.ts)   # A11Y-02, A11Y-01/03, 06/IN-09
.planning/milestones/v1.0-phases/{01,05,06}-*/…-REVIEW-DISPOSITION.md   # TRI-*
```

### Pattern 1: One authority for "rd." (D-22)

**What:** Move `RD_PRAEFIX` and `betragMitHinweis` verbatim into `charts/format.ts`, add one short variant, and make every other site call them.

Current definition [VERIFIED: `app/src/lib/geldfluss.ts:124-129`]:
```ts
export const RD_PRAEFIX = 'rd. '
export function betragMitHinweis(wert: number, gerundet: boolean): string {
  return gerundet ? `${RD_PRAEFIX}${euro(wert)}` : euro(wert)
}
```
Target in `charts/format.ts` (names for the short variant are discretion):
```ts
export const RD_PRAEFIX = 'rd. '
export function betragMitHinweis(wert: number, gerundet: boolean): string {
  return gerundet ? `${RD_PRAEFIX}${euro(wert)}` : euro(wert)
}
export function kurzMitHinweis(wert: number, gerundet: boolean): string {
  return gerundet ? `${RD_PRAEFIX}${euroKurz(wert)}` : euroKurz(wert)
}
```
**When to use:** `.ts` and string-valued table cells use the functions; templates use `<EuroBetrag>` (optionally an additive `kurz` prop).

**Complete inventory of copies to remove** (all [VERIFIED: grep this session], line numbers current):

| File:line | Current shape | Replace with |
|-----------|---------------|--------------|
| `components/SteuerZeitreihe.vue:147` | `<span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}` | `<EuroBetrag :wert :gerundet>` |
| `components/PostenZeitreihe.vue:153` | same markup | `<EuroBetrag>` |
| `pages/AusgabenPage.vue:347` | same markup | `<EuroBetrag>` |
| `pages/EinnahmenPage.vue:336, 409` | same markup (also `BerechnetEtikett` next to it) | `<EuroBetrag :berechnet>` |
| `lib/drilldown.ts:201` | `` `rd. ${euro(...)}` `` | `betragMitHinweis` |
| `lib/drilldown.ts:360` | `` `rd. ${euroKurz(Math.abs(...))}` `` | `kurzMitHinweis` |
| `lib/zeitreihen.ts:246` | `` `rd. ${text}` `` in `betragText` | `betragMitHinweis` (keep `KEIN_WERT` for null) |
| `components/AufwandTreemap.vue:53` | `` `rd. ${euroKurz(...)}` `` | `kurzMitHinweis` |
| `components/EbenenTabelle.vue:79` | local `betragText` | `betragMitHinweis` |
| `components/ZuschussListe.vue:65, 84, 89` | `rd. ${euro(wert)}`, `Zusammen rd. ${euro(summe)}`, `rd. ${euroKurz(p.wert)}` | functions / `EuroBetrag` |
| `components/NichtBeeinflussbarBlock.vue:52` | `` `rd. ${euroKurz(p.wert)}` `` | `kurzMitHinweis` |
| `components/KreisumlageCallout.vue:70` | `<span class="om-zahl">rd. {{ euroKurz(u.wert) }}</span>` | `kurzMitHinweis` or `EuroBetrag kurz` |
| `lib/geldfluss.ts:515` | `` `${RD_PRAEFIX}${betrag}` `` with `betrag = euroKurz(...)` | `kurzMitHinweis` |

The `rund` variant for running text (UI-SPEC "Die Regel rd. und rund") also belongs here (e.g. `rundText`), and `lesehilfeSatz` Satz 1 (`rund ${euroKurz(...)}` at `geldfluss.ts:661`, currently a plain space) must use it so there is no second spelling of "rund".

**Test updates required:** `lib/__tests__/geldfluss.test.ts` (imports `RD_PRAEFIX`, `betragMitHinweis` from `@/lib/geldfluss`, lines ~193-230), `zeitreihen.test.ts:231-236`, `drilldown.test.ts:321-338`, `quelltext.test.ts:151` (the probe `'<span v-if="zeile[\'gerundet\'] === 1">rd. </span>'` in the "lässt … unbeanstandet" list of `getippteZahlen` must go or be replaced). `EuroBetrag.vue` imports `betragMitHinweis` from `@/lib/geldfluss`; change it to `@/charts/format` (this removes the `EuroBetrag` -> `geldfluss` coupling named in 06/IN-04).

**Guard test:** a vitest that reads all non-test `src/**/*.ts|vue` via `import.meta.glob(..., { query: '?raw' })` (the established pattern in `quelltext.test.ts`, `stiltokens.test.ts`) and fails if a string/template shape builds the prefix by hand. Shapes that exist today and must be caught: template `rd. {{`, markup `>rd. </span>`, TS template literals `` `rd. ${ `` and `'rd. '`. Allowlist `charts/format.ts` and `__tests__/`. Strip comments first, because many doc comments legitimately contain the typographic form `„rd.“`.

**Pitfall:** `zweizeilig()` (`charts/beschriftung.ts:10`) splits at the first `\s`, which includes U+00A0. Never call it on a string that already carries the `rd.` prefix, or "rd." lands alone on line 1.

### Pattern 2: Year placeholders (D-01 to D-05)

`pruefe_text` today [VERIFIED: `pipeline/ostbevern/texte.py:189-232`]: placeholders are removed from `rest`, then `rest = _JAHR_MUSTER.sub("", rest)`, then `_PARAGRAF_MUSTER` and `_SEITE_MUSTER`, then any remaining `\d` raises `Nackte Ziffer außerhalb Platzhalter/Jahreszahl/§/S.`.

Implementation shape:
1. Delete `_JAHR_MUSTER` (line 44) and the `.sub` at line 221.
2. After the paragraph/page substitutions and before the generic digit check, test the same pattern `\b(?:19|20)\d{2}\b` and raise a dedicated `TexteFehler` (German, names the number, the section, and the way out). UI-SPEC proposes: `Handgetippte Jahreszahl „{zahl}“ in Abschnitt „{schluessel}“. Jahreszahlen stehen nur als Platzhalter, zum Beispiel {{jahr.haushaltsjahr|jahr}}.` `pruefe_text(text)` has no section argument today, so either add an optional `kontext` parameter or let the callers (`app_daten.py:1114-1116`) wrap the error with the section key.
3. Without step 2 the generic digit error already rejects `2026` (so TXT-03 would "work" accidentally), but its message talks about "Nackte Ziffer"; the requirement text asks for a clear message.
4. `"1990er"` has no `\b` between `1990` and `er`, so it falls through to the generic digit error: still rejected, fine.

**Where the sections stand** (all [VERIFIED: `daten/manuell/texte/erklaerungen.md` read this session]; typed years in prose, outside placeholders):

| Section (line) | Typed years | Suggested key |
|----------------|-------------|---------------|
| `schluesselzuweisung` (7) | "Im Jahr 2025" | `jahr.vorjahr` (exists, `texte.py:423`) |
| `gewerbesteuer` (13) | 2022, 2023, 2024 | `jahr.fest_2022`, `jahr.fest_2023`; 2024 as `jahr.vorvorjahr` (new) |
| `kreisumlage` (19) | "Jahresabschluss 2024" | `jahr.vorvorjahr` |
| `schulden` (49) | "Ende 2025" | `jahr.vorjahr` |
| `verpflichtungsermaechtigungen` (55) | "im Jahr 2027 … 2028" | `jahr.haushaltsjahr_plus_1`, `jahr.haushaltsjahr_plus_2` (new) |
| `ueberschuss_pb_11` (93) | "aus dem Jahr 2023 … im Jahr 2025" | `jahr.fest_2023`, `jahr.fest_2025` |
| `ueberschuss_ruecklage` (109) | "2020 bis 2024" | `jahr.fest_2020`, `jahr.fest_2024` |

`glossar.md`: the grep for years only matches inside data placeholders (`….2026|euro}}` etc.), no typed prose year [VERIFIED: grep this session]. All `Titel:` lines contain no digit and no `{`, `<`, `>` [VERIFIED: grep this session].

**Fixed-year resolution (discretion, recommendation):** resolve `jahr.fest_<JJJJ>` generically by parsing the four digits from the key (`^jahr\.fest_(\d{4})$`), in a helper that `loese_auf` (and `vorschau`) consult when a key is not in `werte`. Reasons: (a) the pytest fixture `werte` is built with `textwerte(haushalt, investitionen, produkte)` without `texte` (`test_texte.py` fixture, `test_formatiere.py:~350`), and `test_erklaerungen_alle_schluessel_existieren` calls `loese_auf(echte_erklaerungen, werte)`, so keys added only when `texte` is passed would break that test; (b) the historical years 2020/2022/2023 are not in `haushalt.jahre` (2024-2029), so there is nothing to look up; (c) the key name already carries the value, so a TOML table would be a tautology; (d) no Jahrgang value is hard-coded in Python. Relative keys (`jahr.vorvorjahr`, `jahr.haushaltsjahr_plus_1`, `jahr.haushaltsjahr_plus_2`) are added next to `jahr.vorjahr` in `textwerte` (`texte.py:422-425`), always present.

**Resulting `texte.json` diff** (intended, to be justified in the commit): `absaetze` of the 7 sections, and `werte` gains `jahr.vorvorjahr`, `jahr.haushaltsjahr_plus_1`, `jahr.haushaltsjahr_plus_2`, `jahr.fest_2020`, `jahr.fest_2022`, `jahr.fest_2023`, `jahr.fest_2024`, `jahr.fest_2025` in first-use order (`verwendet` dict order in `loese_auf`). The visible text for 2026 must be character-identical; the 2026 values are 2024 (vorvorjahr), 2027, 2028.

**D-04 (`istJahrneutral`)** [VERIFIED: `app/src/lib/texte.ts:62-64`]: current rule is "no placeholder at all". New rule: neutral iff every placeholder key starts with `jahr.`. Side effects checked in `texte.json`: no text in `texte` consists only of `jahr.*` placeholders today; the only glossary entry that does is `haushaltssicherung`, and glossary entries are not filtered by `textFuerJahr` (`GlossarListe.vue` renders all), so nothing disappears or appears unexpectedly [VERIFIED: node scan of `texte.json`]. Add the invariant test from the UI-SPEC: every `texte` entry that `istJahrneutral` marks neutral uses only `jahr.fest_*` keys.

**Pitfall (title placeholders):** D-05 sends titles through `pruefe_text`, which accepts well-formed placeholders. `ErklaerText.vue` renders `{{ text.titel }}` raw [VERIFIED: `ErklaerText.vue:27`], and `loese_auf` only scans `absaetze`. A placeholder in a title would therefore be shown literally. Make the title check also reject `{{`.

**Pitfall (latent mismatch, informational):** several of these texts already contain data placeholders with a hard-coded year in the key (e.g. `{{vorbericht.zuwendungen.schluesselzuweisung.2025|mio}}`). Replacing only the typed prose year by a relative key makes the prose move with the Jahrgang while the data key does not. D-02 is locked and the texts must be rewritten for the next Jahrgang anyway; mention it in the commit message so it is a conscious state.

### Pattern 3: `lesehilfeSatz` four cases (D-06)

Current logic [VERIFIED: `app/src/lib/geldfluss.ts:653-686`]: Satz 1 always; Defizit sentence if `defizit`; "ebenfalls links" Minderaufwand sentence if `minderaufwand`; Überschuss sentence; the bug is `if (!defizit && !ueberschuss)` adding "gleichen sich … genau aus" (line 678-680), which is also reached when only the Minderaufwand closes the gap. The sentence has the verbatim text `'Erträge und Aufwendungen gleichen sich in diesem Jahr genau aus.'` (line 679).

Implement the four cases in UI-SPEC "Lesehilfe": A (Defizit), B (Überschuss, Minderaufwand without "ebenfalls"), C (only Minderaufwand: `Die Aufwendungen sind höher als die Erträge. Erst der globale Minderaufwand von {Betrag mit Hinweis} gleicht beide Seiten aus. …`), D (nothing: the only place with "genau"). Case C's amount goes through `betragMitHinweis(wert, gerundet)` (the node has `gerundet`), not `euro()`.

Test with a constructed `Geldfluss` literal (type at `geldfluss.ts:73-79`: `knoten`, `kanten`, `summeLinks`, `summeRechts`, `pdfSeite`; node fields at `:44-58`). Real data never hits C or D (CONTEXT data table). The existing test block `describe('lesehilfeSatz …')` (`geldfluss.test.ts:397-440`) already iterates the real years and must stay green: for 2025-2029 it expects "Defizit" plus the Minderaufwand amount; for 2024 "Überschuss".

### Pattern 4: Minderaufwand rule shared (D-08)

`minderaufwandHinweis` [VERIFIED: `app/src/lib/aufwandsarten.ts:167-186`] reads module-level `haushalt` and returns `null` for `wert >= 0` (line 173). `baueGeldfluss` [VERIFIED: `geldfluss.ts:233-262`] computes `minderaufwand = -planZeile('globaler_minderaufwand', jahrIndex)` and throws `'Globaler Minderaufwand ist positiv: Datenfehler'` (line 261) when it is negative (i.e. Z. 27 > 0). To test "Z. 27 > 0 throws" in both places without mutating the imported JSON, extract a pure helper (e.g. in `lib/berechnung.ts`, which is documented as "Reine Funktionen ohne Datenzugriff") that takes `(zeile27: number | undefined, jahr: number)` and returns the positive amount, `0`/`null` for absent or zero, and throws with a message that starts with the existing phrase and names the year (UI-SPEC wording). Both call sites use it. Existing tests: `aufwandsarten.test.ts:223-280` (real years 2024 null, 2025-2029 amount).

### Pattern 5: Per-tile source pages and labels (D-10, D-11, 06/IN-07)

`stellenSummen(daten = stellenplan)` returns one union `pdfSeiten` (`stellen.ts:122-133`, built from `[...hj, ...vj, ...besetzt]`). Add per-tile arrays (e.g. `seitenHaushaltsjahr`, `seitenVorjahr`, `seitenBesetzt`) next to the union. **Keep the union field and `belegSchluessel.seite(summen.pdfSeiten[0] ?? 0)`** (`StellenplanPage.vue:68`) unchanged so `quellen.json` and the belege keys stay byte-identical (the card-level `teilQuelle` at `StellenplanPage.vue:~147` also uses the union and should stay on it). `nachwuchs()` (`stellen.ts:187-200`): `pdfSeiten` is built from all rows of the two years even when `personen()` returned `null` for a year; return only pages of years that have a value, and `nachwuchsSatz` (`StellenplanPage.vue:~102-113`) then cites exactly the years it names.

Tile flags (`StellenplanPage.vue:~80-120`): today `berechnet` is `diffVorjahr !== null`, `false`, `diffBesetzt !== null`. New: `berechnet: <value present>` for all three (D-10). `kachelZeile` builds `${quelle} · ${seitenText(pages)}` with the tile's own pages; with no value there is no label and no pages.

**Data reality:** hj, vj and besetzt rows are all on pages 284, 285, 286 in the shipped `stellenplan.json`; nachwuchs rows are on 290 [VERIFIED: node scan of `app/src/data/stellenplan.json`]. The D-11 example ("das Haushaltsjahr auf S. 284-289") does not occur, so the visible text on `/stellenplan` does not change in real data except for the new label on tile 2. Tests must pass a constructed `Stellenplan` (`stellenSummen`/`nachwuchs` already take `daten`) with differing pages per merkmal/jahr.

### Pattern 6: `zusammen()` and the Zuschuss "Zusammen" row (D-12)

`zusammen(gruppe)` [VERIFIED: `lib/zuschuesse.ts:138-144`] returns the printed `gesamt` if present, else the sum of present posten values, else `null`. Change to `{ wert, berechnet } | null` (`berechnet` true iff `gesamt === null`). `transfer` always has `gesamt: null` (line ~126), `kita` and `lfdZwecke` use `gesamt_vorbericht`.

`ZuschussListe.vue` builds `zusammenText: summe === null ? null : 'Zusammen rd. …'` (line 84) as a string used in two places: the body row `<p v-if="gruppe.titel && gruppe.zusammenText">` (only for groups with a title, i.e. `transfer`, `lfd`) and, for the kita card, as the `ChartCard` `beschreibung` string (`kita.zusammenText ?? 'Zuschuss je Einrichtung.'`, line ~135). The `beschreibung` prop is a plain string, so a label component cannot go there. **Planner decision needed:** for the kita card the printed total (S. 46) means no label is needed today; if `gesamt` were ever missing the derived sum would show in the description without a label. Recommended: keep the printed-total description as is, and when `berechnet` is true render the "Zusammen" row in the body with `EuroBetrag` (+ label) and fall back to `'Zuschuss je Einrichtung.'` in the description.

**Starting list for the D-12 survey** ("weitere abgeleitete Summen", UI-SPEC says the list is a start, not a limit). My read of the code, to be confirmed by the planner:
- `lib/investitionen.ts` `ergebnisText` (`:~214`): `${anzahlText(...)} · zusammen ${euroKurz(summe)}` is an aria-live sum of displayed projects, derived and unlabelled. Text-only; a visible label cannot be a component inside the live string.
- `pages/InvestitionenPage.vue:~44-52` VE tile: `berechnet: false`; `veGesamt()` sums `ve_faelligkeiten` rows, the comment says it equals the printed VE cell of the Gesamtfinanzplan row and cites that row as the belege key, so it can be argued as printed.
- `lib/finanzierung.ts` (`:~99`, `:~110`, `:~329`): `einzahlungsAufteilung` sums are checked against the printed GFP total (`gedruckt`) rather than displayed as a new total; likely no label needed.
- `components/BindungsgradBalken.vue:120`: already carries `Summen und Anteile <BerechnetEtikett />`.
- `lib/einnahmen.ts:~315`: the remainder row `sonstige` is already `berechnet: true`.
Record the outcome as "geprüft, Etikett nötig / nicht nötig" per UI-SPEC.

### Pattern 7: `DatenTabelle` (D-16, D-19, D-20, A11Y-01/03)

Current template [VERIFIED: `DatenTabelle.vue:147-263`]: outer `div.om-tabelle-rahmen` with `:role="scrollbarBenannt ? 'region' : undefined"`, `:aria-label="scrollbarBenannt ? beschriftung : undefined"`, `:tabindex="ueberlaeuft ? 0 : undefined"`; `scrollbarBenannt = ueberlaeuft && !!beschriftung` (line 130); data-mode `<caption v-if="beschriftung" class="om-visually-hidden">`; slot-mode `<table v-else>` with visible `<caption>` and `<slot />`; prop `beschriftung?: string` (line 10). All 29 call sites pass `beschriftung` and `:zeilen` [VERIFIED: parsed every `<DatenTabelle` opening tag this session; my first regex flagged `ProduktPage.vue:167` only because `>` inside `length > 0` truncated the tag, the real tag has both].

Changes:
- `beschriftung: string` (required). Remove the default slot and the slot-mode table, update the `defineSlots` block, drop `istDatenModus`, simplify the `watch([...])` accordingly, keep `zelle`/`zeilenzusatz` slots. Put the D-16 deviation note in the component comment and commit message.
- `<caption :id="captionId" class="om-visually-hidden">` always rendered; `captionId = useId()` (Vue 3.5; `ChartCard.vue:2,13` already uses `useId` for `aria-labelledby`).
- Frame gets all three attributes together only when `ueberlaeuft`: `tabindex="0"`, `role="region"`, `aria-labelledby="{captionId}"`; never `aria-label`.
- **vitest limitation:** SSR (`renderToString`) never mounts, so `ueberlaeuft` stays false and the attributes can never be observed in unit tests (this is the same limitation behind 05/IN-02 and 06/IN-09). Put the attribute decision into a pure function in `components/datenTabelle.ts` (for example `rahmenAttribute(ueberlaeuft, captionId)` returning `{}` or the three attributes) and bind it with `v-bind`. Unit-test the function and, via SSR, that the caption is always present, carries an `id` and that no `aria-label` is rendered. The real overflow behaviour is proven by Playwright at 360 px.
- `zustaende.test.ts` (`components/__tests__/`) renders `DatenTabelle` without `beschriftung` in all three cases; add the prop. `vue-tsc` will not flag the test (props are passed as `Record<string, unknown>`), so update by hand.

**Accessibility-tree evidence (D-20)** [VERIFIED: Playwright `ariaSnapshot()` against the production build at 360 px, `/investitionen` with all `wa-details` opened]: the current markup (`aria-label` plus caption) and the `aria-labelledby` variant produce the identical tree:
```
- region "Investitionsmaßnahmen 2026–2029":
  - table "Investitionsmaßnahmen 2026–2029":
    - caption: Investitionsmaßnahmen 2026–2029
```
So after D-20 the text exists once in the DOM, but a region and a table both carry the same accessible name, and the caption is also exposed. Whether a screen reader reads that twice (on entering the region, then the table) is not verifiable here. The pattern `role="region"` + `aria-labelledby` + `tabindex="0"` is the documented one for scrollable tables [CITED: adrianroselli.com/2020/11/under-engineered-responsive-tables.html; the full page returned HTTP 403 to the fetch tool, content taken from a search summary]. Treat the doubled-announcement question as open (assumption A1) and keep the UI-SPEC fallback (only one carrier of the name) available; do not block the phase on it.

Measured at 360 px on all 11 routes with every `wa-details` open: 6 frames overflow on `/einnahmen`, 3 on `/ausgaben`, 2 on `/geldfluss`, 3 of 8 on `/entwicklung`, 6 on `/investitionen`, 4 of 8 on `/rat-entscheidet`, 5 on `/stellenplan`, 3 on `/produkt/010601`; every frame has a caption; region names are unique within each route (no duplicates among table regions) [VERIFIED: probe run in scratch copy].

### Pattern 8: Mobile drawer (D-21, A11Y-02)

Current code [VERIFIED: `App.vue:31-75`]: `oeffneDrawer`, `beiHide`, `beiAfterHide`, watcher on `route.path` that sets `schliesstDurchSeitenwechsel` and `drawerOffen = false`; `beiAfterHide` skips `menueSchalter.focus()` when the flag is set. `RouterLink`s at `:173` (group links) and `:177` (single links) have no click handler.

**Measured baseline (Playwright, 360 px, production build):**
1. Tap on the current-page link: the drawer stays open (`aria-expanded` remains `true`). This is the A11Y-02 bug.
2. Tap on a link to another page: the drawer closes and the page changes, but `document.activeElement` is the menu button (`BUTTON.om-menue-schalter`), not the `h1`. The existing comment ("Nach einem Seitenwechsel gehört der Fokus der neuen Seite") is not what happens.

**Cause** [VERIFIED: `node_modules/@awesome.me/webawesome/dist/chunks/chunk.2UZFSBAI.js:107-111`]: `requestClose` does
```js
const trigger = this.originalTrigger;
if (typeof trigger?.focus === "function") {
  setTimeout(() => trigger.focus());
}
this.dispatchEvent(new WaAfterHideEvent());
```
i.e. it queues a focus restore to the element that was focused when the drawer opened (the menu button) one macrotask after `wa-after-hide`. Any synchronous focus in `beiAfterHide` is overwritten.

**Verified fix** (prototype in a scratch copy; not applied to the repo): add `@click="beiDrawerLinkKlick"` to both `RouterLink`s; the handler sets `schliesstDurchSeitenwechsel = true` and `drawerOffen = false`; `beiAfterHide`, when the flag is set, calls `setTimeout(fokussiereUeberschrift)` (queued after WA's timer, so it runs last) with a shared helper that sets `tabindex="-1"` if missing and focuses `h1` (same logic as the skip-link handler at `App.vue:101-109`). Escape/close button/outside click keep focusing the menu button. `RouterLink` passes `@click` through to its `<a>` and navigation still happens.
Measured result with the prototype, both `reducedMotion: 'no-preference'` and `'reduce'`:

| Action | Drawer | `aria-expanded` | Focus after |
|--------|--------|-----------------|-------------|
| tap current-page link | closed | `false` | `H1` |
| tap other-page link | closed, title changed | `false` | `H1` |
| Escape | closed | `false` | `BUTTON.om-menue-schalter` |

The prototype also passed the whole `ci` project (81 tests) and the `mobil` project (its 14 existing tests; the run also contained my 2 probe tests). This matches the UI-SPEC [Default] ("Fokus auf die h1"), but note that it also changes the other-page case from "button" to "h1", which is what the router logic and the UI-SPEC intended.

### Pattern 9: Einwohner helper (D-09, TXT-06)

Three code paths [VERIFIED]: `lib/kennzahlen.ts:60-66` (`einwohnerZahl`, throws `Error('meta.einwohner.wert muss eine Zahl sein')`), `lib/produkt.ts:157-163` (`einwohnerzahl`, `TypeError` with the same text), `EbenenTabelle.vue:29` (`const einwohner = haushalt.meta.einwohner.wert`) and `:58` (`typeof einwohner === 'number' ? proKopf(...) : null`). `proKopf` (`lib/berechnung.ts:9-14`) already throws for `einwohner <= 0`.
Recommendation: a tiny module `lib/einwohner.ts` exporting `einwohnerZahl()` (reads `haushalt` from `@/data/daten`; `lib/berechnung.ts` is documented as data-free, keep it that way). Message per UI-SPEC: `Einwohnerzahl fehlt in haushalt.json: meta.einwohner.wert muss eine Zahl sein`. In `EbenenTabelle`, call it only when `modus === 'zuschussbedarf'` (the only mode that shows the `proKopf` column, `EbenenTabelle.vue:41-43`), inside the `zeilen` computed, so other modes are not broken by an unrelated missing value. A vitest for the throwing branch needs the helper to accept an injectable meta value (or `vi.spyOn`), because `haushalt` is a static import.

### Pattern 10: Playwright tests to add

Project facts [VERIFIED: `app/playwright.config.ts`]: `ci` (1280x800) ignores `mobil.spec.ts` and `textliste.spec.ts`; `mobil` (360x640) matches only `/mobil\.spec\.ts$/`; CI runs `npm run test:e2e` = `playwright test --project=ci` only. Consequences: tests placed in `mobil.spec.ts` (as D-21 asks) are **not** part of the CI chain. To keep A11Y-02 regression-protected in CI, additionally add the drawer test to `interaktion.spec.ts`, whose existing drawer tests already call `page.setViewportSize({ width: 360, height: 640 })` (`interaktion.spec.ts:~175`, `:~276`). A new test file for the `mobil` project must end in `mobil.spec.ts` or `playwright.config.ts` must change.
- A11Y-02 (above table), plus a "wa-details opened" step is not needed.
- A11Y-01/03: at 360 px on `/investitionen`, open details, assert every `.om-tabelle-rahmen` that has `tabindex="0"` also has `role="region"` and an `aria-labelledby` resolving to a `<caption>` with non-empty text, has no `aria-label`, and `document.documentElement.scrollWidth <= window.innerWidth`; assert region-name uniqueness per route.
- 06/IN-09 `menueVersatz`: viewport about 700 px, open the group "Mehr wissen", assert the list rectangle stays inside `[0, innerWidth]`; resize to 1200 and back to a narrower width and re-assert; read `element.style.left` where behaviour is the point. Source of the logic: `MenueGruppe.vue:36-62` (`positioniere`, `listenVersatz`).
- Prettier covers `e2e/` (`format:check` runs on `src/ e2e/`), so run `npm run format` in the scratch copy.

### Anti-Patterns to Avoid
- **Do not gate the phase on axe `landmark-unique` or `region`.** They are best-practice rules (not in the `wcag2a/aa/21a/21aa` tags used by `smoke.spec.ts:23,92`) and they already report violations at 360 px that come from Web Awesome internals: each opened `wa-details` exposes `role="region"` named by its summary text, duplicated across identical summaries (e.g. `/einnahmen` 3 nodes, even `/glossar` 1 node) [VERIFIED: axe probe]. Assert region-name uniqueness of `DatenTabelle` frames with a custom check instead.
- Do not re-introduce a second text in a `aria-label` for the frame.
- Do not apply `.replace(' ', '\n')`-style splitting on `rd.`-prefixed strings.
- Do not run `git add -A` (CLAUDE.md); stage explicit paths, and use an explicit `git rm`/path for the deleted `beispieldaten.json`.
- Do not mutate the real `app/node_modules` or run app tooling there (macOS binaries).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Amount with "rd." / "rund" | Another `rd. ${...}` string | `betragMitHinweis`, `kurzMitHinweis`, `<EuroBetrag>` | Single authority (D-22). |
| Singular/plural counts | `n === 1 ? 'Person' : 'Personen'` | `anzahlText(anzahl, einzahl, mehrzahl)` in `charts/format.ts` | Already central (06/IN-03 `personenText`). |
| Two-line chart labels | `.replace(' ', '\n')` | `zweizeilig()` in `charts/beschriftung.ts` | Handles NBSP (06/IN-06). |
| Index of the Haushaltsjahr | Five private copies | One `haushaltsjahrIndex()` in `lib/jahr.ts` | 06/IN-03. |
| Placeholder rendering | Own year formatting | `rendereAbsatz` / `formatiere(..., 'jahr')` | No thousands separator for years. |
| Unique ids for ARIA | Hand-made ids | Vue `useId()` | Already used in `ChartCard.vue`. |
| Chart surface colour | Another `getComputedStyle` copy | One exported function in `echartsTheme.ts` | 06/IN-01 (see inventory below). |
| DOM behaviour tests | happy-dom, `@vue/test-utils` | Playwright | D-14. |
| Text validation | Ad-hoc regex in components | `pruefe_text` | Single gate. |

**Key insight:** every fix here is the removal of a second implementation; the risk is leaving one behind, which is why guard tests (rd. rule, year rule) are part of the deliverable.

## Runtime State Inventory

Not a rename/migration phase, but one data deletion and one text-data regeneration are involved.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | `app/src/data/texte.json` (generated, checked in): content changes by design (D-03). `app/src/data/beispieldaten.json`: orphan, nothing imports it (grep over `app/src`, `app/e2e`, `pipeline`, README: only a prop name in `ChartCard.vue`) [VERIFIED]. | Regenerate with `alle.py --jahr 2026`, commit with reason; delete `beispieldaten.json` with reason. |
| Live service config | None - verified: static site, no backend. | None |
| OS-registered state | None - verified: no scheduled tasks or services. | None |
| Secrets/env vars | None - verified: no new variable; Playwright script uses `E2E_SCHRIFT_CACHE` only for font cache. | None |
| Build artifacts | `app/dist` is gitignored; scratch copies must be rebuilt (`npm run build-only`) before Playwright. `quellen.json` and `app/public/quellen/*` must stay unchanged (belege keys stable, D-11). | Re-run `alle.py` and confirm `git status --porcelain -- app/public/quellen` is empty. |

## Common Pitfalls

### Pitfall 1: wa-drawer overwrites focus after `wa-after-hide`
**What goes wrong:** focus ends on the menu button regardless of what the app does synchronously.
**Why:** `setTimeout(() => trigger.focus())` in `chunk.2UZFSBAI.js:109` before the event is dispatched.
**How to avoid:** focus the `h1` in a `setTimeout` queued from `beiAfterHide`; assert focus in Playwright.
**Warning signs:** a test that reads `document.activeElement` immediately after the drawer is hidden passes or fails depending on timing; wait at least one macrotask.

### Pitfall 2: Overflow-dependent attributes are invisible to vitest
**What goes wrong:** a vitest asserting `role="region"` on the frame can never pass (SSR has no layout) or passes vacuously.
**How to avoid:** pure helper + Playwright (Pattern 7).

### Pitfall 3: Pytest fixture `werte` is built without `texte`
**What goes wrong:** keys registered only when `texte` is passed to `textwerte` make `loese_auf(echte_erklaerungen, werte)` fail in `test_texte.py`.
**How to avoid:** resolve `jahr.fest_<JJJJ>` in the resolver (Pattern 2).

### Pitfall 4: Test that asserts "no placeholder" for neutral texts
`test_jahrneutrale_erklaerungen_ohne_platzhalter` (`test_texte.py:~714-722`) asserts `"{{" not in absatz` for `_JAHRNEUTRAL_SCHLUESSEL`, which includes `ueberschuss_pb_11` and `ueberschuss_ruecklage`. After D-03 these contain `{{jahr.fest_…|jahr}}`. Update the test to allow only `jahr.fest_*` placeholders in neutral texts (and keep the check that no amount or relative key appears).

### Pitfall 5: Tests that look green on real data but never hit the boundary
TXT-01 cases C/D, TXT-02 positive Z. 27, TXT-05 differing page sets and TXT-06 missing Einwohner do not occur in shipped data. Every one needs a constructed input; check each new test would fail against the pre-fix code (fail-first).

### Pitfall 6: Scratch copy staleness and native binaries
The real `app/node_modules` has `@rolldown/binding-darwin-arm64`; vitest/vite fail there. Always rsync current `app/` sources into a scratch directory (excluding `node_modules`, `dist`, `test-results`), `npm ci`, run checks there; copy generated `app/src/data/*` into the scratch copy after each `alle.py` run.

### Pitfall 7: `ledger` rows silently dropped by id reuse
The 05 ledger header note says a reused finding id replaces an earlier row. The older 05 review round (commit `ce51941`) had different IN-01 to IN-04; they are not in the ledger any more (see Open Question 1).

### Pitfall 8: Visible change of chart labels from 06/IN-06
`euroKurz(wert).replace(' ', '\n')` (`RuecklagenBalken.vue:59`, `ErgebnisBalken.vue:30`) only splits "21,3 Mio. €" (regular space); amounts under 1 Mio. use `euro()` with a NBSP and stay on one line today. `zweizeilig()` splits both. This is a deliberate small rendering change for sub-million labels; mention it in the commit.

## Code Examples

### Pure attribute helper (Pattern 7)
```ts
// components/datenTabelle.ts (new export; unit-testable without layout)
export function rahmenAttribute(
  ueberlaeuft: boolean,
  captionId: string,
): Record<string, string | number> {
  return ueberlaeuft ? { tabindex: 0, role: 'region', 'aria-labelledby': captionId } : {}
}
```
```vue
<div ref="rahmen" class="om-tabelle-rahmen" v-bind="rahmenAttribute(ueberlaeuft, captionId)">
  ...
  <caption :id="captionId" class="om-visually-hidden">{{ beschriftung }}</caption>
```

### Drawer fix (Pattern 8), verified prototype
```ts
function fokussiereUeberschrift() {
  const ziel = document.querySelector<HTMLElement>('h1')
  if (ziel !== null) {
    if (!ziel.hasAttribute('tabindex')) ziel.setAttribute('tabindex', '-1')
    ziel.focus()
  }
}
function beiDrawerLinkKlick() {
  schliesstDurchSeitenwechsel.value = true
  drawerOffen.value = false
}
// in beiAfterHide, flag branch:
//   schliesstDurchSeitenwechsel.value = false
//   setTimeout(fokussiereUeberschrift) // wa-drawer holt den Fokus selbst per setTimeout zurück
```

### Constructed-data test for TXT-01 (Pattern 3)
```ts
const knoten = (art: KnotenArt, wert: number, seite: KnotenSeite): GeldflussKnoten => ({
  id: `${art}`, name: art, wert, seite, art, code: null, farbe: '#000',
  gerundet: false, berechnet: false,
})
const nurMinderaufwand: Geldfluss = {
  knoten: [knoten('minderaufwand', 600_000, 'links')],
  kanten: [], summeLinks: 600_000, summeRechts: 600_000, pdfSeite: 51,
}
expect(lesehilfeSatz(nurMinderaufwand, 2026, 'Ansatz')).not.toContain('genau')
```

### pytest for TXT-03
```python
@pytest.mark.parametrize("text", ["im Jahr 2026", "2022 kamen 5 ", "von 2020 bis 2024", "1900", "2099"])
def test_pruefe_text_lehnt_getippte_jahreszahl_ab(text):
    with pytest.raises(TexteFehler, match="Jahreszahl"):
        pruefe_text(text)

def test_pruefe_text_erlaubt_jahr_nur_als_platzhalter():
    pruefe_text("im Jahr {{jahr.haushaltsjahr|jahr}} und {{jahr.fest_2022|jahr}}")
```

## Per-requirement implementation map (files and lines)

| Req | Where | Notes |
|-----|-------|-------|
| TXT-01 | `lib/geldfluss.ts:653-686` | Pattern 3. |
| TXT-02 | `lib/aufwandsarten.ts:167-186`, `lib/geldfluss.ts:259-263` | Pattern 4. 53b96ac already hides negatives. |
| TXT-03 | `pipeline/ostbevern/texte.py:44,189-232`, `app_daten.py:1112-1116`, `erklaerungen.md`, `lib/texte.ts:62-64` | Pattern 2. `app_daten.py` is where all paragraphs (not titles) pass `pruefe_text` today. |
| TXT-04 | 17 sites (Pattern 1), `EuroBetrag.vue:3,5-8` | Pattern 1. |
| TXT-05 | `lib/stellen.ts:122-133,187-200`, `pages/StellenplanPage.vue:60-124`, `lib/zuschuesse.ts:138-144`, `components/ZuschussListe.vue:65-135` | Patterns 5, 6. |
| TXT-06 | `EbenenTabelle.vue:29,58`, `lib/kennzahlen.ts:60-66`, `lib/produkt.ts:157-163` | Pattern 9. |
| A11Y-01/03 | `components/DatenTabelle.vue` | Pattern 7. |
| A11Y-02 | `App.vue:37-75,173,177` | Pattern 8. |

## Review-finding triage (28 open findings)

Counts verified against the three ledgers: 01 has IN-01..IN-05 open (5), 05 has WR-01, WR-02, IN-01..IN-11 open (13), 06 has WR-01, IN-01..IN-09 open (10); total 28 [VERIFIED: ledger frontmatter `open: 5/13/10`]. "Work" below is my assessment of what the fix needs; the disposition is per D-13/D-17.

| ID | Finding | Disposition | Work needed (file) | Evidence for ledger |
|----|---------|-------------|--------------------|---------------------|
| 01/IN-01 | `bars.svg` unused | fixed | none; `App.vue:149` has `<wa-icon name="bars" aria-hidden="true">` | 1c14077 |
| 01/IN-02 | duplicate `pdf_relativ` | fixed | `pipeline/alle.py:~48-58`: compute once before the `is_file()` check | new commit |
| 01/IN-03 | `circle-info` in warning callout | fixed | `ChartCard.vue:~39` icon to `triangle-exclamation` (file exists under `app/public/icons/solid/`); delete `app/src/data/beispieldaten.json` | new commit (deliberate `app/src/data/` change) |
| 01/IN-04 | no `>= 0` for `anzahlen.*` | fixed | `pipeline/ostbevern/konfiguration.py` loop at `~:149-155`; overlap check already exists (`~:186-196`); add test in `test_konfiguration.py` | new commit |
| 01/IN-05 | double labelling of tables | fixed | A11Y-01/03 | commit of D-19/D-20 |
| 05/WR-01 | rd. half migrated | fixed | TXT-04 | commit of D-22 |
| 05/WR-02 | tab stop without role/name | fixed | A11Y-01 | commit of D-19 |
| 05/IN-01 | `alsRgb` rejects `#010203`-normalising colour | fixed | `charts/echartsTheme.ts:~149-176`: two-marker comparison per review; browser-only (canvas), not unit-testable under `environment: 'node'`, verify by type-check, build and smoke | new commit |
| 05/IN-02 | no re-observe on slot swaps | fixed (obsolete) | slot mode removed by D-16 | commit of D-16 |
| 05/IN-03 | vacuous negative assertion | fixed | `geldfluss.test.ts:~213-218`: add positive assertion for the same edge (`toContain(euro(kante.wert))`) or a right-hand `gerundet: true` fixture | new commit |
| 05/IN-04 | token guard limits | fixed | `stiltokens.test.ts:1-36`: header sentence naming both limits; skip names ending in `-` with a clear message | new commit |
| 05/IN-05 | drawer stays open | fixed | A11Y-02 | commit of D-21 |
| 05/IN-06 | "genau aus" | fixed | TXT-01 | commit of D-06 |
| 05/IN-07 | negative Minderaufwand | fixed | 53b96ac + unification commit (D-08) | 53b96ac, new commit |
| 05/IN-08 | silent column drop | fixed | TXT-06 | commit of D-09 |
| 05/IN-09 | placeholder contact data | fixed | none; `config.ts` holds real values, `config.test.ts` guard and `.invalid` check in `smoke.spec.ts` exist | 1ab6b4b, b29be89, f4fad93 [VERIFIED: commits exist, titles match] |
| 05/IN-10 | years 1900-2099 pass | fixed | TXT-03 | commit of D-01 |
| 05/IN-11 | doc/tooling drift | fixed | (a) `.claude/CLAUDE.md:56-60` CI block: add the pipeline reproducibility step and the Playwright step; (b) `.github/workflows/ci.yml:10-12` header still says "Es gibt noch kein GitHub-Remote"; (c) `lies_glossar` check that `absaetze[0]` has no `{{` (current data complies, 0 of 27 violate [VERIFIED: node scan]); `@types/node` item is already done (`package.json` has `@types/node ^22.20.5`, `@tsconfig/node22`) | new commit(s) |
| 06/WR-01 | footnote sign wording | skipped | reasoned by UAT 06 test 1 (`result: pass`) and `PROJECT.md:138`; still clarify the two "plus" comments at `lib/ruecklagen.ts:~91` and `ruecklagen.test.ts:~212-213` | UAT 06 + PROJECT.md:138 |
| 06/IN-01 | hex fallbacks | fixed | Remaining sites: `charts/wertartStil.ts:39,44` (`'white'`), `lib/geldfluss.ts:590,595` (`'#ffffff'`, `trennerFarbe`), `components/AufwandTreemap.vue:39,58` (local `token` copy + `'#ffffff'`), `components/SchuldenstandDiagramm.vue:30` (`'white'`). The Stellen colours were already moved by 3260357 (`NEUTRAL_*_FARBE` in `echartsTheme.ts:62-64`). Export one **function** (not a module-level constant: `wertartStil.flaechenFarbe()` reads the token lazily at call time, a constant would read it once at import) from `echartsTheme.ts` and use it in all places | new commit |
| 06/IN-02 | dead/test-only exports | fixed | `ausgleichsruecklageAufgebrauchtJahr` (`lib/ruecklagen.ts:~195-207`): switch to the existing `haushaltsjahrIndex()` (keeps its 6 tests and the Python twin rule); `menueLinks` is **not** dead, `e2e/routen.ts:3` imports it, leave it | new commit |
| 06/IN-03 | duplicated helpers | fixed | Index helpers: `zuschuesse.ts:49 jahrIndex`, `kennzahlen.ts:44 jahrIndex`, `bindungsgrad.ts:69 jahrIndex`, `ruecklagen.ts:219 haushaltsjahrIndex`, `investitionen.ts:58 planAb` -> one `haushaltsjahrIndex()` in `lib/jahr.ts`; `wertartAn`: `ruecklagen.ts:64`, `entwicklung.ts:56` -> one; `postenName` vs `postenWerte` (`ruecklagen.ts:~45-51,~125-132`) -> `postenEintrag()`; `personenText` (`StellenplanPage.vue:~96-98`) -> `anzahlText`. Check tests that assert the old error strings before unifying messages | new commit |
| 06/IN-04 | coupling | fixed | `quellenZeile` (`lib/kennzahlen.ts:38`, imported by `schulden.ts:25`, `NichtBeeinflussbarBlock.vue:10`, `StartPage.vue:11`, `InvestitionenPage.vue:19`), `jahreListe` (`lib/schulden.ts:92`, imported by `FinanzierungsDiagramm.vue:17`), `klickIndex` (`lib/investitionen.ts:224`, imported by `ProduktBalkenListe.vue:13`) to slim modules; `EuroBetrag` -> `geldfluss` coupling disappears with D-22 | new commit |
| 06/IN-05 | filter instantiated twice | fixed | `useMassnahmenFilter()` at `MassnahmenFilter.vue:16` and `InvestitionenPage.vue:70`; call once in the page and pass down (props or provide/inject); the composable reads/writes the URL (`pb`, `art`) | new commit |
| 06/IN-06 | nits | fixed | `VeFaelligkeiten.vue:51` key without separator; `EntwicklungsDiagramm.vue:54` `!= null`; `EntwicklungPage.vue:40,47` `== null`; `RuecklagenBalken.vue:59`, `ErgebnisBalken.vue:30` `.replace` -> `zweizeilig()` (Pitfall 8) | new commit |
| 06/IN-07 | derived sum label and tile pages | fixed | TXT-05 | commit of D-10/D-11/D-12 |
| 06/IN-08 | untyped pipeline errors | fixed | `texte.py:~326-331`: `anfang == 0` raises `TexteFehler` naming the formula; missing keys are already wrapped by `_mit_eingabepruefung` (`texte.py:~360-372`); add a test | new commit |
| 06/IN-09 | tests read source | fixed | D-14; list of `?raw` test files below | commit of D-14 |

`?raw` tests that stay but need a reason comment (D-14): `quelltext.test.ts`, `stiltokens.test.ts`, `duanrede.test.ts`, `menue.test.ts`, `hinweis.test.ts`, `glossar.test.ts:203`, `quelle*.test.ts`, `kennzahlen.test.ts`, `stellen.test.ts:267`, `entwicklung.test.ts:351`, `schulden.test.ts:9`, `bindungsgrad.test.ts:197`. Remove: the `menueVersatz.test.ts` block "Verdrahtung in MenueGruppe.vue" (`~:152-155`) with the `?raw` import at `:5-8`, and `ruecklagen.test.ts:~305-308`.

**Ledger mechanics** [VERIFIED: the three `…-REVIEW-DISPOSITION.md` files]: frontmatter has `findings:` list entries (`id`, `severity`, `disposition`, `title`), `open: N`, `total: N`, `recorded:`; the table has `| Finding | Severity | Disposition | Source |`; Source of a fixed row looks like `fixed in 06-13 (gate 06-17)`; `deferred` and reasons are hand-set. Edit both the frontmatter `disposition:` and the table row for each finding, set `open: 0`, leave `total` unchanged. The 06 ledger footer explains that the id `WR-01` was reused by the current review and that the earlier WR-01 decision is recorded in prose; keep that footer. The ledger tool is advisory and "keeps every decision it can" when re-run, so hand edits are safe.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Tab stop on a scrollable container without role/name | `tabindex="0"` + `role="region"` + `aria-labelledby` to the caption | established pattern (Roselli 2020) | A11Y-01/03 |
| Close drawer only via route watcher | Close on link click plus a deferred focus step | wa-drawer 3.14 restores focus itself | A11Y-02 |

**Deprecated/outdated:** the `EuroBetrag.vue` doc comment ("Die Regel steht nur hier") - false today, corrected by D-22.

## Corrections to upstream premises

These are facts found in the code or by running it that differ from CONTEXT/UI-SPEC statements. Each needs a planner decision or a visible adoption in the plan.

1. **Drawer focus** (UI-SPEC "Mobiles Menü"): "Fokus geht auf die h1 der neuen Seite (Router-Verhalten, unverändert)" is not what happens today; focus lands on the menu button (Pattern 8). Adopting the verified fix changes the other-page case too.
2. **axe coverage** (UI-SPEC E6 zero-one-many and A11Y Belege): "axe `landmark-unique` auf jeder Route bei 360 px und 1280 px" and "der axe-Smoke-Test (jede Route …, bei 360 px und 1280 px) deckt das ab" are not true: `smoke.spec.ts` runs only in the `ci` project (1280 px) with WCAG tags; the `mobil` project has no axe. Either add an axe pass at 360 px (WCAG tags; `@axe-core/playwright` is already a dependency) in `mobil.spec.ts`, or reword the verification to the custom uniqueness check. Do not add `landmark-unique` as a gate (Anti-Patterns).
3. **D-11 example pages**: the shipped data has identical page sets for all three tiles (S. 284-286); only constructed data shows the effect.
4. **D-20**: switching to `aria-labelledby` does not change the accessibility tree (region and table both named); it removes duplicated attribute text only. See Assumption A1.
5. **D-05**: titles may not contain placeholders (they are never resolved); reject `{{` in titles in addition to running `pruefe_text`.
6. **D-14 / Playwright projects**: `mobil` is not run in CI; mirror at least the A11Y-02 test into the `ci`-project spec so the regression is gated.
7. **06/IN-02**: `menueLinks` is used by `e2e/routen.ts`, not dead.
8. **D-12 kita card**: the "Zusammen" string for the kita group goes into a plain-text `ChartCard` description, where a label cannot be rendered (Pattern 6).
9. **UI-SPEC claim "UI-SPEC E3 backstop"** that long source lines etc. are covered: no existing test covers 6+ page source lines at 360 px beyond the generic overflow measurement in `mobil.spec.ts` (`scrollWidth <= innerWidth` per route), which still passes; acceptable as the backstop.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | A screen reader announces the name of a scroll region and its table separately but not harmfully (Roselli pattern accepted); no real SR was run | Pattern 7, A11Y-03 | A11Y-03 could remain "doubled" for some SR; fallback is to let only one element carry the name (UI-SPEC allows it). Needs one manual VoiceOver/NVDA check, listed as a human item. |
| A2 | Content of Roselli's article (`role="region"`, `aria-labelledby`, `tabindex="0"`, `overflow: auto`, focus outline) as summarised by a web search; the page itself returned 403 | Pattern 7 | Low; the pattern is standard and matches the UI-SPEC citation. |
| A3 | The four older 05 findings (IN-01 "-0 €", IN-02 hard-coded superlative, IN-03 singular "PDF-Seite" for several pages, IN-04 `useJahr` redirect watchers) are out of scope for this phase | Open Questions | If the user wants them closed, 4 extra small fixes or ledger rows are needed. |
| A4 | `jahr.fest_<JJJJ>` parsed from the key is acceptable under the "no Jahrgang values in code" rule | Pattern 2 | If the user insists on TOML, `textwerte`/`loese_auf` need the `Jahrgang` object and the fixture changes. |
| A5 | Changing sub-million chart labels to two lines via `zweizeilig()` is acceptable | Pitfall 8 | Visible but harmless; could be limited to `>= 1 Mio.` with a comment. |
| A6 | The `rund` NBSP in Satz 1 of the Lesehilfe (UI-SPEC [Default]) is acceptable | Pattern 1 | Changes a plain space to a NBSP in visible text only. |

## Open Questions

1. **Orphaned older 05 findings.** The 05 ledger lists IN-01..IN-04 from the newest review round (alsRgb, slot-mode observer, vacuous test, token guard). The first review round (commit `ce51941`) had different IN-01..IN-04 which were `open` and were silently replaced by id reuse: "-0 €" from `proKopf`/`Intl` (`lib/berechnung.ts:13`; `Intl` prints `-0 €` for `Math.round(-0.3)`, I ran it), hard-coded "Der größte Einzelposten …" (`KreisumlageCallout.vue:~46`), "PDF-Seite" singular for several pages (`ErklaerText.vue:~22,29`, partially), `useJahr` redirect watchers (`lib/jahr.ts:~96-107`). I confirmed three still exist in the code. They are not among the 28 and not in any requirement.
   - Recommendation: do not expand scope silently; record them as a note in the plan summary and let the user decide (one trivial fix, `-0` via `+ 0`, fits TXT's spirit). If added to the ledger, they need new ids.
2. **Kita "Zusammen" when berechnet** (Pattern 6): confirm the recommended handling.
3. **Where to run the manual a11y check (A1)**: user-side human verification, consistent with `human_verify_mode: end-of-phase`.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node | scratch app checks | yes | v22.22.1 (`engines ^22.18.0`) | - |
| npm | `npm ci`, scripts | yes | 9.2.0 | - |
| npm registry | scratch `npm ci` | yes | 283 packages installed, exit 0 | - |
| uv | pipeline | yes | 0.9.26 | - |
| Python | pipeline | yes (uv-managed 3.12.12) | `pipeline/.venv` is Linux aarch64 | - |
| Docker daemon | Playwright, `e2e-wie-ci.sh` | yes | 29.8.1 | - |
| Playwright image | e2e | yes | `mcr.microsoft.com/playwright:v1.63.0-noble` already pulled | - |
| Playwright chromium on host | direct `npx playwright test` | **no**; `playwright install` fails (download blocked) | - | use `scripts/e2e-wie-ci.sh <scratch-app>` (works; font package download succeeded) |
| `app/node_modules` in the real repo | app tooling | **no for this OS** (macOS rolldown binding) | - | scratch copy |
| Real screen reader (VoiceOver/NVDA) | A11Y-03 doubled-announcement check | no | - | human item |
| Lighthouse | a11y score >= 95 | not installed; `scripts/lighthouse-a11y.sh` installs `lighthouse@13.5.0` after a user package approval from phase 7 | - | optional; axe + a11y e2e are the automated evidence |

**Missing dependencies with no fallback:** a real screen reader (human check only).
**Missing dependencies with fallback:** host Playwright browser (docker script), real-repo `node_modules` (scratch copy).

**Working recipe (executed this session):**
```bash
SP=<scratch dir>
rsync -a --exclude node_modules --exclude dist --exclude test-results app/ $SP/app/
(cd $SP/app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run test && npm run build-only)
scripts/e2e-wie-ci.sh $SP/app                      # project ci (as CI)
scripts/e2e-wie-ci.sh $SP/app --project=mobil      # 360 px
# pipeline runs in place (Linux .venv):
uv run --directory pipeline pytest ; uv run --directory pipeline ruff check . ; uv run --directory pipeline ruff format --check .
uv run --directory pipeline python alle.py --jahr 2026
git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen
```
After `alle.py`, re-sync `app/src/data` into the scratch app and rebuild. For the one pytest that compares the Python format port with the real `format.ts` (`test_formatiere.py::test_port_wie_format_ts`), `app/node_modules/typescript` must exist: it is skipped in a repo copy without it; in the real repo `typescript` is plain JS and is expected to be found, or link the scratch `node_modules` in.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | vitest 5.0.3 (node env, SSR render, `?raw` globs); Playwright 1.63.0 + axe 4.13.0; pytest 9.1.1; ruff 0.16.9 |
| Config file | `app/vitest.config.ts` (`include: ['src/**/__tests__/*.test.ts']`), `app/playwright.config.ts`, `pipeline/pyproject.toml` (`testpaths = ["tests"]`) |
| Quick run command | vitest single file in scratch: `npx vitest run src/lib/__tests__/<file>.test.ts` (whole suite takes ~2 s); pytest single file: `uv run --directory pipeline pytest tests/test_texte.py -q` (0.06 s) |
| Full suite command | App chain in scratch (type-check, lint, format:check, test, build-only), `scripts/e2e-wie-ci.sh <scratch>/app` plus `--project=mobil`; `uv run --directory pipeline pytest` (full run is 5 min 44 s in this sandbox); `alle.py --jahr 2026` (29 s) |

Baselines measured this session: vitest 45 files / 1968 tests; Playwright `ci` 81 tests / 35 s; `mobil` 14 tests / about 10 s; pytest 645 passed 1 skipped; slowest pytest file `test_app_daten.py` 25 s (relevant to D-03), `test_texte.py`/`test_formatiere.py`/`test_konfiguration.py`/`test_alle.py` together about 2 s.

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TXT-01 | Cases A-D, "genau" only in D, case C with `gerundet` | unit (constructed `Geldfluss`) | `npx vitest run src/lib/__tests__/geldfluss.test.ts` | extend existing |
| TXT-02 | 2024 -> no hint, 2025-29 positive amount, constructed Z. 27 > 0 throws in `aufwandsarten` and `geldfluss` with the same message | unit | `npx vitest run src/lib/__tests__/aufwandsarten.test.ts src/lib/__tests__/geldfluss.test.ts` | extend existing |
| TXT-03 | typed 1900-2099 rejected with clear message; placeholders accepted; titles checked; fixed-year resolver; sections converted | pytest + vitest | `uv run --directory pipeline pytest tests/test_texte.py tests/test_app_daten.py -q`; `npx vitest run src/lib/__tests__/texte.test.ts` | extend existing |
| TXT-04 | no `rd.` + space copy outside `charts/format.ts`; adapted tests | unit (guard via `?raw` glob) + existing | `npx vitest run src/lib/__tests__/quelltext.test.ts src/lib/__tests__/zeitreihen.test.ts src/lib/__tests__/drilldown.test.ts src/lib/__tests__/geldfluss.test.ts src/charts/__tests__/format.test.ts` | extend; new guard test (Wave 0) |
| TXT-05 | per-tile pages from constructed `Stellenplan`; all tiles labelled; `zusammen()` `{wert, berechnet}`; `nachwuchs` only pages of years with value | unit | `npx vitest run src/lib/__tests__/stellen.test.ts src/lib/__tests__/zuschuesse.test.ts` | extend existing |
| TXT-06 | `einwohnerZahl()` throws with "fehlt in haushalt.json"; `EbenenTabelle` has no "-" column fallback | unit | `npx vitest run src/lib/__tests__/einwohner.test.ts` | new file (Wave 0) |
| A11Y-01 | frame attributes together (pure helper); caption always, with id, no `aria-label`; prop required | unit (+ `vue-tsc`) | `npx vitest run src/components/__tests__/zustaende.test.ts` and `npm run type-check` | extend existing |
| A11Y-01/03 | at 360 px every overflowing frame has role, name via caption, no `aria-label`; no page-level horizontal scroll; unique region names | e2e `mobil` | `scripts/e2e-wie-ci.sh <scratch>/app --project=mobil e2e/mobil.spec.ts` | extend `mobil.spec.ts` |
| A11Y-02 | drawer closes on current-page and other-page tap; `aria-expanded` false; focus on `h1` not button; Escape still returns focus to button | e2e `mobil` (+ mirror in `ci` spec) | same, plus `scripts/e2e-wie-ci.sh <scratch>/app e2e/interaktion.spec.ts` | extend `mobil.spec.ts`, `interaktion.spec.ts` |
| 06/IN-09 | `menueVersatz` behaviour after resize | e2e | `scripts/e2e-wie-ci.sh <scratch>/app e2e/interaktion.spec.ts` | extend |
| 01/IN-03 | icon is `triangle-exclamation`, file exists | unit | `npx vitest run src/components/__tests__/chartcard.test.ts` (name free) | new (Wave 0) |
| 01/IN-04 | negative `anzahlen.*` rejected | pytest | `uv run --directory pipeline pytest tests/test_konfiguration.py -q` | extend |
| 06/IN-08 | `anfang == 0` -> `TexteFehler` | pytest | `uv run --directory pipeline pytest tests/test_texte.py -q` | extend |
| TRI-01..03 | no row `| open |`, frontmatter `open: 0`, non-empty Source for every changed row | scripted check | `grep -c "disposition: open" <ledger>` and `grep -c "| open |" <ledger>` both 0; `grep -n "^open:" <ledger>` shows `open: 0` | n/a |
| TRI-04 | hygiene fixes keep data identical | cross | `alle.py --jahr 2026` + `git status --porcelain -- daten app/src/data app/public/quellen` shows only the intended `texte.json` change and the `beispieldaten.json` deletion | n/a |
| Cross-cut | rules 1-10 green, 1 EUR tolerance unchanged | pipeline | `alle.py` output lines `Schritt 06: Regel N: grün`; full pytest | existing |

### Sampling Rate
- **Per task commit:** the single affected vitest file(s) or pytest file (seconds), plus `npm run type-check` for any `.vue`/`.ts` edit.
- **Per wave merge:** full vitest, type-check, lint, `format:check`, build; Playwright `ci` project; for pipeline waves `pytest tests/test_texte.py tests/test_app_daten.py tests/test_konfiguration.py tests/test_formatiere.py` and `ruff`.
- **Phase gate:** the complete CI chain from CLAUDE.md in scratch copies (including `mobil` project and the pipeline reproducibility diff), full pytest, then `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `app/src/lib/__tests__/einwohner.test.ts` — TXT-06.
- [ ] guard test for the "rd." rule (new file or block in `quelltext.test.ts`) — TXT-04.
- [ ] `app/src/components/__tests__/chartcard.test.ts` (or block in an existing file) — 01/IN-03.
- [ ] new tests in `app/e2e/mobil.spec.ts` / `interaktion.spec.ts` — A11Y-01/02/03, 06/IN-09.
- [ ] No framework installs needed.

## Security Domain

`security_enforcement` is enabled (absent = enabled; config shows `true`, `security_asvs_level: 1`). The phase has no new inputs, endpoints or dependencies; the relevant surface is the text pipeline and rendering of generated strings.

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | static site, no accounts |
| V3 Session Management | no | none |
| V4 Access Control | no | none |
| V5 Input Validation | yes | `pruefe_text` (HTML-char ban, placeholder grammar, digit/year rule), `rendereAbsatz` (unknown key shows "–", unknown format throws), Vue text interpolation only (no `v-html`; `getippteZahlen` guard test already flags the raw-HTML directive) |
| V6 Cryptography | no | none |
| V14 Configuration | yes | no third-party requests at runtime (smoke test checks every request origin and `.invalid`), CI actions pinned by SHA (unchanged) |

### Known Threat Patterns
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Markup in curated text reaching the DOM | Tampering | `pruefe_text` rejects `<` and `>`; titles also checked (D-05); render via interpolation |
| Unresolved placeholder shown to users | Information/Integrity | `loese_auf` fails the build; reject placeholders in titles |
| Tooltip HTML injection from data strings | Tampering | `tooltipZeilen`/escape in `charts/tooltip.ts` (unchanged; new `rd.` strings contain no markup) |
| Supply chain | Tampering | no new packages (D-14) |
| Silent wrong number | Integrity | throw on data errors (D-08, D-09), byte-identity gate on generated data |

## Sources

### Primary (HIGH confidence)
- Repository files read this session (paths and lines cited inline): `app/src/App.vue`, `components/DatenTabelle.vue`, `EuroBetrag.vue`, `EbenenTabelle.vue`, `ZuschussListe.vue`, `ChartCard.vue`, `lib/geldfluss.ts`, `aufwandsarten.ts`, `stellen.ts`, `zuschuesse.ts`, `texte.ts`, `charts/format.ts`, `pipeline/ostbevern/texte.py`, `konfiguration.py`, `app_daten.py`, `alle.py`, `daten/manuell/texte/erklaerungen.md`, `.github/workflows/ci.yml`, `scripts/e2e-wie-ci.sh`, `app/playwright.config.ts`, `app/e2e/*.spec.ts`, the three review ledgers and review reports (05 older rounds via `git show ce51941:…`, `e70324d:…`).
- Web Awesome 3.14.0 source in `app/node_modules/@awesome.me/webawesome/dist/chunks/chunk.2UZFSBAI.js:107-111` (drawer focus restore).
- Executed in this sandbox: vitest, type-check, lint, prettier, build, Playwright via docker (`ci` 81, `mobil` 14), pytest (645 passed), `alle.py --jahr 2026` (clean diff), Playwright probes (ARIA snapshots, axe rules, drawer focus).

### Secondary (MEDIUM confidence)
- [Under-Engineered Responsive Tables - Adrian Roselli](https://adrianroselli.com/2020/11/under-engineered-responsive-tables.html) (via search summary; the page returned 403 to WebFetch).
- [Scrollable region must have keyboard access - Deque University (axe 4.11)](https://dequeuniversity.com/rules/axe/4.11/scrollable-region-focusable).

### Tertiary (LOW confidence)
- none beyond Assumptions A1-A6.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - nothing new; versions from `package.json`/lockfile and a successful install.
- Architecture/implementation map: HIGH - every file and line read this session, baseline and prototypes executed.
- Pitfalls: HIGH for drawer focus, vitest SSR limits, fixture ordering (reproduced or read); MEDIUM for screen-reader behaviour (A1).

**Research date:** 2026-10-07
**Valid until:** 2026-11-06 (stable codebase; re-check line numbers if other commits land before planning)
