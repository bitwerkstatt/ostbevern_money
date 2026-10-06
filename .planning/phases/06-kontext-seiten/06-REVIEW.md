---
phase: 06-kontext-seiten
reviewed: 2026-10-06T00:00:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - app/src/charts/__tests__/format.test.ts
  - app/src/charts/format.ts
  - app/src/components/BindungsgradBalken.vue
  - app/src/components/MassnahmenFilter.vue
  - app/src/components/MenueGruppe.vue
  - app/src/components/ProduktBalkenListe.vue
  - app/src/lib/__tests__/bindungsgrad.test.ts
  - app/src/lib/__tests__/investitionen.test.ts
  - app/src/lib/__tests__/menueVersatz.test.ts
  - app/src/lib/__tests__/ruecklagen.test.ts
  - app/src/lib/__tests__/schulden.test.ts
  - app/src/lib/__tests__/stellen.test.ts
  - app/src/lib/bindungsgrad.ts
  - app/src/lib/investitionen.ts
  - app/src/lib/menueVersatz.ts
  - app/src/lib/ruecklagen.ts
  - app/src/lib/schulden.ts
  - app/src/lib/stellen.ts
  - app/src/pages/EntwicklungPage.vue
  - app/src/pages/InvestitionenPage.vue
findings:
  critical: 0
  warning: 1
  info: 9
  total: 10
status: issues_found
---

# Phase 6: Code Review Report (Re-Review nach Gap-Plänen 06-13 bis 06-16)

**Reviewed:** 2026-10-06
**Depth:** standard (inkrementell gegen c193e3f)
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Geprüft wurden die Änderungen seit c193e3f (`git diff c193e3f..HEAD`) an den 20 Dateien. Die Vitest-Suite wurde nicht ausgeführt (statische Prüfung, `node_modules` enthält macOS-Binaries); die Aussagen beruhen auf Lesen und Nachrechnen mit `app/src/data/haushalt.json`.

Ergebnis der Fix-Prüfung:

| Vorheriger Befund | Stand | Bewertung |
| --- | --- | --- |
| CR-01 Fußnote Rücklagen | teilweise behoben | Der Verrechnungs-Term wird jetzt genannt, aber ohne Vorzeichenregel; siehe neues WR-01. Kein Critical mehr, weil die Zahl nun nachvollziehbar zuordenbar ist und die Fußnote auf die PDF-Seite 311 verweist. |
| WR-01 `MenueGruppe` Messung | behoben | `listenVersatz()` rechnet die Basisposition (Rechteck minus angewandter Versatz) und liefert einen absoluten Versatz; `element.style.left` liest den tatsächlich im DOM stehenden Wert. Algebraisch und per Trace geprüft (zweites Öffnen, Resize, zu breite Liste); keine neuen Fehler. |
| WR-02 "1 Maßnahmen" | behoben | `anzahlText` in `format.ts`, genutzt in `ergebnisText`, `produkteText`, `segmentZusammenfassung`. Alle drei Fundstellen ersetzt; kein weiterer fester Plural im App-Code gefunden. |
| WR-03 `berechnet` auf Schulden-Kacheln | behoben | `schuldenKacheln()` setzt `berechnet` aus `kennzahlen.berechnet` auf beiden Kacheln. |
| WR-04 Teilsumme "Summe" | behoben | `summe` ist `null`, sobald eine Rücklage fehlt; Test deckt den Fall ab. |
| WR-05 `personen ?? 0` | behoben | `personen()` liefert `null` bei einer Zeile ohne Personenzahl; Tests für Vorjahr und Haushaltsjahr vorhanden. |

Neue Defekte durch die Fixes: ein Warning (Vorzeichen in der Fußnote und im zugehörigen Test), sonst nur Infos. Die Infos IN-01 bis IN-08 bleiben wie vereinbart offen und werden weitergeführt.

## Warnings

### WR-01: Fußnote "zuzüglich der Verrechnung" nennt das Vorzeichen nicht; wörtlich angewandt ergibt sie eine andere Zahl (Restmangel von CR-01)

**File:** `app/src/lib/ruecklagen.ts:146-153` (auch `:13`, `:89-91`, `:105-106`), `app/src/lib/__tests__/ruecklagen.test.ts:211-230`
**Issue:** Der Text lautet jetzt "…, zuzüglich der Verrechnung aus der Zeile „Einmalige Verrechnung Bilanzierungshilfe“, geteilt durch die allgemeine Rücklage zu Jahresbeginn." Der gedruckte Wert dieser Zeile ist aber negativ (−476.327 in der Spalte 2026, S. 311), und `abbau()` rechnet `max(0, −Ergebnis − Ausgleich) − verrechnung`, zieht den negativen Wert also ab. Wer die Fußnote wörtlich liest und den gedruckten Wert addiert, erhält 221.293 + (−476.327) < 0 statt der gezeigten 697.620 (1,77 %). Die Tabelle zeigt weder Jahresergebnis noch Verrechnung, der Leser muss die Werte also aus der PDF-Seite 311 holen und dort die Vorzeichen selbst deuten. Der Kernwert der App ("jede Zahl nachvollziehbar") ist damit für genau das Jahr 2026 weiterhin nicht ohne Raten reproduzierbar. Der Test `nachgerechnet()` zementiert die Verwechslung: sein Kommentar sagt "plus … die Verrechnung", der Code rechnet `- wert(VERRECHNUNG)`; weil der Test dieselbe Formel wie die Implementierung benutzt, kann er die Lesbarkeit des Textes nicht prüfen. Dasselbe Wort "plus"/"zuzüglich" steht in den Doc-Kommentaren von `abbau()` und im Dateikopf.
**Fix:** Die Vorzeichenregel in den Satz aufnehmen, ohne Zahl, zum Beispiel:
```ts
? `, vermehrt um den Betrag der Verrechnung aus der Zeile „${verrechnungsName}“ (dort negativ gebucht)`
```
und in den Doc-Kommentaren "abzüglich der (negativ gebuchten) Verrechnung" bzw. "um den Betrag der Verrechnung erhöht" schreiben. Im Test den Term ausdrücklich als `-verrechnung` benennen (Kommentar korrigieren) und zusätzlich prüfen, dass der Text einen Hinweis auf das Vorzeichen enthält.

## Info

### IN-01: Hard-coded hex fallback colors in components

**File:** `app/src/components/StellenNachTeil.vue:49-50`, `app/src/components/StellenNachGruppe.vue:31`, `app/src/charts/wertartStil.ts:567,572` (nicht im Re-Review-Scope; unverändert weitergeführt)
**Issue:** `KATEGORIE_FARBEN[1] ?? '#545868'`, `?? '#9194a2'` und `'white'` umgehen die Konvention "Chartfarben ausschließlich aus `echartsTheme.ts`". `RueckgangBalken`/`RuecklagenBalken` nutzen `?? ''`.
**Fix:** Benannte Konstanten aus `echartsTheme.ts` exportieren oder den Fallback entfernen.

### IN-02: Dead or test-only production exports

**File:** `app/src/lib/ruecklagen.ts:195-207` (weiter vorhanden), `app/src/lib/menue.ts:48-50`
**Issue:** `ausgleichsruecklageAufgebrauchtJahr` und `menueLinks` werden nur von Tests genutzt. `ausgleichsruecklageAufgebrauchtJahr` nutzt `haushalt.jahre.indexOf(haushalt.haushaltsjahr)` ungeprüft (−1 startet bei Index 0), obwohl wenige Zeilen weiter unten (`:219`) `haushaltsjahrIndex()` genau dafür existiert.
**Fix:** Aus der Produktions-API entfernen oder `haushaltsjahrIndex()` verwenden.

### IN-03: Duplicated helpers across lib modules

**File:** `app/src/lib/bindungsgrad.ts:68`, `app/src/lib/zuschuesse.ts:236`, `app/src/lib/kennzahlen.ts:36` (`jahrIndex`); `app/src/lib/entwicklung.ts:56` und `app/src/lib/ruecklagen.ts:64` (`wertartAn`); `app/src/lib/investitionen.ts:57` und `app/src/lib/ruecklagen.ts:219`; neu: `app/src/lib/ruecklagen.ts:125-132` (`postenName` dupliziert die Suche und Fehlermeldung von `postenWerte`, `:45-51`) und `app/src/pages/StellenplanPage.vue:96-98` (`personenText` dupliziert die Singular/Plural-Logik von `anzahlText`)
**Issue:** Gleiche "Index suchen, sonst werfen"-Logik mehrfach mit leicht abweichenden Fehlertexten. Die Gap-Fixes haben zwei weitere Duplikate eingeführt (`postenName`, `personenText`), obwohl `anzahlText` die Zero-One-Many-Regel jetzt zentral hat.
**Fix:** Ein `postenEintrag(tabelle, schluessel)` für `postenWerte` und `postenName`; `personenText` als `anzahlText(anzahl, 'Person', 'Personen')`; gemeinsame Index-Helfer in `lib/jahr.ts`.

### IN-04: Cross-module coupling for small helpers

**File:** `app/src/components/FinanzierungsDiagramm.vue:17` (`jahreListe` aus `lib/schulden`), `app/src/components/ProduktBalkenListe.vue:13` (`klickIndex` aus `lib/investitionen`), neu verstärkt durch `app/src/lib/schulden.ts:25` (`import { quellenZeile } from '@/lib/kennzahlen'`)
**Issue:** `klickIndex` zieht `lib/investitionen` samt Modul-IIFE `MASSNAHMEN_AUFGABENBEREICHE` und `vue-router` in die Rat-entscheidet-Seite. Seit WR-03 importiert `lib/schulden` zusätzlich `lib/kennzahlen` (und damit `ertragsarten`, `berechnung`); jeder Import von `jahreListe` aus `lib/schulden` hängt nun an diesem Graphen. Ein Zirkelimport besteht nicht (`kennzahlen` importiert `schulden` nicht), aber die Kopplung wächst.
**Fix:** `quellenZeile` und `jahreListe` in ein schlankes Modul (`lib/quelle.ts` bzw. `charts/format.ts`) verschieben; `klickIndex` nach `charts/`.

### IN-05: `useMassnahmenFilter` is instantiated twice per page

**File:** `app/src/components/MassnahmenFilter.vue:14`, `app/src/pages/InvestitionenPage.vue:63`
**Issue:** Seite und Filterkomponente rufen beide `useMassnahmenFilter()` auf; zwei `immediate`-Watcher, doppelte Bereinigung bei ungültigem `?pb=`, doppelte `baueVorhaben`-Berechnung. Unverändert.
**Fix:** Einmal in der Seite aufrufen und per Props/`provide` weiterreichen.

### IN-06: Minor markup and equality nits

**File:** `app/src/components/VeFaelligkeiten.vue:51`, `app/src/components/EntwicklungsDiagramm.vue:54`, `app/src/pages/EntwicklungPage.vue:39,46` (`== null`), `app/src/components/RuecklagenBalken.vue:59`, `app/src/components/ErgebnisBalken.vue:30`
**Issue:** (a) `:key="m.produkt + m.massnahmeId"` ohne Trenner; (b) lose `!=`/`==` gegen `null`; (c) `.replace(' ', '\n')` trifft das geschützte Leerzeichen von `euro()` unter 1 Mio. nicht (`zweizeilig()` kann beides). Unverändert.
**Fix:** `/`-Trenner im Key, strikte Vergleiche, `zweizeilig()`.

### IN-07: Derived sum shown without "berechnet" label; source line cites all pages on every tile

**File:** `app/src/components/ZuschussListe.vue:84`, `app/src/pages/StellenplanPage.vue:52-56`, `:102-113` (`nachwuchsSatz`)
**Issue:** "Zusammen rd. …" ohne `BerechnetEtikett`; `kachelZeile` hängt die Vereinigung aller PDF-Seiten an jede Kachel. Neu sichtbar durch WR-05: `nachwuchs().pdfSeiten` enthält auch die Seiten von Zeilen, deren Jahr wegen fehlender Personenzahl `null` ist; `nachwuchsSatz` nennt dann Seiten für ein Jahr, das im Satz gar nicht vorkommt (nur bei defekten Daten erreichbar).
**Fix:** Etikett neben abgeleiteten Summen; kachelspezifische Seitenlisten; in `nachwuchs()` nur die Seiten der Jahre mit Wert zurückgeben.

### IN-08: Pipeline formulas raise untyped errors

**File:** `pipeline/ostbevern/texte.py:317-322,328-338` (nicht im Re-Review-Scope, unverändert weitergeführt)
**Issue:** `_allgemeine_ruecklage_rueckgang_bis_letztes_jahr` teilt ohne Guard durch `anfang`; fehlende Jahresschlüssel geben ein nacktes `KeyError`.
**Fix:** `anfang == 0` abfangen und Lookups mit `TexteFehler` und Formelnamen umhüllen.

### IN-09: Neue Tests prüfen Quelltext statt Verhalten

**File:** `app/src/lib/__tests__/menueVersatz.test.ts:96-113`, `app/src/lib/__tests__/bindungsgrad.test.ts` (Block "Anzahltexte in den Komponenten"), `app/src/lib/__tests__/schulden.test.ts` ("die Seite rendert die Kacheln"), `app/src/lib/__tests__/ruecklagen.test.ts:305-308`
**Issue:** Die Verdrahtung wird über `?raw`-Quelltext und Regex/`toContain` festgenagelt (zum Beispiel `positioniere()` kommt mindestens dreimal vor, `not.toContain('soweit die Ausgleichsrücklage')`). Das ist umbenennungsanfällig, zählt auch Kommentartreffer und beweist nicht, dass das Verhalten stimmt (die tatsächliche WR-01-Korrektur, dass `element.style.left` mit dem DOM übereinstimmt, ist ohne DOM-Test nicht abgedeckt; nur die reine Funktion `listenVersatz` ist es). Fachlich korrekt ist die reine Funktion; die Lücke liegt in der Integration.
**Fix:** Entweder ein Komponententest mit `@vue/test-utils` und `happy-dom`/`jsdom`, der `getBoundingClientRect` stubbt und zweimal öffnet, oder die Quelltext-Tests auf wenige stabile Zusicherungen beschränken und als solche kommentieren.

---

_Reviewed: 2026-10-06_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
