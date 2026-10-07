---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 03
subsystem: quellenbelege
tags: [pdfplumber, pypdfium2, pillow, webp, redaction, polars, vitest, ci]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: "07-01: Schritt 08 (quellen.py, belegbilder.py, 08_quellenbelege.py), Schluesselgrammatik in lib/quelle.ts, findeBeleg, QuelleKnopf"
  - phase: 04-manuelle-daten-und-app-daten
    provides: "App-JSONs, manuelle Vorberichts-CSVs, meta.json, verbindlichkeiten.csv"
provides:
  - "app/src/data/quellen.json mit 2496 Belegen aller Arten (ep, fp, vb, meta, gz, pr, inv, ve, sd, sp, seite) auf 231 Seiten"
  - "231 WebP-Belegseiten unter app/public/quellen/ (18 MB), Produktinformationen-Seiten mit geschwaerzten Personenfeldern"
  - "daten/pruefberichte/quellenbelege.md: 33 Belege ohne Markierung mit Grund, Datenschutz-Pruefliste, Liste der geschwaerzten Seiten"
  - "produkte.personenfeld_rechtecke (nur Geometrie), belegbilder.rendere_seiten(ohne_personenfelder), [layout.quellenbelege]"
  - "Schritt 08 in alle.py und im CI-Reproduzierbarkeitstest; Vertragstest quelle-abdeckung.test.ts"
affects: [07-06, 07-07, 07-08, 07-10, 07-11, 07-12]

actuals:
  tokens: 161000
  tasks: 3
  commits: 7

tech-stack:
  added: []
  patterns:
    - "Jede Suche prueft Beschriftung (oder Zeilennummer/Konto) plus Betrag des Haushaltsjahrs; ohne genau einen Treffer bbox null mit Grund (D-03)"
    - "Teilplan-Belege suchen nur im Teilergebnisplan-Abschnitt der Seite (lies_abschnitte), nie im Teilfinanzplan"
    - "Schwaerzung wird als Geometrie (Rechtecke) berechnet, nie als Text; Seitenbilder der Personenfelder entstehen nur mit Rechtecken oder ausdruecklicher Freigabe als Fortsetzungsseite"
    - "Ein Beleg-Rechteck, das eine Schwaerzung beruehrt, wird verworfen (ueberlappt_schwaerzung)"

key-files:
  created:
    - pipeline/tests/test_belegbilder.py
    - app/src/lib/__tests__/quelle-abdeckung.test.ts
    - daten/pruefberichte/quellenbelege.md
    - app/public/quellen/ (229 neue Seitenbilder s008 bis s311)
  modified:
    - pipeline/ostbevern/quellen.py
    - pipeline/ostbevern/produkte.py
    - pipeline/ostbevern/belegbilder.py
    - pipeline/ostbevern/konfiguration.py
    - pipeline/ostbevern/schema.py
    - pipeline/jahrgaenge/2026.toml
    - pipeline/08_quellenbelege.py
    - pipeline/alle.py
    - pipeline/tests/test_quellen.py
    - pipeline/tests/test_produkte.py
    - pipeline/tests/test_konfiguration.py
    - pipeline/tests/test_alle.py
    - app/src/data/quellen.json
    - .github/workflows/ci.yml

key-decisions:
  - "ep-Belege nur fuer Zeilen, die die App als Datensatz kennt (haushalt.ergebnisplan[code].zeilen); die fuenf nachrichtlichen GEP-Zeilen unter Z. 28 haben keinen ep-Beleg, damit jeder Schluessel auf einen Datensatz zeigt (Vertragstest)"
  - "Beschriftungsvergleich: Gleichheit, Praefix oder Suffix der normalisierten Beschriftung ab vier Zeichen, fuehrende Gliederungsnummer wird ignoriert; so trifft der Umbruch 'fuer Investitionen' der Verbindlichkeiten-Tabelle, nicht aber die Zeile '2.5.1 von Banken' mit denselben Betraegen"
  - "Promille und Hektar werden auch in der gedruckten Form Prozent (36,3) bzw. Quadratkilometer (89,6) gesucht; berechnete MetaWerte und Posten bekommen bbox null mit Grund 'berechnet' statt einer Suche"
  - "Grundzahlen werden mit dem Wert des Haushaltsjahrs gesucht, ohne Haushaltsjahrwert mit dem des letzten Jahrs (die Ist-Tabellen enden 2025)"
  - "Fortsetzungsseiten der Produktinformationen (zweite Seite von 010901) zeigen kein Personenfeld: rendere_seiten bekommt sie ueber ohne_personenfelder; personenfeld_rechtecke erzwingt, dass die erste Seite jedes Produkts beide Personenfelder traegt"
  - "Die schwarze Flaeche reicht 2 px ueber das gemeldete Rechteck hinaus, damit die verlustbehaftete WebP-Kompression keine hellen Pixel in das Rechteck traegt (Pixeltest gruen)"
  - "Eine leere Liste in der Jahrgangsdatei ist erlaubt (schwaerzen_nach = []), ein leerer Eintrag nicht"

patterns-established:
  - "Konsumenten (07-06 bis 07-08) bauen Schluessel nur ueber belegSchluessel; jeder Datensatz mit Seitenfeld hat einen Schluessel, den Vertragstest und Konsumenten teilen"
  - "ep-Schluessel gibt es nur fuer gedruckte Zeilen: eine leere Tabellenzelle (Zeile nicht gedruckt) hat keinen Beleg, QuelleKnopf rendert dort nichts"

requirements-completed: [DATA-04]

coverage:
  - id: D1
    description: "Belege fuer Plaene aller Knoten (1508 ep, 41 fp), Vorbericht (145 vb), Meta (19), Schuldenstand (3), Massnahmen (137), VE (6) und Stellenplan (123) mit Beschriftungs-/Betragsprobe, Rechteck sonst null mit Grund"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_quellen.py (Proben je Belegart gegen das echte PDF, test_jede_gedruckte_ergebnisplanzeile_hat_einen_beleg, test_belege_decken_alle_datensaetze_der_aufgabe, Duplikat-bbox-Test)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Produkt-, Grundzahl- und Seitenbelege (63 pr, 220 gz, 231 seite) fuer die Vereinigung aller Seitenfelder der fuenf App-JSONs, jede Seite als WebP"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_quellen.py#test_seitenbelege_decken_die_vereinigung_aller_seitenfelder"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_belegbilder.py#test_eingecheckte_bilder_existieren_mit_erwarteten_massen"
        status: pass
    human_judgment: false
  - id: D3
    description: "Personenfelder der 64 Produktinformationen-Seiten sind in den eingecheckten Bildern geschwaerzt (Geometrie- und Pixeltest), kein Personenname in quellen.json oder Bericht"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_belegbilder.py#test_jedes_namenswort_liegt_in_einem_schwaerzungsrechteck"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_belegbilder.py#test_in_jedem_eingecheckten_schwaerzungsrechteck_sind_die_pixel_schwarz"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_quellen.py#test_keine_personennamen_in_quellen_json_und_bericht"
        status: pass
    human_judgment: false
  - id: D4
    description: "Datenschutz-Pruefliste: Seiten mit Namens- oder Kontakthinweis ausserhalb der Personenfelder (u. a. Haushaltssatzung S. 9) sind gelistet, aber nicht geschwaerzt"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_quellen.py#test_bericht_nennt_pruefliste_und_geschwaerzte_seiten"
        status: pass
    human_judgment: true
    rationale: "Ob Unterschriftsnamen oder Kontaktzeilen auf diesen Seiten veroeffentlicht oder geschwaerzt werden, ist eine Entscheidung der Nutzerin am Checkpoint 07-10"
  - id: D5
    description: "Schritt 08 laeuft in alle.py nach Schritt 07, Fehler enden mit exit 1, der CI-Reproduzierbarkeitstest prueft app/public/quellen; alle.py ist auf dem echten Datenbestand byte-reproduzierbar"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_quellenfehler_beendet_mit_fehler, #test_schritt_08_meldet_belege_und_laeuft_nach_schritt_07"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026, danach git diff --exit-code (daten, app/src/data) und git status (app/public/quellen) leer"
        status: pass
    human_judgment: false
  - id: D6
    description: "Vertragstest zwischen quellen.json und den TS-Schluesselbauern: jeder Datensatz mit Seitenfeld hat einen Beleg, jeder Schluessel zeigt auf einen Datensatz, Bild und Seite stimmen mit der seiten-Karte ueberein"
    requirement: "DATA-04"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelle-abdeckung.test.ts (7 Tests; Mutationsprobe: fehlender Beleg, erfundener Schluessel und falsches Bild lassen drei Tests rot werden)"
        status: pass
    human_judgment: false

duration: 39min
completed: 2026-10-06
status: complete
plan_head_before: 82a22f435c189de004f0db24fe85c06e946d3b5d
plan_head_after: 77573d9cfa8f2be1e9e8b0110ea6f3aae22d44d4
---

# Phase 7 Plan 03: Alle Belegarten, Schwaerzung und Vertragstest Summary

**Schritt 08 belegt jetzt jeden Wert mit Seitenfeld (2496 Belege auf 231 Seiten, nur 33 ohne Zeilenrechteck und mit Grund im Bericht), rendert alle Seiten als WebP mit schwarz gedeckten Personenfeldern (Geometrie- und Pixeltest), laeuft in alle.py und im CI-Reproduzierbarkeitstest, und ein vitest-Vertragstest haelt quellen.json und die TS-Schluesselbauer deckungsgleich.**

## Performance

- **Duration:** 39 min
- **Started:** 2026-10-06T11:57:00Z (geschaetzt)
- **Completed:** 2026-10-06T12:36:00Z
- **Tasks:** 3 (alle TDD mit RED- und GREEN-Commit)
- **Files modified:** 16 Quelldateien plus 229 neue WebP-Seiten

## Accomplishments

- **Belege je Art** (Haushaltsjahr 2026): ep 1508 (0 ohne Markierung), fp 41 (0), vb 145 (20), meta 19 (4), gz 220 (4), pr 63 (0), inv 137 (0), ve 6 (0), sd 3 (1), sp 123 (4), seite 231. Insgesamt 2496 Belege, 33 ohne Zeilenrechteck. Der Anteil ohne Markierung liegt bei 1,3 Prozent; die Gruende stehen in `daten/pruefberichte/quellenbelege.md` (`betrag_fehlt` 14 mal, `nicht_gefunden` 14, `berechnet` 3, `mehrdeutig` 2 ueber alle Belegarten hinweg).
- **Treffsicherheit** per Overlay auf den gerenderten Seiten geprueft (Maßnahme mit VE-Zeile samt Kassenwirksamkeit, Verbindlichkeiten-Tabelle mit umgebrochenem Namen, Stellenuebersicht mit umbrochenen Produktbereichs-Zeilen): die Rechtecke sitzen auf den richtigen Zeilen.
- **Datenschutz:** `personenfeld_rechtecke` liefert 64 Seiten mit Rechtecken (nur Zahlen). Alle Namenswoerter aus `lies_personennamen` liegen in Rechtecken, in jedem eingecheckten Rechteck ist das Maximum der Farbkanaele hoechstens 40, und kein Name steht in quellen.json oder im Bericht. Die Seite S. 72 wurde mit dem Auge geprueft (Verantwortliche/r und Sachbearbeiter/innen schwarz, der Rest lesbar).
- **Ausfuehrung:** Schritt 08 braucht etwa 20 bis 30 Sekunden; ein zweiter Lauf rendert 0 Bilder und aendert keine Datei. Die komplette `alle.py` ist auf dem echten Bestand reproduzierbar (diff leer, keine ungetrackte Datei unter `daten`, `app/src/data`, `app/public/quellen`).
- **Vertragstest:** `quelle-abdeckung.test.ts` schlaegt bei einer Luecke fehl und nennt die fehlenden Schluessel (E1).

## Task Commits

1. **Task 1: Belege fuer Plaene aller Knoten, Vorbericht, Meta, Schuldenstand, Massnahmen, VE, Stellenplan** - RED `3cf1578` (test), GREEN `82713f0` (feat)
2. **Task 2: Schwaerzung, Produkt-/Grundzahl-/Seitenbelege, alle Belegseiten** - RED `393280d` (test), GREEN `6fddfc1` (feat)
3. **Task 3: Schritt 08 in alle.py und CI, Vertragstest** - RED `43b48a3` (test), GREEN `897f10d` (feat), danach `77573d9` (refactor: Seitenbelege stehen nicht in `ohne_bbox`)

**Plan metadata:** folgt als docs-Commit (SUMMARY.md)

## TDD Gate Compliance

Fuer alle drei Aufgaben gibt es einen `test(07-03)`-Commit vor dem `feat(07-03)`-Commit.

- **RED Aufgabe 1** (`3cf1578`): 19 neue Tests rot, u. a. `test_schluesselgrammatik_alle_arten` (AttributeError: `schluessel_vb` fehlt), `test_alle_belegarten_der_aufgabe_vorhanden` (nur ep und fp vorhanden), die Proben je Belegart (KeyError: Schluessel fehlt in quellen.json), `test_jede_gedruckte_ergebnisplanzeile_hat_einen_beleg`. Semantische Bewertung: jeder Test lief und scheiterte an der noch nicht gebauten Funktion bzw. am noch fehlenden Beleg, nicht an Syntax, Import oder Fixture; die 26 bestehenden Tests blieben gruen.
- **RED Aufgabe 2** (`393280d`): 18 Tests rot (`personenfeld_rechtecke` als Geruest ohne Rechtecke, `ohne_personenfelder` unbekannt, keine `seite:`-/`pr:`-/`gz:`-Belege, kein `[layout.quellenbelege]`). Semantische Bewertung wie oben; `test_kein_beleg_rechteck_ueberlappt_eine_schwaerzung` und der Namenstest laufen im RED vakuum gruen und sind als Schutz nach dem GREEN gemeint.
- **RED Aufgabe 3** (`43b48a3`): vier alle.py-Tests rot (Reihenfolge endet nicht mit 08, `QuellenFehler` und `BelegbildFehler` fuehren nicht zu exit 1). Der vitest-Vertragstest war schon gruen, weil die Daten aus Aufgabe 1 und 2 existieren: er sichert kuenftige Luecken. Belegt wurde seine Wirksamkeit durch eine Mutationsprobe (Beleg geloescht, Schluessel erfunden, Bild vertauscht: drei Tests rot, danach wiederhergestellt) und durch den Test, der einen erfundenen Schluessel ablehnen muss.
- `gsd_run check tdd-red-evidence` wurde nicht ausgefuehrt: `workflow.tdd_mode` ist aus, und der pytest-Bericht ist kein vom Klassifizierer unterstuetztes Format.
- **REFACTOR:** `77573d9` (kleine Bereinigung, Tests weiter gruen).

## Files Created/Modified

Siehe Frontmatter `key-files`. Kern: `pipeline/ostbevern/quellen.py` (alle Suchen, Bericht, `erzeuge_quellen`), `pipeline/ostbevern/produkte.py` (`personenfeld_rechtecke`), `pipeline/ostbevern/belegbilder.py` (Schwaerzung zeichnen, Freigabe fuer Fortsetzungsseiten), `app/src/lib/__tests__/quelle-abdeckung.test.ts` (Vertrag).

## Decisions Made

Siehe `key-decisions`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Jahrgangsdatei lehnte eine leere Liste ab**
- **Found during:** Task 2 (`schwaerzen_nach = []`)
- **Issue:** Der Layout-Validator in `konfiguration.py` verlangte nicht-leere Listen; der geplante Eintrag haette die Konfiguration unlesbar gemacht.
- **Fix:** Eine leere Liste ist erlaubt, ein leerer oder nicht-String-Eintrag bleibt verboten; Tests in `test_konfiguration.py`.
- **Files modified:** pipeline/ostbevern/konfiguration.py (nicht in der Dateiliste des Plans), pipeline/tests/test_konfiguration.py
- **Committed in:** 6fddfc1

**2. [Rule 1 - Bug] ep-Belege fuer Zeilen ohne Datensatz in der App**
- **Found during:** Task 1 (Vertrag: jeder Schluessel zeigt auf einen Datensatz)
- **Issue:** Die 07-01-Fassung belegte alle 33 GESAMT-Zeilen der Ergebnisplan-CSV, darunter die fuenf nachrichtlichen GEP-Zeilen, die `haushalt.ergebnisplan.GESAMT.zeilen` nicht kennt; der Vertragstest haette sie als Schluessel ohne Datensatz gemeldet.
- **Fix:** ep nur fuer Zeilen mit App-Datensatz (28 statt 33 fuer GESAMT); der 07-01-Test `test_jede_gesamtzeile_hat_einen_beleg` vergleicht jetzt gegen diese Menge.
- **Files modified:** pipeline/ostbevern/quellen.py, pipeline/tests/test_quellen.py
- **Committed in:** 82713f0

**3. [Rule 2 - Datenschutz] Freigabe fuer Fortsetzungsseiten der Produktinformationen**
- **Found during:** Task 2 (Produkt 010901 hat zwei Produktinformationen-Seiten, nur die erste zeigt Personenfelder)
- **Issue:** Die geplante Wache (jede Produktinformationen-Seite braucht Rechtecke) haette S. 99 blockiert und damit `seite:99` und das Bild verhindert.
- **Fix:** `rendere_seiten(..., ohne_personenfelder=...)` gibt solche Seiten ausdruecklich frei; eine leere Rechteckliste fuer eine Produktinformationen-Seite loest weiter `BelegbildFehler` aus. Abgesichert wird die Freigabe dadurch, dass `personenfeld_rechtecke` mit `ProdukteFehler` abbricht, wenn die erste Seite eines Produkts nicht beide Personenfelder traegt.
- **Files modified:** pipeline/ostbevern/belegbilder.py, pipeline/ostbevern/produkte.py, pipeline/ostbevern/quellen.py, Tests
- **Committed in:** 6fddfc1

**4. [Rule 2 - Datenschutz] Schwaerzung 2 px ueber das gemeldete Rechteck hinaus**
- **Found during:** Task 2 (Pixeltest)
- **Issue:** Bei verlustbehafteter WebP-Kompression koennen Randpixel eines schwarzen Rechtecks heller werden.
- **Fix:** `SCHWAERZUNG_UEBERSTAND_PX = 2`; das gemeldete Rechteck liegt vollstaendig im Schwarz.
- **Files modified:** pipeline/ostbevern/belegbilder.py
- **Committed in:** 6fddfc1

**5. [Rule 2 - Missing Critical] `ProdukteFehler` endet mit exit 1**
- **Found during:** Task 3
- **Issue:** `erzeuge_quellen` ruft `personenfeld_rechtecke` auf, das `ProdukteFehler` ausloest; die Fehlerliste des Plans kennt ihn nicht, es gaebe einen Stacktrace statt `Fehler:` und exit 1.
- **Fix:** `ProdukteFehler` in alle.py und 08_quellenbelege.py abgefangen; Test `test_quellenfehler_beendet_mit_fehler[produktefehler]`.
- **Committed in:** 897f10d

### Kleine Abweichungen und Ergaenzungen

- **Meta-Suche:** Promille und Hektar werden zusaetzlich in der gedruckten Form (Prozent mit Komma, Quadratkilometer) gesucht, sonst waeren Hebesatz der Kreisumlage und Gemeindeflaeche ohne Markierung geblieben.
- **Vergleich in Tabellen:** zusaetzlich zur Plan-Regel entscheidet die vollstaendige Wertfolge (alle gedruckten Jahre in Reihenfolge) bei mehreren Treffern; Beschriftungsvergleich auch ueber Praefix und Suffix (Umbruch).
- **Gemeinsame Zeile:** Zwei Schluessel teilen sich ein Rechteck nur, wenn sie dieselbe gedruckte Zeile belegen; der Duplikat-Test kennt drei solche Faelle: Teilergebnisplan-Zeile von Produkt und synthetischer Produktgruppe, `inv` und `ve` einer Kontozeile, Zellen einer Stellenuebersicht-Zeile, ausserdem `meta:kreisumlage.netto` und `vb:transferaufwendungen:kreisumlage` (S. 46).
- **Tests:** die fuenf Bild-Tests aus `test_quellen.py` liegen jetzt in `test_belegbilder.py`; die Fixture `tmp_ergebnis` baut die App-JSONs per `erzeuge_app_daten` in einem tmp-Verzeichnis und schreibt den Bericht in eine Kopie von `daten/`.
- **App-Pruefungen** liefen direkt im Worktree (nach `npm ci`, ohne `--dry-run`) statt in einer Scratch-Kopie: type-check, lint, format:check, die volle vitest-Suite (1630 Tests) und `build-only` sind gruen.

---

**Total deviations:** 5 auto-fixed (1 Bug, 3 Rule 2, 1 Rule 3) plus kleine Ergaenzungen.
**Impact on plan:** Keine Aenderung an Schluesselgrammatik, Dateiformat oder Schnittstellen von 07-01; die Abweichungen sichern Datenschutz und Vertragstest ab.

## Issues Encountered

- **Bundle-Groesse:** `quellen.json` hat 454 KB (die gemeinsame JSON-Ausgabe schreibt jede Zahl einer bbox in eine eigene Zeile), das JS-Bundle waechst von etwa 1,75 MB auf 2,03 MB (gzip 485 KB). Die Planschaetzung von 100 bis 200 KB war zu niedrig. Spaeter laesst sich der Beleg-Index aufteilen (RESEARCH Pitfall 4); hier nicht Teil des Plans.
- **Bildmenge:** 231 Seiten mit 18 MB statt der in D-01 genannten 188 Seiten (Vereinigung aller Seitenfelder plus Teilplan-Seiten der ep-Belege), wie in den Flagged assumptions angekuendigt.
- **Quellen-Pruefliste, Entscheidung offen (T-07-09):** S. 9 (Haushaltssatzung) druckt die Namen der Unterzeichnenden (Kaemmerin, Buergermeister); das Etikett steht dort aber unter der Namenszeile, das Hilfsmittel `schwaerzen_nach` schwaerzt nur die Zeile direkt nach einem Etikett und passt deshalb nicht ohne Erweiterung. Weitere Seiten mit Stichwort und ohne Schwaerzung: 17, 18, 32, 48, 75, 95 (Telefon) u. a.; die vollstaendige Liste steht im Bericht. Die Bilder sind lokal eingecheckt, es gibt kein Remote bis 07-12; die Entscheidung faellt am Checkpoint 07-10.
- **Nicht markierte Werte (siehe Bericht):** Tabellen mit umgebrochenen Beschriftungen ueber und unter der Wertzeile (z. B. Zuschuss an das Kinder- und Jugendwerk), Zuschuesse fuer laufende Zwecke S. 47 (Werte stehen im Fliesstext), Verbindlichkeiten aus Krediten zur Liquiditaetssicherung (verdoppelte Buchstaben in der Textebene des PDF), vier Stellenplanzeilen der Tarifgruppen (Wert und Beschriftung in verschiedenen Zeilenhoehen) sowie vier Grundzahlen mit mehrzeiligem Namen. Sie bekommen die Seite ohne Markierung mit dem Hinweis aus 07-01.

## User Setup Required

None - keine externen Dienste noetig.

## Known Stubs

None. `bbox: null` ist ein modellierter Zustand (D-03) und im Bericht jeweils begruendet.

## Threat Flags

None - die neue Flaeche (committete Seitenbilder, Bericht) liegt in der Bedrohungsliste des Plans (T-07-08 bis T-07-12); T-07-09 bleibt als Entscheidung am Checkpoint 07-10 offen (siehe Issues Encountered).

## Next Phase Readiness

- Konsumenten 07-06 bis 07-08 koennen jeden Datensatz mit Seitenfeld ueber `belegSchluessel` + `QuelleKnopf` belegen; es gibt fuer jeden Schluessel einen Eintrag, bei fehlendem Rechteck zeigt die Leiste den Hinweis.
- Ein `ep`-Beleg existiert nur fuer gedruckte Zeilen; leere Tabellenzellen (Zeile nicht gedruckt, EXTR-04) haben keinen Beleg und damit keinen Knopf.
- 07-10 entscheidet ueber die Datenschutz-Pruefliste (insbesondere S. 9) und ob `schwaerzen_nach` oder eine andere Vorgabe gebraucht wird; 07-11 und 07-12 koennen den Bild- und Bundle-Umfang bewerten.

## Self-Check: PASSED

- Dateien vorhanden: quellen.py, belegbilder.py, produkte.py, 2026.toml, 08_quellenbelege.py, alle.py, alle Testdateien, quellen.json, quellenbelege.md, quelle-abdeckung.test.ts, ci.yml; 231 WebP-Seiten.
- Commits vorhanden: 3cf1578, 82713f0, 393280d, 6fddfc1, 43b48a3, 897f10d, 77573d9 (alle im Zweig).
- Akzeptanzkriterien aller drei Aufgaben geprueft (erfuellt); Gesamtsuite 631 pytest, ruff check und format, 1630 vitest, type-check, lint, format:check und alle.py-Reproduzierbarkeit gruen.

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
