# Phase 8: Fixes und Triage - Context

**Gathered:** 2026-10-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Nacharbeit ohne neue Funktionen. Drei Dinge werden geliefert:

1. Sätze über Zahlen stimmen auch in Grenzfällen. Das betrifft TXT-01 bis TXT-06: Lesehilfe, Minderaufwand-Hinweis, Jahreszahlen in Texten, die „rd.“-Regel, die Kennzeichnung „berechnet“ samt Quellseiten und die fehlende Einwohnerzahl.
2. `DatenTabelle` und das mobile Menü funktionieren für Screenreader und Touch ohne Lücken (A11Y-01 bis A11Y-03).
3. Alle 28 offenen Review-Befunde der Ledger 01, 05 und 06 haben eine Disposition. Jede Disposition nennt einen Beleg-Commit oder eine Begründung, und die Ledger stehen auf `open: 0` (TRI-01 bis TRI-04).

Reihenfolge laut Roadmap: zuerst Zahlen und Texte, dann Barrierefreiheit und Hygiene, zum Schluss die Ledger.

Querschnittsbedingung: `uv run --directory pipeline python alle.py --jahr 2026` erzeugt `daten/` und `app/src/data/` byte-identisch, außer eine Änderung ist bewusst und im Commit begründet. Die Prüfregeln 1–10 bleiben grün, die 1-€-Toleranz bleibt unverändert. Die App-Prüfungen laufen in einer Scratch-Kopie von `app/`. Jeder Fix-Commit nennt die Befund-ID mit Phasenpräfix, z. B. `05/IN-06`.

</domain>

<decisions>
## Implementation Decisions

### Jahreszahlen in Texten (TXT-03, 05/IN-10)
- **D-01:** `pruefe_text` lehnt jede handgetippte Zahl zwischen 1900 und 2099 ab und gibt eine klare Fehlermeldung aus. Die Ausnahme `_JAHR_MUSTER` (`pipeline/ostbevern/texte.py:44`) fällt weg. Jahreszahlen sind nur noch als `{{jahr.…|jahr}}` erlaubt. Dazu kommt ein pytest-Fall. Der Test `pipeline/tests/test_texte.py:388`, der „im Jahr 2026“ heute als gültig führt, wird umgedreht.
- **D-02:** **Gemischtes Schema für Jahres-Platzhalter.** Jahre, die sich auf das Haushaltsjahr beziehen (Vorjahr, Planjahre), werden relativ geschrieben, also über die bestehenden Schlüssel `jahr.haushaltsjahr`, `jahr.vorjahr`, `jahr.letztes_jahr` plus neue Schlüssel wie `jahr.haushaltsjahr_plus_1` oder `jahr.vorvorjahr`. Echte Ereignisjahre bekommen einen ausdrücklich festen Schlüssel, z. B. `{{jahr.fest_2022|jahr}}`. Das betrifft die Gewerbesteuer-Historie 2022/2023 und die Rücklagen „2020 bis 2024“. Jede Jahreszahl ist damit bewusst gesetzt, und ein fester Schlüssel wandert beim nächsten Jahrgang nicht mit. Die Schlüsselnamen legt der Planer fest.
- **D-03:** Alle 7 Abschnitte in `daten/manuell/texte/erklaerungen.md` mit getippten Jahren werden umgestellt: `schluesselzuweisung` (:7), `gewerbesteuer` (:13), `kreisumlage` (:19), `schulden` (:49), `verpflichtungsermaechtigungen` (:55), `ueberschuss_pb_11` (:93) und `ueberschuss_ruecklage` (:109). Für jeden Abschnitt wird geprüft, ob das Jahr relativ (D-02) oder fest ist. `glossar.md` enthält keine getippten Jahre. Die Änderung erzeugt einen bewussten Diff in `app/src/data/texte.json` (`absaetze` und `werte`), der im Commit begründet wird. Die CSVs unter `daten/aufbereitet/` dürfen sich nicht ändern.
- **D-04:** **`jahr.*`-Platzhalter binden einen Text nicht an das Haushaltsjahr.** `istJahrneutral` (`app/src/lib/texte.ts:62-64`) ignoriert sie, denn sie hängen am Haushaltsjahr und nicht am gewählten Jahr. Nur Platzhalter mit Beträgen binden einen Text weiterhin. Ohne diese Regel würden `ueberschuss_ruecklage` (nur 2024 sichtbar) und `ueberschuss_pb_*` nach der Umstellung verschwinden. Ein vitest-Fall sichert das ab.
- **D-05:** Auch die `Titel:`-Zeilen in `erklaerungen.md` und `glossar.md` laufen durch `pruefe_text`, bisher waren es nur die Absätze. Heute enthält kein Titel eine Zahl, es ist also eine reine Absicherung.

### Lesehilfe und Minderaufwand (TXT-01, TXT-02, 05/IN-06, 05/IN-07)
- **D-06:** `lesehilfeSatz` (`app/src/lib/geldfluss.ts:655-685`) sagt „Erträge und Aufwendungen gleichen sich in diesem Jahr genau aus.“ nur noch, wenn es weder Defizit noch Überschuss noch Minderaufwand gibt. Kommt das Ergebnis erst durch den globalen Minderaufwand auf genau 0, lautet der Satz sinngemäß: „Die Aufwendungen sind höher als die Erträge. Erst der globale Minderaufwand von rund {Betrag} gleicht beide Seiten aus.“ Der Betrag kommt aus den Daten. vitest deckt beide Grenzfälle mit konstruierten Daten ab, denn mit den echten Daten tritt keiner davon ein.
- **D-07:** Der statische Text `geldfluss_lesehilfe` („Beide Seiten sind gleich groß.“) bleibt unverändert. Die Sankey-Seiten weichen wegen Druckrundungen um 1 bis 2 € voneinander ab (2024: 2 €, 2028: 1 €). Das liegt innerhalb der Toleranz, und der dynamische Satz sagt ohnehin „rund“. `texte.json` ändert sich dadurch nicht. Der Planer kann optional einen erklärenden Satz in `befunde.md` ergänzen.
- **D-08:** Ein positiver Minderaufwand (Z. 27 > 0) ist ein Datenfehler und wird einheitlich behandelt. `/geldfluss` (heute schon `geldfluss.ts:260-262`) und `/ausgaben` (`minderaufwandHinweis`, `app/src/lib/aufwandsarten.ts:173`) werfen dann beide mit einer klaren Meldung. Bei 0 erscheint kein Hinweis, das ist legitim (2024). TXT-02 („nie negativ angezeigt“) ist in Commit 53b96ac schon erfüllt. 05/IN-07 wird mit diesem Commit auf fixed gesetzt, der Vereinheitlichungs-Commit kommt als Beleg dazu.

### Fehlende und abgeleitete Werte (TXT-05, TXT-06, 05/IN-08, 06/IN-07)
- **D-09:** **Eine fehlende oder ungültige Einwohnerzahl bricht laut ab.** Es gibt eine gemeinsame Hilfsfunktion `einwohnerZahl()`, die mit klarer Meldung wirft (Muster „… fehlt in haushalt.json“). Sie ersetzt die beiden privaten Duplikate in `lib/kennzahlen.ts:60-66` und `lib/produkt.ts:157-163` und wird auch von `EbenenTabelle` genutzt (heute `EbenenTabelle.vue:29,58`: Spalte bleibt, jede Zelle zeigt „–“). Damit ist auch das Einwohner-Duplikat aus 06/IN-03 erledigt. Ein sichtbarer Hinweis auf der Seite ist ausdrücklich nicht gewünscht.
- **D-10:** **Alle Summen der Stellenplan-Kacheln tragen das Etikett „berechnet“**, nicht nur die Differenzen. Grund: Es gibt keine gedruckte Gesamtzahl, die Werte sind Zeilensummen (`StellenplanPage.vue:66-69`). Heute setzt Kachel 2 `berechnet: false`. Die Quellenleiste nennt, woraus summiert wurde (P7 D-03).
- **D-11:** **Die Quellzeile einer Kachel nennt nur die PDF-Seiten der Zeilen, aus denen ihr Wert stammt**, und nur für Jahre, die einen Wert haben. Beispiel: Vorjahr und besetzt stehen auf S. 284–286, das Haushaltsjahr auf S. 284–289. Dazu liefert `stellenSummen()` (`lib/stellen.ts:122-133`) die Seiten je Kachel getrennt statt als Vereinigung. Das gilt auch für `nachwuchs()` (`lib/stellen.ts:187-200`) und `nachwuchsSatz`. Die `seitenBeleg`-Schlüssel bleiben gleich, damit `quellen.json` sich nicht ändert.
- **D-12:** **„Zusammen rd. …“ in `ZuschussListe.vue:84` trägt „berechnet“ nur, wenn die Summe tatsächlich berechnet wurde.** `zusammen()` (`lib/zuschuesse.ts:138-144`) liefert dazu `{ wert, berechnet }`. Eine gedruckte Summe bleibt ohne Etikett. Die Gruppe `transfer` hat nie eine gedruckte Summe und ist daher immer berechnet. Danach wird geprüft, ob weitere abgeleitete Summen auf Kontextseiten ohne Etikett sind.

### Hygiene und Triage (TRI-01 bis TRI-04)
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

### Barrierefreiheit (A11Y-01 bis A11Y-03, 05/WR-02, 01/IN-05, 05/IN-05) — Voreinstellung, vom Nutzer übernommen
- **D-19:** **`beschriftung` wird bei `DatenTabelle` Pflicht** (`string`, nicht optional). Alle 29 Aufrufe übergeben sie schon. `components/__tests__/zustaende.test.ts` wird angepasst. Ein scrollbarer Rahmen (`tabindex` bei Überlauf) hat damit immer `role="region"` und einen Namen.
- **D-20:** **Jede Tabelle hat genau einen Namen.** Die Caption bekommt eine `id`, und der Region-Rahmen verweist per `aria-labelledby` darauf, statt eines zweiten `aria-label`. Der Text existiert also nur einmal. Ob ein Screenreader die Region und die Caption trotzdem nacheinander ansagt, prüft der Planer bzw. die Recherche. Falls ja, ist die Alternative erlaubt, in der nur eine der beiden Beschriftungen den Namen trägt. Belege: vitest, der axe-Smoke-Test und ein Playwright-Test bei 360 px.
- **D-21:** **Das mobile Menü schließt sich bei jedem Klick auf einen Link im Drawer** (`@click` an den `RouterLink`s, `App.vue:172,177`), auch beim Link der aktuellen Seite. Der Watcher auf die Route bleibt. Beim Klick auf die aktuelle Seite springt der Fokus nicht zum Menüknopf zurück, analog zu `schliesstDurchSeitenwechsel`. Ein Playwright-Test im Projekt `mobil` (360 px) belegt das. Die vorhandenen Drawer-Tests liegen in `e2e/interaktion.spec.ts:175,276` und `e2e/mobil.spec.ts:194`.

### „rd.“-Regel (TXT-04, 05/WR-01)
- **D-22:** Die Regel „rd.“ plus Betrag mit geschütztem Leerzeichen ist an genau einer Stelle umgesetzt. `RD_PRAEFIX` und `betragMitHinweis` ziehen aus `lib/geldfluss.ts` in `charts/format.ts` um. Damit ist auch die Kopplung `EuroBetrag` → `geldfluss` aus 06/IN-04 aufgelöst. Templates nutzen `EuroBetrag`, `.ts`-Code nutzt `betragMitHinweis` bzw. eine Kurzvariante für `euroKurz`. Zu entfernen sind alle Altkopien. Das sind die fünf aus dem Review (`SteuerZeitreihe.vue:147`, `lib/drilldown.ts:201,360`, `lib/zeitreihen.ts:246`, `AufwandTreemap.vue:53`, `EbenenTabelle.vue:79`) und die weiteren Fundstellen (`PostenZeitreihe.vue:153`, `AusgabenPage.vue:347`, `EinnahmenPage.vue:336,409`, `ZuschussListe.vue:65,84,89`, `NichtBeeinflussbarBlock.vue:52`, `KreisumlageCallout.vue:70`). Die Tests werden angepasst (`quelltext.test.ts:151`, `zeitreihen.test.ts:232`, `drilldown.test.ts:337`), und ein Wächter-Test verhindert neue Kopien. Der veraltete Doc-Kommentar in `EuroBetrag.vue:5-8` wird korrigiert.

### Claude's Discretion
- Die genauen Namen der neuen `jahr.`-Schlüssel (relativ und fest), und ob feste Jahre als Schlüssel in `jahrgaenge/2026.toml` oder direkt in `texte.py` aufgelöst werden. Jahrgangsregel: Werte, die vom Jahrgang abhängen, gehören in die TOML.
- Der genaue Wortlaut des Minderaufwand-Satzes im Rahmen von D-06 (Du-Anrede, „rund“ mit `RD`-Regel).
- Ob eine Kurzvariante (z. B. `kurzMitHinweis`) für `euroKurz` entsteht oder `RD_PRAEFIX` direkt genutzt wird.
- Ob 06/IN-02 durch Entfernen oder Umstellen gelöst wird.
- Wie die Pläne zugeschnitten und in Wellen geordnet werden, innerhalb der Roadmap-Reihenfolge Texte → A11Y/Hygiene → Ledger.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Meilenstein und Anforderungen
- `.planning/ROADMAP.md` § Phase 8 — Ziel, Erfolgskriterien 1–5, Querschnittsbedingung
- `.planning/REQUIREMENTS.md` — TXT-01…06, A11Y-01…03, TRI-01…04
- `.planning/PROJECT.md` — Constraints, Key Decisions (u. a. Zeile 138 zu 06/WR-01)

### Befund-Ledger und Reviews
- `.planning/milestones/v1.0-phases/01-setup/01-REVIEW-DISPOSITION.md` und `01-REVIEW.md` — 5 offene Befunde
- `.planning/milestones/v1.0-phases/05-leitfragen-seiten/05-REVIEW-DISPOSITION.md` und `05-REVIEW.md` — 13 offene Befunde. Den Text zu IN-05…IN-11 enthält das aktuelle 05-REVIEW.md nicht mehr, er steht in der Git-Historie dieser Datei.
- `.planning/milestones/v1.0-phases/06-kontext-seiten/06-REVIEW-DISPOSITION.md`, `06-REVIEW.md` und `06-UAT.md` (Test 1, Begründung zu WR-01) — 10 offene Befunde
- `.planning/milestones/v1.0-phases/07-feinschliff-und-ver-ffentlichung/07-REVIEW.md` (IN-02, IN-04) und `07-CONTEXT.md` (D-03 berechnete Werte in der Quellenleiste, D-11…D-14 Smoke-Test, axe, Paketfreigabe, D-17 Token-Hygiene, D-20 Daten bleiben unverändert)

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` — Abschnitt 3 (Minderaufwand, Ergebnisplan), 3.8 (Datenauffälligkeiten), Anhang B (Sollwerte)

### Konventionen
- `.claude/CLAUDE.md` — Konventionen (Jahrgangswerte nur in TOML, Zahlen in Texten nur aus Daten, `beispieldaten`-Flag, Münster-Props, `om-`-Präfix, Farben nur über Tokens)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/src/components/EuroBetrag.vue` (`wert`, `gerundet?`, `berechnet?`) und `BerechnetEtikett` — Ziel der „rd.“-Vereinheitlichung und der „berechnet“-Kennzeichnung
- `app/src/charts/format.ts` — `euro`, `euroKurz`, `anzahlText`. Neuer Ort für `RD_PRAEFIX` und `betragMitHinweis`.
- `lib/ruecklagen.ts:219` `haushaltsjahrIndex()` — Vorlage für einen gemeinsamen Helfer in `lib/jahr.ts`
- `charts/beschriftung.ts:10` `zweizeilig()` — ersetzt `.replace(' ', '\n')` (06/IN-06)
- `echartsTheme.ts`: `NEUTRAL_DUNKEL_FARBE`, `NEUTRAL_MITTEL_FARBE`, `token()` — Vorlage für eine Surface-Konstante (06/IN-01)
- Playwright: `app/playwright.config.ts` mit den Projekten `ci` (1280×800), `mobil` (360×640) und `texte`. Der axe-Smoke-Test liegt in `app/e2e/smoke.spec.ts` und prüft jede Route einmal geschlossen und einmal mit offenen `wa-details`. Dazu kommen `scripts/e2e-wie-ci.sh` und `scripts/lighthouse-a11y.sh`.

### Established Patterns
- Datenfehler werfen laut (`throw new Error('… fehlt in haushalt.json')`), stilles Weglassen gibt es nicht. D-08 und D-09 folgen dem.
- Texte: `daten/manuell/texte/{erklaerungen,glossar}.md` → `pruefe_text` (`pipeline/ostbevern/texte.py:189-232`) → `app/src/data/texte.json`. Platzhalter-Syntax `{{schluessel|kuerzel}}`, Kürzel in `FORMATKUERZEL`. `jahr.`-Schlüssel stehen in `texte.py:422-425`.
- vitest läuft mit `environment: 'node'` und SSR-`renderToString`, eine DOM-Umgebung gibt es nicht. Verhalten im Browser wird per Playwright geprüft.
- Ledger-Format: Frontmatter-Liste plus Tabelle. `deferred` und die Begründung in der Source-Spalte werden von Hand gesetzt.

### Integration Points
- `app/src/lib/texte.ts:62-80` `istJahrneutral` / `textFuerJahr` — Anpassung nach D-04
- `app/src/App.vue:39,66-74,152-177` — Drawer-Zustand, Route-Watcher und Links (D-21)
- `app/src/components/DatenTabelle.vue:10,44,124,148-169` — Props, Slot, Watcher, Region und Caption (D-16, D-19, D-20)
- `app/src/pages/StellenplanPage.vue:58-124` und `lib/stellen.ts:122-200` — Kacheln, Quellseiten, Nachwuchs (D-10, D-11)
- CI: `.github/workflows/ci.yml` (Reproduzierbarkeits-Diff ab :46, e2e bei :115)

### Datenstand (zur Einordnung der Grenzfälle, GESAMT aus `app/src/data/haushalt.json`)
| Jahr | Ergebnis vor MA | Minderaufwand | nach MA | Knoten |
|---|---|---|---|---|
| 2024 | +191.990 | 0 | +191.990 | Überschuss |
| 2025 | −1.896.120 | −564.600 | −1.331.520 | Defizit + MA |
| 2026 | −2.953.506 | −600.000 | −2.353.506 | Defizit + MA |
| 2027 | −2.262.528 | −620.000 | −1.642.528 | Defizit + MA |
| 2028 | −2.418.827 | −660.000 | −1.758.827 | Defizit + MA |
| 2029 | −4.217.700 | −660.000 | −3.557.700 | Defizit + MA |

Kein Jahr trifft den Grenzfall von TXT-01. Die Tests brauchen konstruierte Daten.

</code_context>

<specifics>
## Specific Ideas

- Bewusste Diffs, die erwartet und im Commit begründet werden: `app/src/data/texte.json` (D-03, Jahres-Platzhalter) und die Löschung von `app/src/data/beispieldaten.json` (D-15). Jeder andere Diff in `daten/` oder `app/src/data/` ist ein Befund für den Nutzer (P7 D-20).
- Fix-Commits nennen die Befund-ID mit Phasenpräfix (z. B. `05/IN-06`), damit die Ledger-Pflege am Phasenende sie zitieren kann.

</specifics>

<deferred>
## Deferred Ideas

None — die Diskussion blieb im Phasenumfang. Neue Pakete wurden bewusst abgelehnt (DOM-Testumgebung, D-14).

</deferred>

---

*Phase: 08-fixes-und-triage*
*Context gathered: 2026-10-07*
