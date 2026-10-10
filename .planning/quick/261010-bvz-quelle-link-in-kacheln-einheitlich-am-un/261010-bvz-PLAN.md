---
phase: quick-261010-bvz
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app/src/components/KennzahlKachel.vue
  - app/e2e/kacheln.spec.ts
autonomous: true
requirements:
  - QUICK-261010-bvz

estimate:
  tokens: 60000
  raw_tokens: 60000
  tasks: 2
  confidence: low

must_haves:
  truths:
    - "Auf jeder Kachelroute (start, investitionen, rat-entscheidet, stellenplan) und bei jeder Breite des Sweeps (360 bis 1440 px) endet der Quelle-Knopf (Icon file-lines + „Quelle“) jeder Kennzahl-Kachel genau am unteren Inhaltsrand der grauen Box, also mit dem Innenabstand --wa-space-m über der Unterkante (Toleranz 0,5 px)."
    - "Alle Kennzahl-Kacheln einer Rasterreihe sind gleich hoch, und ihre Quelle-Knöpfe enden auf derselben Höhe (Toleranz 0,5 px), unabhängig davon, wie viele Zeilen Bezeichnung oder Zeile umbrechen."
    - "Die Zeile „{Wertart} {jahr} · PDF-Seite {n}“ steht weiterhin direkt unter dem Betrag; nur die Quelle-Zeile ist unten fixiert."
    - "Der Mindestabstand zwischen Zeile und Quelle-Knopf bleibt wie bisher (Flex-Gap xs plus xs), die höchste Kachel einer Reihe wird also nicht höher; alle bisherigen Prüfungen in app/e2e/kacheln.spec.ts (kein Überlauf, Betragsgröße l, Knopf mindestens 44 × 44 px, zugänglicher Name) bleiben grün."
    - "type-check, lint, format:check, vitest, build und die Playwright-Suite des Projekts ci sind grün (in einer Scratch-Kopie mit Linux-node_modules)."
  artifacts:
    - path: "app/src/components/KennzahlKachel.vue"
      provides: "Kachel als Flex-Spalte, deren Quelle-Wrapper .om-kennzahl__quelle per margin-top: auto am unteren Rand fixiert ist"
      contains: "margin-top: auto"
    - path: "app/e2e/kacheln.spec.ts"
      provides: "Layoutprüfung Unterkante Quelle-Knopf je Kachel und Gleichlauf je Rasterreihe (Höhe, Knopf-Unterkante)"
      contains: "Quelle-Knopf endet bei"
  key_links:
    - from: "app/src/styles/basis.css (.om-kachelraster, Grid mit align-items stretch)"
      to: "app/src/components/KennzahlKachel.vue (.om-kennzahl height: 100%)"
      via: "gestrecktes li gibt der Kachel die volle Reihenhöhe (gemessen: Kachelhöhe = li-Höhe)"
      pattern: "height: 100%"
    - from: "app/src/components/KennzahlKachel.vue (.om-kennzahl__quelle)"
      to: "Unterkante des Inhaltsbereichs der Kachel"
      via: "margin-top: auto in der Flex-Spalte nimmt den freien Platz auf"
      pattern: "margin-top: auto"
    - from: "app/e2e/kacheln.spec.ts (messeKacheln)"
      to: "alle KACHEL_ROUTEN × BREITEN"
      via: "neue Befunde je Kachel (Unterkante) und je Reihe (Höhe, Knopf-Unterkante)"
      pattern: "Quelle-Knopf endet bei"
---

<objective>
Der Quelle-Link (QuelleKnopf, Variante kachel: Icon file-lines plus Text „Quelle“) in den Kennzahl-Kacheln soll immer mit Innenabstand am unteren Rand der grauen Box liegen, sodass er in einer Reihe nebeneinanderliegender Kacheln nicht mehr je nach Zeilenzahl rauf- oder runterrutscht. Das gilt für alle Verwendungen von `KennzahlKachel` (Startseite, Investitionen, Rat entscheidet über `NichtBeeinflussbarBlock`, Stellenplan), nicht nur für die Startseite.

Befund aus der Planung (Messung im Playwright-Image, Chromium, gebauter Stand mit unverändertem `KennzahlKachel.vue`):
- Die Kacheln einer Reihe sind bereits gleich hoch (Kachelhöhe = Höhe des gestreckten `li`, z. B. /#/ bei 1280 px: alle fünf Kacheln der ersten Reihe 176 px). Die Höhenkette Grid → li → `.om-kennzahl { height: 100% }` funktioniert.
- Der Quelle-Knopf endet aber nicht am Rand: /#/ bei 1280 px liegen die Knöpfe der Kacheln 3 bis 5 um 7 px höher als die der Kacheln 1 und 2; /#/stellenplan bei 1280 px streuen sie um 21 px, /#/investitionen bei 768 px ebenfalls um 21 px.
- Ursache: Die vorhandene Regel `.om-kennzahl__zeile { margin-top: auto }` greift nie. Die Regel `.om-kennzahl p { margin: 0 }` ist spezifischer (mit dem Scoped-Attribut 0,2,1 gegenüber 0,2,0) und setzt den oberen Außenabstand der Zeile auf 0. Der freie Platz der Flex-Spalte landet deshalb unter dem Knopf statt darüber.

Gestaltungsentscheidung (Ermessen des Planers, keine CONTEXT.md vorhanden): Unten fixiert wird nur die Quelle-Zeile (Wrapper `.om-kennzahl__quelle` mit `margin-top: auto`), wie in der Aufgabe vorgeschlagen. Die Zeile „{Wertart} {jahr} · PDF-Seite {n}“ bleibt direkt unter dem Betrag, so wie sie heute tatsächlich gerendert wird; sie gehört inhaltlich zum Betrag. Die wirkungslose Deklaration an `.om-kennzahl__zeile` wird entfernt.

Purpose: Ruhiges, einheitliches Kachelbild auf allen Kachelrouten und bei allen Breiten ab 360 px; der Quelle-Link ist immer an derselben Stelle zu finden.
Output: Geändertes Kachel-CSS, eine erweiterte Layoutprüfung in `app/e2e/kacheln.spec.ts`, die den Fehler rot zeigt und nach dem Fix grün ist.
</objective>

<execution_context>
@.claude/gsd-core/workflows/execute-plan.md
@.claude/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.claude/CLAUDE.md
@app/src/components/KennzahlKachel.vue
@app/src/components/QuelleKnopf.vue
@app/src/styles/basis.css
@app/e2e/kacheln.spec.ts
@scripts/e2e-wie-ci.sh

<interfaces>
Relevante Stellen, damit der Executor nicht suchen muss:

app/src/components/KennzahlKachel.vue (Template): `div.om-kennzahl` enthält in dieser Reihenfolge `p.om-kennzahl__bezeichnung`, `p.om-kennzahl__wert`, `p.om-kennzahl__zeile` und, nur wenn die Prop `quelle` gesetzt ist, `div.om-kennzahl__quelle` mit `QuelleKnopf variante="kachel"`.
app/src/components/KennzahlKachel.vue (Style, scoped): `.om-kennzahl` ist `display: flex; flex-direction: column; gap: var(--wa-space-xs); height: 100%; box-sizing: border-box; background: var(--wa-color-surface-lowered); padding: var(--wa-space-m)`. `.om-kennzahl p { margin: 0 }`. `.om-kennzahl__zeile` enthält die wirkungslose `margin-top: auto`. `.om-kennzahl__quelle { margin-top: var(--wa-space-xs) }`.
app/src/components/QuelleKnopf.vue: `button.om-quelle-knopf` ist `display: inline-flex`, mindestens 44 × 44 px; nur gerendert, wenn der Beleg in `quellen.json` existiert.
app/src/styles/basis.css: `.om-kachelraster` ist ein Grid (auto-fit, minmax mit `--om-kachel-mindestbreite`), Standard-`align-items` (stretch); `.om-kachelraster > li { min-width: 0; margin: 0 }`.

app/e2e/kacheln.spec.ts:
- `messeKacheln(page)` wertet in einem einzigen `page.evaluate` alle sichtbaren `.om-kennzahl` aus. Im Browserkontext stehen die Helfer `zahl`, `sichtbar`, `px`, die Parameter `mindest` und `toleranz` (= `TOLERANZ` 0,5) sowie je Kachel `name`, `rahmen` (getBoundingClientRect der Kachel), `stil` (getComputedStyle der Kachel), `innenLinks`, `innenRechts` zur Verfügung. Befunde werden als Strings in `befunde` gesammelt.
- Abschnitt „(f) Knopf „Quelle““ iteriert über `kachel.querySelectorAll('.om-quelle-knopf')` mit `kasten = knopf.getBoundingClientRect()`.
- Die Liste der Kachel ist `kachel.closest('li')?.parentElement` (wird in (a) schon für die Spurmessung benutzt).
- Der Test „Kacheln und Seitenbreite: {pfad}“ läuft je Route aus `KACHEL_ROUTEN` über alle `BREITEN` (360 bis 1440 px plus Spaltensprünge) und erwartet `befunde` leer.
</interfaces>
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Task 1: Tracer – Layoutprüfung „Quelle-Knopf am unteren Rand, Reihen im Gleichlauf“ rot, dann Kachel-CSS fixieren und grün</name>
  <files>app/e2e/kacheln.spec.ts, app/src/components/KennzahlKachel.vue</files>
  <precondition>Docker ist erreichbar und das Image mcr.microsoft.com/playwright:v1.63.0-noble ist vorhanden oder ladbar; OM_SCRATCH zeigt auf ein Verzeichnis im Session-Scratchpad des Executors (außerhalb des Repos), in dem `npm --prefix "$OM_SCRATCH/repo/app" ci` einmal erfolgreich gelaufen ist.</precondition>
  <behavior>
    - Für jede sichtbare Kennzahl-Kachel und jeden sichtbaren `.om-quelle-knopf` darin gilt: Unterkante des Knopfs = Unterkante des Inhaltsbereichs der Kachel (Kachel-Unterkante minus border-bottom minus padding-bottom), Abweichung höchstens TOLERANZ. Sonst Befund „„{name}“: Quelle-Knopf endet bei {y} px, Inhaltsbereich endet bei {y'} px“.
    - Für jede Rasterreihe (gleiche Liste, li-Oberkanten innerhalb TOLERANZ) mit mindestens zwei Kacheln gilt: Spannweite der Kachelhöhen höchstens TOLERANZ, Spannweite der Knopf-Unterkanten höchstens TOLERANZ. Sonst je ein Befund „Reihe bei {y} px: Kachelhöhen {min} bis {max} px“ bzw. „Reihe bei {y} px: Quelle-Knöpfe enden bei {min} bis {max} px“, ergänzt um die Namen der Kacheln der Reihe.
    - Rot vor dem CSS-Fix: Auf / bei 1280 px und auf /stellenplan bei 1280 px meldet der Test mindestens einen der neuen Befunde (Planungsmessung: 7 px bzw. 21 px Streuung).
    - Grün nach dem CSS-Fix: `e2e/kacheln.spec.ts` meldet auf allen vier Kachelrouten bei allen Breiten keinen Befund, auch nicht in den bisherigen Prüfungen.
  </behavior>
  <action>
Schritt 0, Scratch-Kopie (CLAUDE.md: app/node_modules enthält macOS-Binaries, App-Prüfungen nur in einer Scratch-Kopie). Setze OM_SCRATCH auf ein neues Verzeichnis in deinem Session-Scratchpad. Spiegle das Repo dorthin mit `rsync -a --delete` und den Ausschlüssen `.git`, `node_modules`, `dist`, `test-results`, `playwright-report`, `.venv`, `.planning`, `.claude` nach `"$OM_SCRATCH/repo/"` und führe einmal `npm --prefix "$OM_SCRATCH/repo/app" ci` aus. Spätere Abgleiche nutzen denselben rsync-Aufruf; ausgeschlossene Pfade wie die Scratch-node_modules bleiben dabei erhalten.

Schritt 1, RED, Prüfung zuerst (app/e2e/kacheln.spec.ts, Funktion `messeKacheln`):
- Vor der Kachelschleife ein Array für Reiheneinträge anlegen (je Kachel: Liste als Element, li-Oberkante, Kachelhöhe aus `rahmen.height`, Unterkante des ersten sichtbaren Quelle-Knopfs oder null, Name).
- In der Kachelschleife neben `innenLinks`/`innenRechts` die Größe `innenUnten` berechnen: `rahmen.bottom` minus `zahl(stil.borderBottomWidth)` minus `zahl(stil.paddingBottom)`.
- Im Abschnitt (f) nach der Mindestmaß-Prüfung: Weicht `kasten.bottom` um mehr als `toleranz` von `innenUnten` ab, den Befund aus <behavior> mit `px(...)`-Formatierung anhängen. Die Unterkante des Knopfs in den Reiheneintrag übernehmen.
- Nach der Kachelschleife einen neuen Abschnitt „(j) Reihen im Gleichlauf“ anlegen: Einträge nach Liste und li-Oberkante (Abstand höchstens `toleranz`) gruppieren; für jede Gruppe mit mindestens zwei Einträgen die Spannweite der Höhen und, über die Einträge mit Knopf, die Spannweite der Knopf-Unterkanten prüfen und die beiden Befunde aus <behavior> erzeugen. Alles bleibt innerhalb des einen `page.evaluate` (keine Closures aus Node), Typen bleiben strikt (vue-tsc für e2e über tsconfig.e2e.json, ESLint-Flat-Config), deutsche Bezeichner ohne Umlaute.
- Den Kopfkommentar der Datei um die zwei neuen Prüfpunkte ergänzen (Quelle-Knopf am unteren Inhaltsrand; Reihe: gleiche Kachelhöhe und gleiche Knopf-Unterkante), mit Verweis auf die Quick-Aufgabe 261010-bvz.
- Abgleich in die Scratch-Kopie, `npm --prefix "$OM_SCRATCH/repo/app" run build-only`, dann vom Repo-Root `scripts/e2e-wie-ci.sh "$OM_SCRATCH/repo/app" --project=ci e2e/kacheln.spec.ts`. Erwartung: rot mit den neuen Befunden (mindestens / und /stellenplan bei 1280 px). Die Ausgabe (Route, Breite, Befund) für die SUMMARY notieren. Schlägt der Lauf rot aus einem anderen Grund fehl (Schrift, Timeout), erst das klären; ist er grün, misst die Prüfung falsch und muss korrigiert werden, bevor das CSS geändert wird.

Schritt 2, GREEN, Kachel-CSS (app/src/components/KennzahlKachel.vue, nur der Style-Block):
- Aus `.om-kennzahl__zeile` die Deklaration für den automatischen oberen Außenabstand entfernen; sie ist wirkungslos, weil `.om-kennzahl p` den Außenabstand aller Absätze auf 0 setzt und spezifischer ist. Die Zeile bleibt direkt unter dem Betrag (Gestaltungsentscheidung im Objective).
- `.om-kennzahl__quelle` bekommt `display: flex`, `margin-top: auto` und `padding-top: var(--wa-space-xs)` statt des bisherigen festen `margin-top: var(--wa-space-xs)`. Begründung: `margin-top: auto` nimmt in der Flex-Spalte den freien Platz auf und drückt die Quelle-Zeile an den unteren Inhaltsrand (Innenabstand `--wa-space-m` der Kachel bleibt); `padding-top` hält den bisherigen Mindestabstand zur Zeile (Gap xs plus xs), damit die höchste Kachel einer Reihe nicht wächst; `display: flex` verhindert eine Grundlinien-Lücke unter dem inline-flex-Knopf, sodass Knopf- und Wrapper-Unterkante zusammenfallen. Der Wrapper ist ein `div`, die Regel `.om-kennzahl p` trifft ihn nicht.
- Einen kurzen Kommentar über `.om-kennzahl__quelle` setzen, der die Ursache nennt (Spezifität von `.om-kennzahl p`) und dass die Quelle-Zeile deshalb am Wrapper und nicht an einem Absatz fixiert wird. Keine Beträge im Kommentar (die Vitest-Probe in app/src/lib/__tests__/kennzahlen.test.ts verbietet Muster wie „27,5 Mio“ in KennzahlKachel.vue).
- Nicht ändern: `height: 100%` und `box-sizing` an `.om-kennzahl`, Template, Props, QuelleKnopf.vue, basis.css (das Raster streckt die li bereits korrekt). Nur `--wa-*`-Tokens, Klassen behalten das Präfix `om-`.
- Optional die JSDoc der Prop `quelle` um „steht am unteren Rand der Kachel“ ergänzen.
- Abgleich in die Scratch-Kopie, `build-only`, erneut `scripts/e2e-wie-ci.sh "$OM_SCRATCH/repo/app" --project=ci e2e/kacheln.spec.ts`. Erwartung: grün auf allen vier Kachelrouten und allen Breiten.

Schritt 3, Commit: Nur die zwei Pfade explizit stagen (app/e2e/kacheln.spec.ts, app/src/components/KennzahlKachel.vue), Commit-Nachricht im Stil `fix(quick-261010-bvz): Quelle-Knopf der Kennzahl-Kacheln am unteren Rand fixiert` mit kurzer Begründung (Spezifität) im Rumpf und dem Co-Authored-By-Trailer aus der Session.
  </action>
  <verify>
    <automated>rsync -a --delete --exclude .git --exclude node_modules --exclude dist --exclude test-results --exclude playwright-report --exclude .venv --exclude .planning --exclude .claude ./ "$OM_SCRATCH/repo/" && npm --prefix "$OM_SCRATCH/repo/app" run build-only && scripts/e2e-wie-ci.sh "$OM_SCRATCH/repo/app" --project=ci e2e/kacheln.spec.ts</automated>
  </verify>
  <done>
- Der Lauf vor dem CSS-Fix war rot mit den neuen Befunden (in der SUMMARY mit Route, Breite und Abweichung belegt).
- Nach dem Fix ist `e2e/kacheln.spec.ts` im Projekt ci über scripts/e2e-wie-ci.sh grün (alle Routen, alle Breiten, alle bisherigen und neuen Prüfungen).
- `grep -A6 '^\.om-kennzahl__quelle {' app/src/components/KennzahlKachel.vue | grep -c 'margin-top: auto'` liefert 1.
- `grep -c 'Quelle-Knopf endet bei' app/e2e/kacheln.spec.ts` liefert mindestens 1.
- Commit enthält genau die zwei genannten Dateien.
  </done>
</task>

<task type="auto">
  <name>Task 2: Vollständige App-Prüfungen wie in der CI und Sichtprüfung</name>
  <files>app/src/components/KennzahlKachel.vue, app/e2e/kacheln.spec.ts</files>
  <action>
Alle App-Prüfungen aus CLAUDE.md in der Scratch-Kopie aus Task 1 auf dem committeten Stand ausführen (vorher mit demselben rsync-Aufruf abgleichen): `type-check`, `lint`, `format:check`, `test` (Vitest, u. a. die Quelle-Abdeckungs- und Vorlagenproben, die KennzahlKachel.vue roh lesen), `build`, danach die gesamte Playwright-Suite des Projekts ci über `scripts/e2e-wie-ci.sh "$OM_SCRATCH/repo/app"` (ohne Spec-Filter, entspricht `npm run test:e2e` in der CI; die Specs quelle.spec.ts, inventar.spec.ts und smoke.spec.ts klicken bzw. inventarisieren den Quelle-Knopf).

Schlägt `format:check` fehl: in der Scratch-Kopie `npm --prefix "$OM_SCRATCH/repo/app" run format` ausführen und nur die betroffenen der zwei Dateien zurück ins Repo kopieren. Schlägt `lint` oder `type-check` fehl: in den zwei Dateien beheben. Andere Dateien werden nicht angefasst. Gibt es Korrekturen, als eigener Commit mit nur den betroffenen der zwei Pfade (`style(quick-261010-bvz): …` bzw. `fix(quick-261010-bvz): …`, Co-Authored-By-Trailer). Ohne Korrekturen entsteht in dieser Task kein Commit.

Die Datenreproduzierbarkeit ist nicht berührt (keine Änderung an pipeline/, daten/, app/src/data/), ein Pipeline-Lauf ist nicht nötig.

Für die Sichtprüfung am Ende die Startseite und /stellenplan im Browser bei etwa 1280 px und bei 768 px ansehen (siehe human-check).
  </action>
  <verify>
    <automated>rsync -a --delete --exclude .git --exclude node_modules --exclude dist --exclude test-results --exclude playwright-report --exclude .venv --exclude .planning --exclude .claude ./ "$OM_SCRATCH/repo/" && npm --prefix "$OM_SCRATCH/repo/app" run type-check && npm --prefix "$OM_SCRATCH/repo/app" run lint && npm --prefix "$OM_SCRATCH/repo/app" run format:check && npm --prefix "$OM_SCRATCH/repo/app" run test && npm --prefix "$OM_SCRATCH/repo/app" run build && scripts/e2e-wie-ci.sh "$OM_SCRATCH/repo/app"</automated>
    <human-check>Startseite (/#/) bei etwa 1280 px und 768 px sowie /#/stellenplan bei 1280 px: In jeder Kachelreihe sind die grauen Boxen gleich hoch, und alle „Quelle“-Links samt Icon stehen auf derselben Höhe mit gleichem Abstand zur Unterkante der Box; die Zeile „Planwert … · PDF-Seite …“ steht direkt unter dem Betrag. Bei 360 px (eine Spalte) sitzt der Link ebenfalls unten in jeder Kachel.</human-check>
  </verify>
  <done>
- type-check, lint, format:check, Vitest, build und die vollständige Playwright-Suite des Projekts ci sind grün.
- `git status --porcelain -- app scripts daten pipeline` ist nach dem letzten Commit leer, und die Commits dieser Aufgabe berühren nur app/src/components/KennzahlKachel.vue und app/e2e/kacheln.spec.ts.
- Die Sichtprüfung ist als human-check für das Ende vermerkt.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| keine neue | Reine CSS-Layoutänderung einer statischen Vue-Komponente und eine Testerweiterung; keine neuen Eingaben, Daten, Requests oder Abhängigkeiten. |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-261010-bvz-01 | Denial of Service | app/src/components/KennzahlKachel.vue (Layout, Barrierefreiheit) | low | mitigate | Der Quelle-Knopf bleibt mindestens 44 × 44 px, im Inhaltsbereich und ohne Überlauf; abgesichert durch die bestehenden und die neuen Prüfungen in app/e2e/kacheln.spec.ts über alle Breiten ab 360 px. |
| T-261010-bvz-SC | Tampering | npm-Installation in der Scratch-Kopie | low | accept | Es kommen keine Pakete hinzu; `npm ci` installiert ausschließlich aus dem vorhandenen app/package-lock.json, package.json und Lockfile werden nicht geändert. Keine Paketlegitimitätsprüfung nötig. |
</threat_model>

<verification>
- RED-Lauf von e2e/kacheln.spec.ts vor dem CSS-Fix zeigt die neuen Befunde (belegt in der SUMMARY).
- GREEN: `scripts/e2e-wie-ci.sh "$OM_SCRATCH/repo/app" --project=ci e2e/kacheln.spec.ts` grün, danach die gesamte Suite des Projekts ci grün.
- type-check, lint, format:check, Vitest und build in der Scratch-Kopie grün.
- Nur app/src/components/KennzahlKachel.vue und app/e2e/kacheln.spec.ts geändert und explizit gestaged.
</verification>

<success_criteria>
- Auf allen vier Kachelrouten und bei jeder Breite von 360 bis 1440 px endet jeder Quelle-Knopf einer Kennzahl-Kachel auf der Unterkante des Inhaltsbereichs (Abstand zur Box-Unterkante = --wa-space-m), und innerhalb jeder Reihe sind Kachelhöhen und Knopf-Unterkanten gleich (Toleranz 0,5 px), automatisiert geprüft in app/e2e/kacheln.spec.ts.
- Keine Regression in den bestehenden App-Prüfungen und der CI-Playwright-Suite.
</success_criteria>

<output>
Create `.planning/quick/261010-bvz-quelle-link-in-kacheln-einheitlich-am-un/261010-bvz-SUMMARY.md` when done (mit RED-Befunden vor dem Fix, GREEN-Ergebnis und den Commit-Hashes).
</output>
