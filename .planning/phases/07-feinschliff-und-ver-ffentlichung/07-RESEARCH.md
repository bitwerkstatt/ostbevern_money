# Phase 7: Feinschliff und Veröffentlichung - Research

**Researched:** 2026-10-06
**Domain:** Statische Vue-3-App (Vite, Hash-Router, Web Awesome, ECharts) und Python-Pipeline: PDF-Quellenbelege (WebP + Zeilenrechtecke), Barrierefreiheit, Playwright/axe/Lighthouse, GitHub-Pages-Deployment
**Confidence:** HIGH (fast alles in dieser Sitzung im Sandbox nachgemessen; offene Punkte stehen im Assumptions Log)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Quellenbelege**
- **D-01:** **„Quelle anzeigen“ gibt es an jedem Wert mit `pdf_seite`.** Das sind Kennzahlkacheln, alle `DatenTabelle`-Zeilen mit Seitenbezug und die Produktseite. Es gibt einen einzigen Mechanismus für alles, keine Auswahl „prominenter“ Werte. Heute verweisen die App-JSONs auf 188 verschiedene PDF-Seiten.
- **D-02:** **Die Seitenleiste zeigt die ganze PDF-Seite als WebP.** Gerendert wird nach Spez. 5.6 (2 px je PDF-Punkt, Qualität 60), ein Bild je Seite, das mehrere Werte nutzen. Das Zeilenrechteck (`bbox` aus `quellen.json`) wird als Overlay über das Bild gezeichnet, und die Ansicht scrollt zur markierten Zeile. Spaltenköpfe und Planüberschrift bleiben so als Kontext sichtbar. Gerendert werden nur Seiten, die tatsächlich referenziert sind, nicht alle 400.
- **D-03:** **Wird kein Rechteck gefunden, zeigt die Leiste die Seite ohne Markierung mit einem Hinweis.** Das betrifft etwa gerundete Vorberichtswerte in T€ oder berechnete Werte. Der Hinweis lautet sinngemäß „Zeile nicht automatisch markiert“. Bei berechneten Werten (`BerechnetEtikett`) steht dort, woraus sie berechnet sind. Die Pipeline bricht nicht ab, schreibt aber einen Bericht aller Werte ohne `bbox` unter `daten/pruefberichte/`. So wird die Lücke sichtbar und nicht stillschweigend hingenommen.
- **D-04:** **Die Leiste ist ein `wa-drawer` rechts, auf schmalen Bildschirmen vollbreit.** Sie hat eine Fokusfalle, Esc schließt sie, und danach kehrt der Fokus zum auslösenden Knopf zurück. Es gibt keinen URL-Zustand für die Quelle. Grundlage ist das Muster der Münster-Komponente `QuelleSeitenleiste`.

**Veröffentlichung**
- **D-05:** **Die App liegt im GitHub-Account bzw. der Organisation `bitwerkstatt`, im Repo `ostbevern-money`.** Die öffentliche URL ist `https://bitwerkstatt.github.io/ostbevern-money/`. Eine eigene Domain gibt es nicht. `base: './'` und der Hash-Router bleiben.
- **D-06:** **`ORIGINAL_PDF_URL`** in `app/src/config.ts` ist die offizielle Gemeinde-Datei: `https://www.ostbevern.de/_Resources/Persistent/3/2/6/0/3260f0ed6ed16745ad93c953c061f765866667a6/Haushalt%202026%20komplett.pdf`. Es wird keine eigene Kopie des PDFs ausgeliefert, nur die gerenderten Belegseiten (D-02). Weil die URL direkt auf die PDF-Datei zeigt, kann ein seitengenauer Link `#page=X` ergänzt werden. Ob, entscheidet der Planer.
- **D-07:** **`KONTAKT_EMAIL` = `mail@thomas-manthey.de`.** Damit ist P5 D-17 erfüllt. Die bestehende `.invalid`-Prüfung (`config.test.ts`, `istPlatzhalter`) bleibt und läuft zusätzlich im Smoke-Test.
- **D-08:** **Es gibt eine neue Seite „Über dieses Projekt“** (Route, verlinkt aus der Fußzeile). Sie enthält Impressum (verantwortliche Person, Kontakt), einen Datenschutzsatz („keine Cookies, kein Tracking, keine Drittanbieter-Requests, Hosting bei GitHub Pages“), den Hinweis „inoffizielles Projekt“ und den Dank an Code for Münster. Name und Anschrift für das Impressum fragt der **Text-Checkpoint (D-15)** ab. Die Texte nimmt der Nutzer dort ab.
- **D-09:** **Deployt wird bei jedem Push auf `main`, aber nur wenn die CI grün ist.** Dazu kommt ein manueller `workflow_dispatch`. Ein eigener Deploy-Job hängt von `pipeline`, `app` und dem Smoke-Test ab und nutzt `actions/upload-pages-artifact` und `actions/deploy-pages`, beide SHA-gepinnt. Die Rechte `pages: write` und `id-token: write` gelten nur für den Deploy-Job. Global bleibt `contents: read`.
- **D-10:** **Das GitHub-Repo legt der Nutzer selbst an** und macht den ersten Push. Der Plan liefert den Workflow und eine kurze Anleitung (README oder Plan-Checkpoint): Repo anlegen, Remote setzen, Pages-Quelle auf „GitHub Actions“ stellen. Die Verifikation der öffentlichen URL (DEPL-02) ist ein menschlicher Checkpoint nach diesem Push. Der Executor legt **kein** Repo an und pusht nicht ungefragt.

**Prüfungen**
- **D-11:** **Der Playwright-Smoke-Test läuft in der CI vor dem Deployment** und blockiert es bei einem Fehler. Er nutzt `@playwright/test`, und in der CI wird nur Chromium installiert (`npx playwright install --with-deps chromium`). Geprüft wird gegen `vite preview` des Produktions-Builds. Je Route wird geprüft: Die Seite rendert, es gibt keine Konsolenfehler, die Diagramme enthalten Daten, und es gibt keine `.invalid`-Platzhalter. Er kann ein eigener CI-Job oder ein Schritt im `app`-Job sein. Das entscheidet der Planer.
- **D-12:** **Der Smoke-Test deckt alle Routen ab, nur in der Desktop-Ansicht.** Das sind alle Menürouten, `/glossar`, die neue Seite „Über dieses Projekt“ und `/produkt/:code` für ein Beispielprodukt. Die Nutzbarkeit bei 360 px (A11Y-03) und das Öffnen der Quellenleiste werden **nicht** im Smoke-Test geprüft, sondern über Komponententests bzw. die Verifikation (VERIFICATION/UAT).
- **D-13:** **Barrierefreiheit wird zweistufig nachgewiesen.** `@axe-core/playwright` prüft im Smoke-Test jede Route und blockiert bei Verstößen. Dazu kommt ein **einmaliger Lighthouse-Lauf** auf allen Routen, mit dem a11y-Wert je Route im Verifikationsbericht (Ziel ≥ 95). Lighthouse kommt nicht als Abhängigkeit in die `package.json` und läuft nicht in der CI. Es wird einmalig über `npx` bzw. einen lokalen Chrome aufgerufen.
- **D-14:** **Paketfreigabe:** Der Nutzer hat in dieser Diskussion `@playwright/test` und `@axe-core/playwright` (npm, dev) sowie `pypdfium2` und `Pillow` (PyPI, zum Rendern der WebP-Seiten) freigegeben. Installiert werden die neuesten stabilen Versionen **ohne weiteren Checkpoint**. Lockfiles werden aktualisiert. Für jedes andere neue Paket gilt weiterhin die Regel aus Phase 1: vorher freigeben lassen.

**Text- und Aufräumdurchgang**
- **D-15:** **Die Du-Anrede wird automatisch geprüft und zusätzlich per Checkpoint abgenommen.** Ein dauerhafter Test (vitest und/oder pytest) durchsucht `texte.json`, `.vue`-Templates sowie `aria-label`/`title`-Texte nach Sie-Formen (Sie/Ihnen/Ihr/Ihre … in Großschreibung, mit Ausnahmeliste für Satzanfänge mit „sie“ im Plural). Danach legt ein Checkpoint dem Nutzer die Textliste je Seite zur Abnahme vor, zusammen mit den Texten für „Über dieses Projekt“ (D-08) und den Angaben fürs Impressum.
- **D-16:** **Tabellenalternativen werden per Inventar-Test abgesichert.** Jede `ChartCard` bzw. jedes Diagramm hat eine `DatenTabelle`. Gefundene Lücken werden geschlossen. Die Tabelle bleibt wie bisher aufklappbar unter dem Diagramm.
- **D-17:** **Token-Hygiene aus Phase 5:** `font-weight: 600` fest in `App.vue`, `--wa-font-weight-semibold`, `--wa-font-size-xl`, `--wa-space-3xs`/`2xl` außerhalb der UI-SPEC-Skala (05-UI-REVIEW). Danach gilt der Typografie-Wächter aus `stiltokens.test.ts` für **alle** App-Dateien, nicht nur für die Phase-6-Dateien.
- **D-18:** **Kosmetik aus Phase 6:** `h3` in `StellenplanPage.vue` und `.om-zuschuesse__untertitel` bekommen die Spec-Rolle (06-UI-REVIEW).
- **D-19:** **Ein DOM-Integrationstest für `MenueGruppe`** prüft das Dropdown „Mehr wissen“: Tastaturbedienung, Esc und Fokus, Drawer-Gruppe mobil.
- **D-20:** **Die offenen Code-Review-Warnungen werden erledigt:** 02-REVIEW (3 Warnungen, u. a. Vorzeichen-Beschreibung in `befunde.md`, Kommentar zu PB 09/15 mit S. 296/299) und 04-REVIEW-DISPOSITION (WR-01…WR-05, IN-02). Die Daten dürfen sich dadurch nicht ändern, der CI-Diff auf `daten/` und `app/src/data/` bleibt leer. Gibt es doch einen Diff, ist das ein Befund für den Nutzer und keine stille Änderung.

### Claude's Discretion
- Wie die Zeilenrechtecke technisch gefunden werden (Suche über `pdf_seite` plus Zeilentext bzw. Betrag mit pdfplumber, oder Koordinaten schon beim Extrahieren mitschreiben) und das genaue Schema von `quellen.json` (Spez. 4.4: Schlüssel → `{pdf_seite, bbox, bild}`)
- Wie die Quell-Schlüssel an die Werte in den App-JSONs kommen
- Ob der Smoke-Test ein eigener CI-Job ist oder ein Schritt im `app`-Job
- Wie die Du-Anrede-Prüfung im Detail heuristisch arbeitet und wie die Ausnahmeliste aussieht
- Die Reihenfolge der Pläne bzw. Wellen. Das Deployment kommt naturgemäß zuletzt.

### Deferred Ideas (OUT OF SCOPE)
- Verlinkbare Quellenbelege (`?quelle=…` im URL-Zustand) — bewusst nicht in v1 (D-04)
- Smoke-Test bei 360 px und für alle 63 Produktseiten — bewusst nicht im Smoke-Test (D-12). Ein späterer Ausbau ist möglich.
- Lighthouse CI als dauerhaftes CI-Gate — derzeit einmaliger Lauf (D-13)
- Eigene Domain für die App — derzeit nur github.io
- `/gsd-secure-phase 04` steht weiter aus (Blocker aus STATE.md). Das ist nicht Teil dieser Diskussion, sollte aber vor dem Abschluss des Meilensteins erledigt werden.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DATA-04 | Quellenbelege: PDF-Zeilenrechteck und gerenderte WebP-Seite (`quellen.json`, `public/quellen/`) | Zeilensuche trifft 92–100 % ohne Sonderlogik (Messung unten); pdfplumber- und pypdfium2-Koordinaten stimmen auch auf `/Rotate`-Seiten überein; 231 Seiten ≈ 18,5 MB WebP; `pypdfium2` und `Pillow` stehen schon im `uv.lock` |
| UI-02 | „Quelle anzeigen“ öffnet an Kennzahlen und Tabellenzeilen eine Seitenleiste | WA-Drawer-Verhalten aus dem installierten Quelltext geprüft (Fokus, Rückgabe, Animation); Schlüsselgrammatik und Verbraucherinventar unten |
| UI-06 | Alle Texte deutsch, Du-Anrede | Heuristik mit geschlossener Ausnahmeliste (Satzanfangs-„Sie“ ist mehrdeutig, Ist-Treffer gemessen) |
| A11Y-01 | Tabellenalternative je Diagramm | Laufzeit-Inventar per Playwright-DOM-Probe, Ist-Befund pro Route |
| A11Y-02 | Fokus bei Routenwechsel, Kontraste, `prefers-reduced-motion` | Router-Code vorhanden; WA-Drawer/Details ohne eigene Reduktion (Quelltext geprüft); Token-Ansatz aus UI-SPEC funktioniert technisch |
| A11Y-03 | Nutzbar ab 360 px | Messung: Seite scrollt auf allen 10 geprüften Routen nicht waagerecht (`scrollWidth == 360`) |
| A11Y-04 | Lighthouse a11y ≥ 95 | Lauf im Sandbox über Docker verifiziert: 100 auf allen Routen außer `/glossar` (98, `heading-order`) |
| QUAL-02 | Playwright-Smoke-Test | Läuft im Sandbox über das offizielle Playwright-Docker-Image; Konfiguration und Spec-Gerüst verifiziert; Befund: 0 axe-Verstöße, 0 Fremd-Requests, WA-Deprecation-Warnungen in der Konsole |
| DEPL-01 | GitHub Actions baut und deployt auf Pages | Aktionen-SHAs per `git ls-remote` ermittelt; Workflow-Gerüst, Berechtigungen, Branch-Bedingung |
| DEPL-02 | Öffentliche URL erreichbar | Nur durch menschlichen Checkpoint nach dem ersten Push prüfbar (Sandbox erreicht `bitwerkstatt.github.io` nicht) |
</phase_requirements>

## Summary

Phase 7 braucht keine neue Technologie-Entscheidung im Frontend, sondern vier Integrationen: (1) ein Pipeline-Schritt `08_quellenbelege.py`, der aus dem PDF `quellen.json` und WebP-Seiten erzeugt, (2) eine App-Schicht (`lib/quelle.ts`, `QuelleKnopf`, `QuelleSeitenleiste`, `QuelleSeite`), (3) Prüfwerkzeuge (Playwright + axe in der CI, Lighthouse einmalig) und (4) der Deploy-Job. Die Messungen dieser Sitzung zeigen, dass alle vier machbar sind und dass der Ist-Zustand der App besser ist, als die Anforderungen verlangen: axe findet auf allen zehn geprüften Routen keinen Verstoß, Lighthouse a11y liegt bei 100 (außer `/glossar`: 98 wegen `heading-order`), die Seite scrollt bei 360 px nirgends waagerecht, und es gibt keine Requests an fremde Hosts. Der Aufwand liegt also im Quellenmechanismus und in der Testinfrastruktur, nicht in A11Y-Reparaturen.

Drei Umgebungsfakten bestimmen die Planung. Erstens blockiert die Sandbox-Firewall den Playwright-Browser-Download (`cdn.playwright.dev` antwortet „Approval required“), aber das offizielle Image `mcr.microsoft.com/playwright:v1.63.0-noble` ist erreichbar, per Docker gezogen und liefert Playwright **und** ein passendes Chromium für Lighthouse. Alle Playwright- und Lighthouse-Verifikationen des Executors laufen daher über Docker (Rezepte unten, verifiziert). Zweitens läuft vitest hier in `environment: 'node'` ohne DOM; D-19 („DOM-Integrationstest“) und Komponententests brauchen entweder Playwright (freigegeben) oder `jsdom`/`@vue/test-utils` (nicht freigegeben, Checkpoint nötig). Drittens ist die Bildmenge größer als D-01 annimmt: Zählt man alle Seitenfelder der fünf Daten-JSONs (auch `quelle` und `quelle_seiten`), sind es **231** Seiten, nicht 188, gerendert **≈ 18,5 MB** WebP bei Qualität 60.

Ein Abweichungsbefund gegenüber dem UI-SPEC: Das installierte Web Awesome 3.14 fokussiert beim Öffnen des Drawers das `<dialog>` selbst (oder ein `[autofocus]`-Kind im Light DOM), **nicht** den Schließen-Knopf. Die Fokusrückgabe zum Auslöser übernimmt WA bereits (`originalTrigger`), aber auf Safari und Firefox/macOS fokussiert ein Klick einen Button nicht, dort wäre `document.activeElement` der `body`. Die eigene Rückgabe in `lib/quelle.ts` bleibt deshalb nötig.

**Primary recommendation:** Schritt 08 in `ostbevern/quellen.py` mit eigener Zeilensuche über `pdfplumber`-Wörter (Beschriftung plus Betrags-Gegenprobe, Rand 2 pt, 2-Dezimalstellen-Rundung), Bilder nur rendern, wenn sie fehlen (WebP-Bytes nicht in der CI-Diff-Prüfung), `quellen.json` unter `app/src/data/` mit einer Schlüsselgrammatik, die die App aus vorhandenen JSON-Feldern ableitet; Playwright-Specs (Smoke plus axe, Menü/Quelle-Interaktion, 360 px) laufen im Sandbox per Docker-Image und in der CI nach `npx playwright install --with-deps chromium`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Zeilenrechtecke finden, Seiten rendern, `quellen.json` schreiben | Pipeline (Python, Build-Zeit) | — | Das PDF liegt nur in `raw_data/`; die App darf nie PDF lesen (statisch, kein Backend) |
| WebP-Seiten ausliefern | CDN / Static (`app/public/quellen/`) | Browser (lazy, erst beim Öffnen) | Statische Dateien; Bild wird erst nach Klick geladen |
| Schlüssel → Beleg auflösen, Knopf nur bei vorhandenem Eintrag | Browser (`lib/quelle.ts`) | — | Reine Datensuche aus gebündelter `quellen.json` |
| Seitenleiste, Fokus, Markierung, Scrollen | Browser (`wa-drawer` + Vue) | — | Reines UI-Verhalten, kein URL-Zustand (D-04) |
| bbox → Prozent umrechnen | Browser (`QuelleSeite`) | Test (Komponentenlogik als reine Funktion) | Fehler hier verschiebt die Markierung unbemerkt |
| Tabellenalternative / Inventar | Browser (Komponenten) | Test (Laufzeit-DOM per Playwright) | Prüfung am gerenderten DOM ist robuster als Quelltext-Regex |
| Fokus bei Routenwechsel, Reduced Motion | Browser (Router `afterEach`, `basis.css`) | — | Vorhanden; Phase 7 weist nach |
| Smoke-/axe-/Quellen-/Mobil-Specs | CI-Runner bzw. Docker (Playwright gegen `vite preview`) | — | Produktions-Build ist der Prüfgegenstand |
| Build, Smoke, Deploy | CI (GitHub Actions) | GitHub Pages (Hosting) | Pages-Artefakt-Flow, Deploy nur von `main` |
| Impressum/Kontakt-Werte | Browser (`config.ts` + `UeberPage`) | Test (`istPlatzhalter`) | Statischer App-Text ohne Zahlen |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `@playwright/test` | 1.63.0 (`latest`, veröffentlicht 2026-09-04) | Smoke-Test, Interaktions-Specs | Von D-11/D-14 freigegeben; verifiziert im Sandbox-Docker-Lauf [VERIFIED: npm view, Docker-Lauf dieser Sitzung] |
| `@axe-core/playwright` | 4.13.0 (veröffentlicht 2026-08-11; Peer `playwright-core >= 1.0.0`, Dependency `axe-core ~4.13.0`) | axe-Prüfung je Route | Von D-13/D-14 freigegeben; verifiziert [VERIFIED: npm view + Lauf] |
| `pypdfium2` | 5.13.0 bereits in `pipeline/uv.lock` (neueste PyPI-Version 5.14.0 vom 2026-10-04) | Seite als Bitmap rendern | Transitive Abhängigkeit von `pdfplumber` (im Lock und in `.venv` vorhanden); D-14 gibt es frei. **Empfehlung: Lock-Version 5.13.0 beibehalten, direkt als `pypdfium2>=5.13.0` deklarieren, nicht auf die zwei Tage alte 5.14.0 heben** [VERIFIED: pipeline/uv.lock, pip index versions] |
| `Pillow` | 12.3.0 bereits im Lock (= neueste PyPI-Version) | WebP-Kodierung (`libwebp 1.6.0` im Rad) | Ebenfalls transitive Abhängigkeit von `pdfplumber`; D-14 [VERIFIED: pipeline/uv.lock, `PIL.features.check('webp')` → True] |

### Supporting
| Library / Werkzeug | Version | Purpose | When to Use |
|--------------------|---------|---------|-------------|
| `lighthouse` (nur `npx`/Scratch, nie in `package.json`) | 13.5.0 (Node ≥ 22.19; veröffentlicht 2026-09-18) | Einmaliger a11y-Lauf je Route (D-13) | Verifikationsbericht; läuft im Sandbox mit dem Chromium des Playwright-Images [VERIFIED: Lauf dieser Sitzung] |
| `mcr.microsoft.com/playwright:v1.63.0-noble` | Tag muss exakt zur Playwright-Version passen | Browser und Systembibliotheken im Sandbox | Alle Playwright- und Lighthouse-Läufe des Executors; arm64- und amd64-Manifest vorhanden, Image gezogen (3,48 GB Plattenplatz) [VERIFIED: docker manifest inspect, docker pull] |
| `actions/upload-pages-artifact` | v5.0.0 = `fc324d3547104276b827a68afc52ff2a11cc49c9` | Pages-Artefakt hochladen | Deploy-Weg nach D-09 [VERIFIED: git ls-remote] |
| `actions/deploy-pages` | v5.0.1 = `368f82528645a54fb793d4d04e342629a3f51346` (v5 läuft auf Node 24) | Artefakt deployen | Deploy-Job [VERIFIED: git ls-remote, Release-Notes] |
| `@fortawesome/fontawesome-free` (nur `npm pack`, **nicht** installieren) | 7.3.1 | Quelle für `file-lines.svg` | Die vorhandenen Icons unter `app/public/icons/solid/` sind byte-identisch mit `svgs/solid/*.svg` dieses Pakets (geprüft an `circle-info.svg`); `file-lines.svg` ist enthalten [VERIFIED: npm pack + diff] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Playwright für D-19/Quelle-Interaktion | `jsdom`/`happy-dom` + `@vue/test-utils` in vitest | Schneller, aber **nicht freigegeben** (D-14) und Web-Awesome-Custom-Elements (Drawer, Dialog-Fokus) laufen in jsdom nicht echt; Playwright prüft das echte Verhalten. Empfehlung: Playwright |
| Smoke als eigener CI-Job | Schritt im `app`-Job | Eigener Job braucht Build-Artefakt-Weitergabe (zusätzliches `upload-artifact`, weiterer SHA-Pin). Empfehlung: Schritt im `app`-Job, nach `build`, vor `upload-pages-artifact` |
| `actions/configure-pages` | weglassen | Mit `base: './'` nicht nötig (kein base-Pfad zu injizieren); spart einen Pin. Wer es doch nutzt: v6.0.0 = `45bfe0192ca1faeb007ade9deae92b16b8254a0d` [VERIFIED: git ls-remote] |
| WebP-Bytes in der CI-Diff-Prüfung | nur `quellen.json`, Dateiliste und Bildmaße prüfen | Byte-Identität über macOS/Linux/x86/arm ist nicht belegt (siehe Pitfall 2). Empfehlung: Bilder nur rendern, wenn sie fehlen |

**Installation:**
```bash
# App (im Scratch-Repo bzw. nach Freigabe; Lockfile wird aktualisiert)
npm --prefix app install -D @playwright/test@1.63.0 @axe-core/playwright@4.13.0

# Pipeline: bereits transitive Abhängigkeiten, nur direkt deklarieren (hebt die Lock-Versionen nicht)
uv add --directory pipeline "pypdfium2>=5.13.0" "Pillow>=12.3.0"
```

**Version verification:** `npm view @playwright/test version` → 1.63.0; `npm view @axe-core/playwright version` → 4.13.0; `npm view lighthouse version` → 13.5.0; `pip index versions pypdfium2` → 5.14.0 (Lock: 5.13.0); `pip index versions Pillow` → 12.3.0. Registry und PyPI sind aus dem Sandbox erreichbar.

## Package Legitimacy Audit

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| `@playwright/test` | npm | langjährig, 1.63.0 vom 2026-09-04 | Seam: unbekannt (Sandbox), real sehr hoch | github.com/microsoft/playwright | SUS (nur `unknown-downloads`) | **Vom Nutzer in D-14 ausdrücklich freigegeben**, kein Postinstall (`scripts.postinstall` leer) |
| `@axe-core/playwright` | npm | langjährig, 4.13.0 vom 2026-08-11 | Seam: unbekannt | github.com/dequelabs/axe-core-npm | SUS (nur `unknown-downloads`) | **D-14 freigegeben**, kein Postinstall |
| `pypdfium2` | PyPI | langjährig; 5.14.0 vom 2026-10-04 | Seam: unbekannt | github.com/pypdfium2-team/pypdfium2 | SUS (`too-new` wegen 5.14.0, `unknown-downloads`) | **D-14 freigegeben**; seit Phase 1 im Lock als `pdfplumber`-Abhängigkeit (5.13.0). Lock-Version beibehalten |
| `Pillow` | PyPI | langjährig, 12.3.0 vom 2026-07-01 | Seam: unbekannt | github.com/python-pillow/Pillow | SUS (nur `unknown-downloads`) | **D-14 freigegeben**; bereits im Lock |
| `lighthouse` | npm | langjährig, 13.5.0 vom 2026-09-18 | Seam: unbekannt | github.com/GoogleChrome/lighthouse | SUS (`too-new`, `unknown-downloads`) | **Nicht in D-14 genannt.** D-13 legt den `npx`-Einsatz fest, ohne ihn als Paketfreigabe zu benennen. Planer setzt ein kurzes `checkpoint:human-verify` vor den ersten Lauf (oder vermerkt D-13 als Freigabe). Version fest auf 13.5.0 pinnen, nie in `package.json` |

Alle `SUS`-Urteile beruhen darauf, dass die Seam-Download-Zähler im Sandbox nicht abrufbar waren (`weeklyDownloads: null`) bzw. dass die jeweils neueste Version jung ist; keines der Pakete hat ein Postinstall-Skript (`npm view … scripts.postinstall` leer). Quelle der Namen sind D-13/D-14 (Nutzerfreigabe), nicht Websuche.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** alle fünf obigen (siehe Disposition; vier sind durch D-14 freigegeben, nur `lighthouse` verlangt einen Checkpoint)

## Architecture Patterns

### System Architecture Diagram

```
raw_data/haushalt-2026.pdf
        |
        v
  [Schritt 08 ostbevern/quellen.py]
   |-- liest daten/aufbereitet/*.csv, daten/manuell/*.csv|meta.json   (welche Werte brauchen einen Beleg: Schlüssel, pdf_seite, Suchtext, Beträge)
   |-- pdfplumber (nur pdf.py): Wörter mit top/bottom je Seite
   |-- Zeilensuche: Abschnitt+Nr. (Pläne) | Beschriftung + Betrags-Gegenprobe (Rest)
   |-- Treffer: bbox mit 2 pt Rand, auf Seite begrenzt | kein Treffer: bbox = null + Eintrag im Bericht
   |-- pypdfium2 + Pillow: nur fehlende Seiten rendern  (scale=2, WEBP q60)
   v
 app/src/data/quellen.json  (CI-Diff-Prüfung)      app/public/quellen/s{nnn}.webp  (nur Existenz+Maße prüfen)
 daten/pruefberichte/quellenbelege.md  (Werte ohne bbox, CI-Diff-Prüfung)
        |
        v
  [Vite-Build]  quellen.json im Bundle, webp als statische Dateien in dist/quellen/
        |
        v
  [Browser]
   Kachel/Tabellenzeile --QuelleKnopf(schluessel)--> lib/quelle.ts: Beleg nachschlagen
        | (Knopf nur, wenn Schlüssel existiert)
        v
   oeffneQuelle({schluessel, bezeichnung, ausloeser}) --> globales wa-drawer (App.vue, zweite Instanz)
        |--> Wertzeile + Hinweis (bbox null / berechnet) + Link ins Original-PDF (#page=n)
        |--> QuelleSeite: <img BASE_URL+quellen/bild> + Overlay (bbox/Seitenmaß in %) + scrollIntoView
        '--> wa-after-hide: Fokus zurück zum Auslöser (sonst h1)

  [CI]  pipeline-Job --\
        app-Job: ci, type-check, lint, format, vitest, build, playwright install,
                 Playwright (Smoke+axe), upload-pages-artifact (nur main)  --> deploy-Job (nur main/dispatch) --> GitHub Pages
```

### Recommended Project Structure
```
pipeline/
├── 08_quellenbelege.py          # dünner typer-Einstieg, --jahr, --neu-rendern
├── ostbevern/quellen.py         # Zeilensuche, Schlüssel, Rendern, JSON/Bericht schreiben
├── ostbevern/pdf.py             # + Methode für Wörter mit bottom (einzige pdfplumber-Stelle)
└── tests/test_quellen.py
daten/pruefberichte/quellenbelege.md      # Werte ohne bbox (D-03)
app/
├── public/quellen/s062.webp ...          # 231 Dateien, 3-stellig nullgepolstert
├── public/icons/solid/file-lines.svg     # neu (aus FA Free 7.3.1)
├── e2e/                                  # Playwright-Specs (smoke, interaktion, mobil)
├── playwright.config.ts
├── tsconfig.e2e.json                     # lib: DOM, in tsconfig.json referenziert
└── src/
    ├── data/quellen.json
    ├── lib/quelle.ts                     # Zustand + Schlüssel-Hilfen
    ├── components/QuelleKnopf.vue | QuelleSeitenleiste.vue | QuelleSeite.vue
    └── pages/UeberPage.vue
```

### Pattern 1: `quellen.json`-Schema und Schlüsselgrammatik (Claude's Discretion)
**What:** Zwei Karten: `seiten` (je referenzierte Seite Bild und Maße) und `belege` (je Wert Seite, bbox, Bild, optional Herleitung). Das hält Spez. 4.4 („Schlüssel → `{pdf_seite, bbox, bild}`“) ein und liefert dem UI die Maße, die es braucht.
**When to use:** Immer; das UI braucht laut UI-SPEC Seitennummer, Bildname, Breite/Höhe in Punkten, `bbox` oder `null`, optional Herleitungstext.
**Example:**
```json
{
  "haushaltsjahr": 2026,
  "seiten": { "62": { "bild": "s062.webp", "breite": 595.28, "hoehe": 841.89 } },
  "belege": {
    "plan:ergebnisplan:GESAMT:-:steuern": {
      "pdf_seite": 62, "bild": "s062.webp", "bbox": [41.9, 142.3, 560.7, 154.3]
    },
    "kz:aufwendungen": {
      "pdf_seite": 62, "bild": "s062.webp", "bbox": null,
      "herleitung": "Ordentliche Aufwendungen plus außerordentliche Aufwendungen"
    }
  }
}
```
Koordinaten sind Punkte, Ursprung oben links (= `top`/`x0` von pdfplumber), auf **2 Dezimalstellen gerundet** (sonst entstehen Gleitkomma-Diffs). Anzeige: `bbox ÷ Seitenmaß` in Prozent.

**Empfohlene Schlüsselgrammatik** (die App leitet Schlüssel aus Feldern ab, die die JSONs schon haben; die App-JSONs ändern sich nicht, D-20-Diff bleibt leer). Die Spaltennamen stammen aus den CSV-Köpfen dieser Sitzung:

| Beleg-Art | Schlüssel | Identität aus (CSV / JSON) | Suchstrategie |
|-----------|-----------|----------------------------|---------------|
| Ergebnis-/Finanzplanzeile | `plan:{ergebnisplan\|finanzplan}:{ebene}:{code oder -}:{zeile_kanonisch}` | `ergebnisplan.csv`, `finanzplan.csv`: `ebene,code,…,zeile,zeile_kanonisch,…,pdf_seite` | Abschnitt der Seite (vorhandene `lies_abschnitte`) + erstes Wort der Zeile == `zeile` (z. B. `01` bei x ≈ 44) |
| Grundzahl | `gz:{produkt}:{position}` | `grundzahlen.csv`: `produkt,position,…,bezeichnung,…,pdf_seite` | normalisierte `bezeichnung` auf der Seite |
| Erläuterung | `er:{produkt}:{block}:{position}` | `erlaeuterungen.csv`: `produkt,block,position,zu_zeilen,betrag,text,pdf_seite` | Textanfang; mehrzeilig: Vereinigung der Zeilen oder `null` |
| Investitionsmaßnahme | `inv:{produkt}:{massnahme_id}:{konto}:{richtung}` | `investitionen.csv`: `produkt,massnahme_id,…,konto,…,richtung,…,pdf_seite` | `konto` (6 Ziffern) auf der Seite + Betrags-Gegenprobe |
| VE-Fälligkeit | `ve:{produkt}:{massnahme_id}:{konto}` | `ve_faelligkeiten.csv`: `produkt,massnahme_id,konto,jahr,betrag,pdf_seite` | `konto` + `massnahme_id` |
| Stelle | `sp:{teil}:{position}` | `stellenplan.csv`: `teil,position,gruppe,amtsbezeichnung,…,pdf_seite` | `gruppe`/`amtsbezeichnung` (Achtung: `amtsbezeichnung` ist oft leer, dann `gruppe`) |
| Vorberichtsposten | `vb:{tabelle}:{posten}` | manuelle CSVs: `tabelle,position,posten,posten_name,…,quelle` | `posten_name` + Betrag in T€ |
| Meta-Wert | `meta:{pfad}` z. B. `meta:einwohner` | `meta.json`: Felder `quelle` | Betragsformat (€ und T€), sonst `null` |
| Kennzahl (berechnet/zusammengesetzt) | `kz:{schluessel}` | `lib/kennzahlen.ts` | Zeile der Hauptquelle oder `null` + `herleitung` |
| Seitenebene (Rückfall) | `seite:{n}` | jeder `pdf_seite` ohne Zeilenbeleg | immer `bbox: null` |

**Key insight:** Der Rückfall `seite:{n}` stellt sicher, dass jede in den JSONs vorkommende Seite mindestens einen Beleg hat; ein Test (siehe Validation) listet alle `pdf_seite`-Werte der App-JSONs ohne passenden Schlüssel und scheitert. Das ist der Test, den UI-SPEC E1 „error“ verlangt.

### Pattern 2: Zeilensuche mit Betrags-Gegenprobe
**What:** Eine Zeile gilt als gefunden, wenn die normalisierte Beschriftung (bzw. bei Plänen Abschnitt und Zeilennummer) trifft **und** mindestens ein erwarteter Betrag in gedruckter deutscher Schreibweise (`19.614.808`; bei Vorberichtstabellen in T€) in derselben Zeile steht. Mehrdeutige Beschriftungen (Konto mehrfach auf einer Seite, „Summe“) werden so aufgelöst. Kein Treffer: `bbox = null`, Eintrag im Bericht (D-03).
**When to use:** Alle Beleg-Arten außer reinen Seitenbelegen.
**Messung (Prototyp, naive Präfix-Suche ohne Gegenprobe, `zeilen_fein` + `normalisiere`):** Vorbericht/manuelle Tabellen 146 von 158 Zeilen; Grundzahlen 220/220; Investitionen (Konto) 137/137; Erläuterungen 226/229; Stellenplan 6/27 bei leerer `amtsbezeichnung` (dort `gruppe` nehmen). Die Fehlschläge sind erklärbar (Zeilenumbruch, fehlende `posten_name`, Silbentrennung). Erwartung: `null`-Anteil im niedrigen einstelligen Prozentbereich plus berechnete Kennzahlen. [VERIFIED: Prototyp-Läufe dieser Sitzung gegen `raw_data/haushalt-2026.pdf`]
**Example:**
```python
# Koordinaten: pdfplumber liefert x0/x1/top/bottom in PDF-Punkten, Ursprung oben links.
# Quelle: Probelauf dieser Sitzung (Overlay auf pypdfium2-Bild bei scale=2 deckt Wörter exakt)
def bbox_mit_rand(woerter, seite_breite, seite_hoehe, rand=2.0):
    x0 = max(0.0, min(w["x0"] for w in woerter) - rand)
    top = max(0.0, min(w["top"] for w in woerter) - rand)
    x1 = min(seite_breite, max(w["x1"] for w in woerter) + rand)
    bottom = min(seite_hoehe, max(w["bottom"] for w in woerter) + rand)
    return [round(x0, 2), round(top, 2), round(x1, 2), round(bottom, 2)]
```
Hinweis zu `pdf.py`: Das Docstring-Gebot lautet „Dieses Modul ist die einzige Stelle, die `pdfplumber` importiert.“ Das vorhandene `Wort` hat `top`, aber kein `bottom`. Eine Methode für Wörter mit `bottom` gehört deshalb in `pdf.py` (neues, standardbelegtes Feld am Ende von `Wort` oder eigener Typ), nicht als `import pdfplumber` in `quellen.py`.

### Pattern 3: Rendern mit pypdfium2 + Pillow
**What:** Eine Datei je Seite, nur wenn sie fehlt.
**Example:**
```python
# Verifiziert in dieser Sitzung (Seiten 20, 62, 87, 291, 311, 284; je zweimal gespeichert, Bytes gleich)
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(str(pdf_pfad))
try:
    bild = pdf[seite - 1].render(scale=2).to_pil()      # 2 px je PDF-Punkt (Spez. 5.6)
    bild.save(ziel, "WEBP", quality=60, method=6)        # Qualität 60 (Spez. 5.6)
finally:
    pdf.close()
```
Gemessen: Hochformat 1191×1684 px, Querformat 1684×1191 px; 20–180 KB je Seite; alle 231 referenzierten Seiten zusammen 18,5 MB (Q60), Renderzeit ≈ 21 s für den ganzen Satz. [VERIFIED: Lauf dieser Sitzung]
**Rotation:** 22 Seiten sind Querformat (842×595 pt), mindestens ab S. 284 mit `/Rotate 90`. pdfplumber und pypdfium2 melden dasselbe Seitenmaß (Test über alle 400 Seiten: kein Unterschied), und die pdfplumber-Wortkästen liegen auf dem pypdfium2-Bild bei `scale=2` exakt auf dem Text (Overlay auf S. 291 geprüft; Hoch- wie Querformat bleibt dieselbe Umrechnung `Pixel = 2 × Punkt`). [VERIFIED: Overlay-Bild und Vergleichslauf dieser Sitzung]

### Pattern 4: Playwright-Konfiguration und Smoke-Gerüst
**What:** Gegen `vite preview` des Produktions-Builds. Konfiguration und Spec sind im Sandbox-Docker-Lauf grün gelaufen (10 Tests).
**Example:**
```ts
// app/playwright.config.ts   (verifiziert im Lauf; CI-Varianten in Kommentaren)
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  reporter: 'list',                       // CI zusätzlich: ['html', { open: 'never' }]
  // forbidOnly: !!process.env.CI,
  use: { baseURL: 'http://localhost:4173/' },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
  webServer: {
    command: 'npm run preview -- --port 4173 --strictPort',
    url: 'http://localhost:4173/',
    reuseExistingServer: false,           // lokal ggf. !process.env.CI
  },
})
```
```ts
// app/e2e/smoke.spec.ts (Auszug; getestet, lieferte je Route: Überschrift sichtbar, canvas-Anzahl, axe-Verstöße, Konsole, Fremd-Requests)
import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

test(`route ${route}`, async ({ page }) => {
  const meldungen: string[] = []
  const fremd: string[] = []
  page.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') meldungen.push(m.text()) })
  page.on('pageerror', (e) => meldungen.push(e.message))
  page.on('request', (q) => { if (!q.url().startsWith('http://localhost:4173/')) fremd.push(q.url()) })
  await page.goto(`/#/${route}`)
  await page.waitForLoadState('networkidle')
  await expect(page.locator('h1')).toBeVisible()
  const axe = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze()
  expect(axe.violations).toEqual([])
  expect(fremd).toEqual([])
  expect(meldungen).toEqual([])
})
```
**Routenliste:** aus `MENUE` ableiten. `app/src/lib/menue.ts` hat keine Imports und ist deshalb aus einem Playwright-Spec importierbar (`import { menueLinks } from '../src/lib/menue'`; `menueLinks()` löst Gruppen auf, Namen entsprechen den Routennamen, z. B. `rat-entscheidet`). Ergänzen um `glossar` (steht schon im Menü), `ueber` und `produkt/020701`.
**Beispielprodukt:** `020701` „Feuer- und Bevölkerungsschutz“ hat 8 Grundzahlen, 16 Erläuterungen und Investitionen samt VE-Fälligkeit; 19 Produkte haben alle drei Teile. [VERIFIED: `produkte.json` + `investitionen.json` ausgewertet]

### Pattern 5: Diagramm-Daten im Smoke-Test prüfen
**What:** `BaseChart.vue` kennt vier Zustände (`laedt`, `fehler`, `istLeer`, Diagramm). Die Zustandsklassen sind stabil: `.om-base-chart__chart` (Diagramm mit Daten), `.om-base-chart__zustand` (Fehler/Leer). Je Route: Anzahl `.om-base-chart__chart` ≥ erwartete Diagramme und `.om-base-chart__zustand` == 0 in der Standardansicht. Für „Daten enthalten“ zusätzlich `canvas` mit Breite/Höhe > 0.
**Empfehlung (kleiner Produktivcode-Eingriff):** `BaseChart` setzt am Diagramm-Container ein `data-om-datenpunkte`-Attribut (Anzahl der Einträge in `data`/`links`/`edges`, dieselbe Zählung wie `istLeer`). Dann prüft der Test echte Datenmengen statt nur Existenz eines Canvas. Ohne Eingriff geht nur der Klassen- und Canvas-Test (schwächer, aber ohne Produktivänderung).
**Messung Ist:** `/` 0 Diagramme (nur Kacheln, 0 Tabellen), `/einnahmen` 3, `/ausgaben` 2, `/geldfluss` 1, `/entwicklung` 9, `/investitionen` 5, `/rat-entscheidet` 4, `/stellenplan` 6; die Produktseite hat **keine** Diagramme (nur Tabellen). Für die Produktseite bedeutet „Diagramme enthalten Daten“ also nur „Tabellen haben Zeilen“.

### Pattern 6: Deploy-Job (D-09)
**What:** Der `app`-Job lädt nach Smoke das Artefakt hoch (nur `main`), der `deploy`-Job hängt von `pipeline` und `app` ab.
**Example:**
```yaml
# Ergänzungen zu .github/workflows/ci.yml
on:
  push:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read                      # bleibt global

jobs:
  app:
    # ... bestehende Schritte bis "Build" ...
    steps:
      - name: Playwright-Chromium installieren
        run: npx playwright install --with-deps chromium
      - name: Smoke-Test (Playwright + axe)
        run: npm run test:e2e
      - name: Seite für GitHub Pages hochladen
        if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'
        uses: actions/upload-pages-artifact@fc324d3547104276b827a68afc52ff2a11cc49c9 # v5.0.0
        with:
          path: app/dist              # relativ zum Workspace, die `working-directory` des Jobs gilt für `with` nicht

  deploy:
    needs: [pipeline, app]
    if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    concurrency:
      group: pages
      cancel-in-progress: false
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Auf GitHub Pages veröffentlichen
        id: deployment
        uses: actions/deploy-pages@368f82528645a54fb793d4d04e342629a3f51346 # v5.0.1
```
Quelle: Workflow-Gerüst nach der offiziellen Dokumentation von `actions/deploy-pages` (Berechtigungen `pages: write`, `id-token: write`, Environment `github-pages`) [CITED: github.com/actions/deploy-pages] und `actions/upload-pages-artifact` (Eingaben `path`, `name`, `retention-days`; Artefakt: ein gzip mit genau einem tar, keine Links) [CITED: github.com/actions/upload-pages-artifact]. SHA-Auflösung: Tags sind leichtgewichtig, die ermittelten SHAs sind Commits (gleiche Methode bestätigt die vorhandenen Pins `actions/checkout` v7.0.1 = `3d3c42e5…` und `actions/setup-node` v7.0.0 = `82076278…`). [VERIFIED: git ls-remote]

### Pattern 7: Seitenleiste mit `wa-drawer` (Verhalten laut installiertem Quelltext)
**Was der Quelltext von `@awesome.me/webawesome@3.14.0` tatsächlich tut** (gelesen aus `dist/chunks/chunk.2UZFSBAI.js`, Drawer-Klasse):
- `show()`: `this.originalTrigger = document.activeElement;` dann `showModal()`; im nächsten Frame `this.querySelector("[autofocus]")` (nur Light-DOM-Kinder), sonst `this.drawer.focus()` (das `<dialog>` selbst).
- Nach dem Schließen: `const trigger = this.originalTrigger; if (typeof trigger?.focus === "function") { setTimeout(() => trigger.focus()); }`, danach Ereignis `wa-after-hide`.
- Animation: `animateWithClass(this.drawer, "show"|"hide")`; löst sofort auf, wenn `el.getAnimations().length === 0` (im Frame danach). `--show-duration`/`--hide-duration` stehen auf `var(--wa-transition-normal)`.
- Kein `prefers-reduced-motion` im Drawer-, Details- oder Tooltip-Quelltext (Suche in den jeweiligen Chunks: 0 Treffer).
**Konsequenzen:**
1. **Abweichung vom UI-SPEC:** „Beim Öffnen liegt der Fokus auf dem Schließen-Knopf (WA-Standard)“ stimmt nicht. WA fokussiert den benannten Dialog; der Schließen-Knopf ist der erste Tab-Stopp. Der Schließen-Knopf liegt im Shadow-DOM und kann kein `autofocus` tragen. Empfehlung: Vertrag auf „Fokus liegt im Dialog (Name: ‚Quelle: PDF-Seite {n}‘), Tab führt zu Schließen-Knopf, Link, Bildbereich“ ändern und im Playwright-Spec prüfen; die Alternative `autofocus` auf dem Link ins Original wäre ein bewusster Eingriff.
2. **Eigene Fokusrückgabe bleibt nötig:** WA nimmt `document.activeElement` beim Öffnen. Safari und Firefox auf macOS fokussieren einen Button beim Klick nicht, dort wäre das der `body`. `lib/quelle.ts` merkt sich `event.currentTarget` und fokussiert in `wa-after-hide` selbst (wie `beiAfterHide` im Menü-Drawer in `App.vue`). Ob `h1` als Rückfall nötig ist, wenn der Auslöser nicht mehr im DOM ist: ja (UI-SPEC).
3. **Reduced Motion:** Die Tokens `--wa-transition-fast|normal|slow` auf `0ms` plus `wa-drawer { --show-duration: 0s; --hide-duration: 0s }` genügen technisch, weil `animateWithClass` bei fehlender Animation sofort auflöst; `animation: none` wäre ebenfalls unkritisch. Wert immer als Dauer (`0ms`), nicht als bloße `0`.
4. **Bild erst beim Öffnen laden:** Der Drawer-Inhalt liegt im Light DOM. Ein `<img>` im Slot würde auch im geschlossenen Zustand geladen. `QuelleSeite` deshalb per `v-if` an den geöffneten Zustand binden.

### Anti-Patterns to Avoid
- **WebP-Bytes in die CI-Diff-Prüfung aufnehmen:** Cross-Plattform-Identität der Bytes ist nicht belegt (Pitfall 2).
- **Koordinaten beim Extrahieren in bestehende CSVs schreiben:** Würde alle Daten-Diffs und alle Prüfregeln berühren und D-20 („Daten ändern sich nicht“) verletzen. Schritt 08 findet Zeilen eigenständig.
- **Schlüssel in die App-JSONs schreiben:** Ändert alle Daten-JSONs; Ableitung in `lib/quelle.ts` aus vorhandenen Feldern ist stabiler, mit Querprüfung per Test.
- **`v-html`, feste Zahlen, Pfade mit führendem `/`:** gelten weiter (`import.meta.env.BASE_URL` für Belegbilder).
- **`document.activeElement` allein als Auslöser:** siehe Pattern 7 (Safari).
- **`vitest` mit `jsdom` ohne Freigabe einführen:** D-14.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Kontrastprüfung, Landmarken, ARIA-Regeln | Eigene Heuristiken | `@axe-core/playwright` (Tags `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa`) | Schattendom-Grenzen von Web Awesome, Regelwerk gepflegt |
| Barrierefreiheits-Score | Eigene Bewertung | `lighthouse` (nur `accessibility`, einmaliger Lauf) | D-13 verlangt den Lighthouse-Wert |
| Fokusfalle, Esc, Hintergrund-Inertheit, Scroll-Sperre | Eigene Falle | nativer modaler `<dialog>` über `wa-drawer` | Browser-Standard, WA kapselt es |
| PDF → Bitmap | Eigene Rasterung | `pypdfium2` (`render(scale=2).to_pil()`) | PDFium, bereits transitiv im Lock |
| WebP-Kodierung | Eigener Encoder, Fremdtool | `Pillow` (`save(..., "WEBP", quality=60, method=6)`) | Im Rad enthalten (libwebp 1.6.0) |
| Wort-/Zeilenkoordinaten | Eigener PDF-Parser | `pdfplumber` über `ostbevern/pdf.py` | Bereits Projektstandard; Koordinaten verifiziert |
| Seitenzeile/Abschnitt der Pläne | Neue Abschnittslogik | `plaene.lies_abschnitte` und `zeilen.normalisiere_bezeichnung` | Vorhanden, geprüft |
| Browser in CI/Sandbox | Eigener Chromium-Download | `npx playwright install --with-deps chromium` (CI) bzw. das offizielle Docker-Image (Sandbox) | Passende Systembibliotheken, versionsgleich |
| Pages-Deployment | Eigenes `gh-pages`-Branch-Skript | `actions/upload-pages-artifact` + `actions/deploy-pages` | D-09; OIDC statt Token-Push |
| Du/Sie-Erkennung per NLP | Sprachmodell oder Parser | Regex plus geschlossene, geprüfte Ausnahmeliste (siehe Pitfall 6) | Deterministisch, kein neues Paket |

**Key insight:** Alles Schwere (Rendern, axe, Lighthouse, Pages) existiert als Werkzeug; Eigenbau lohnt nur bei der **Zeilensuche** und dem **Mapping Wert → Schlüssel**, weil das Projektwissen ist.

## Runtime State Inventory

Nicht zutreffend (kein Rename-, Refactor- oder Migrationsvorhaben). Die Token-Hygiene (D-17, D-18) ersetzt CSS-Werte im Quelltext, ohne Daten, Dienste, OS-Registrierungen oder Secrets zu berühren. Einzige „nach dem Edit noch alte Zustände“-Frage: **Build-Artefakte.** `app/dist/` im Repo-Verzeichnis ist ein veralteter macOS-/Altbuild und in `.gitignore`; Checks laufen in der Scratch-Kopie, keine Aktion nötig.

## Common Pitfalls

### Pitfall 1: Das Bild-/Seitenmaß der Pipeline weicht vom Bild ab
**What goes wrong:** Die Markierung sitzt an der falschen Stelle, ohne dass etwas fehlschlägt.
**Why it happens:** Mischformat (378 Hochformat-, 22 Querformatseiten), `/Rotate`, gerundete Maße.
**How to avoid:** `seiten[n].breite/hoehe` aus pdfplumber **und** pypdfium2 vergleichen (Test: gleich bis 0,01 pt), WebP-Maße = `round(2 × Punkt)` ± 1 px, Prozentumrechnung als reine Funktion mit Test (Hoch- und Querformat).
**Warning signs:** Markierung verschoben bei Querformat (S. 284 ff., 291 ff., 311).

### Pitfall 2: WebP-Bytes sind nicht plattformstabil belegt
**What goes wrong:** CI-Schritt „Pipeline reproduzierbar“ meldet Diffs an den Bildern, obwohl nichts geändert wurde.
**Why it happens:** Zwei Läufe auf derselben Maschine liefern gleiche Bytes (verifiziert), aber PDFium-Binärrad und libwebp unterscheiden sich je Plattform (hier `aarch64-linux`, in der CI x86_64; Entwickler-Mac). Identität über Plattformen hinweg ist nicht geprüft [ASSUMED].
**How to avoid:** Schritt 08 rendert nur fehlende Bilder (Flag zum Neurendern); die CI-Diff-Prüfung gilt `daten`, `app/src/data` (enthält `quellen.json`), aber nicht den WebP-Bytes. Ein pytest prüft stattdessen: jedes in `quellen.json` genannte Bild existiert, hat die erwarteten Maße (Pillow öffnet es) und es gibt keine verwaisten Bilder.
**Warning signs:** `git status` zeigt `app/public/quellen/*.webp` geändert nach `alle.py`.

### Pitfall 3: Mehrdeutige Zeilensuche trifft die falsche Zeile
**What goes wrong:** Beschriftung kommt mehrfach auf der Seite vor (Konto bei mehreren Maßnahmen, „Summe“, gleiche Grundzahl-Bezeichnung in zwei Produkten auf einer Seite).
**How to avoid:** Betrags-Gegenprobe (Pattern 2), Reihenfolge `position` als Tiebreaker, Abschnittsgrenzen der Pläne verwenden, bei Mehrdeutigkeit `null` plus Bericht statt Raten.
**Warning signs:** Zwei Schlüssel mit identischer `bbox`; Test „keine zwei Belege einer Seite teilen dieselbe bbox, außer sie sind absichtlich gleich“.

### Pitfall 4: Die App lädt `quellen.json` im Bundle
**What goes wrong:** Das Bundle wächst (heute 1,75 MB JS, davon `haushalt.json` ≈ 0,7 MB).
**Einschätzung:** ca. 1000 Einträge à ~100 Byte ≈ 100–200 KB [ASSUMED, Schätzung]. Vertretbar; bei deutlich mehr: Index (nur Schlüssel) im Bundle, Details lazy. Die Regel „Knopf nur bei vorhandenem Schlüssel“ braucht den Schlüsselsatz synchron.
**Warning signs:** `vite build` meldet Chunk > 500 kB (tut er schon; kein neuer Fehler).

### Pitfall 5: Deploy-Job läuft auf Branches und Pull Requests
**What goes wrong:** Die CI läuft bei jedem `push` und `pull_request`; ein Deploy-Job ohne Bedingung scheitert an der `github-pages`-Umgebungsregel oder deployt unfertige Stände.
**How to avoid:** `if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'` am Deploy-Job und am Upload-Schritt; `pages: write` und `id-token: write` nur im Deploy-Job; `concurrency: pages` mit `cancel-in-progress: false`.
**Warning signs:** Deploy-Job erscheint in PR-Checks.

### Pitfall 6: Du/Sie-Heuristik hat viele Falschmeldungen
**What goes wrong:** „Sie stehen im Finanzplan.“ (3. Person Plural, `daten/manuell/texte/glossar.md:33`) und „Ihre Höhe richtet sich nach einem Hebesatz, …“ (`glossar.md:73`, Possessiv für die Kreisumlage) sind korrekt, würden aber von einem naiven `\bSie\b` gemeldet.
**Messung Ist:** Im Bestand gibt es ≈ 12 Treffer von `Sie|Ihnen|Ihr(e|em|en|er|es)?` in `app/src` und `daten/manuell/texte`, **alle satzinitial oder in Kommentaren**, keiner ist eine echte Höflichkeitsform. [VERIFIED: grep dieser Sitzung]
**How to avoid (Empfehlung):** (a) Treffer **innerhalb** eines Satzes (davor Kleinbuchstabe, Komma oder Wort) sind immer ein Fehler; (b) Treffer am Satzanfang sind nur zulässig, wenn die Stelle in einer **geschlossenen Ausnahmeliste** steht (Datei + Satzanfang, 40 Zeichen, mit Begründung „3. Person“); eine neue, unlistete Stelle lässt den Test scheitern und geht in den Text-Checkpoint; (c) Kommentare in `.ts`/`.vue` nicht prüfen (nur Templates, `aria-label`, `title`, `alt`, `texte.json`); (d) zusätzlich ein Positivtest auf typische Höflichkeitsverben nach satzinitialem „Sie“ (`können|müssen|sollten|möchten|finden|sehen`).
**Warning signs:** Ausnahmeliste wächst ohne Begründung.

### Pitfall 7: Konsolenwarnungen aus Web Awesome
**What goes wrong:** „Keine Konsolenfehler“ (QUAL-02) wird durch `console.warn` der Deprecation gestört, falls der Test auch Warnungen zählt.
**Messung:** `[wa-tag] size="small" is deprecated. Use size="s" instead` und `[wa-button] size="large" is deprecated. Use size="l" instead` erscheinen auf allen Routen mit diesen Komponenten. Fundstellen: `size="small"` in `BerechnetEtikett.vue`, `WertartEtikett.vue`, `AusgabenPage.vue` (2×), `EinnahmenPage.vue`, `ProduktPage.vue`; `size="large"` in `EinstiegsKachel.vue`. `s`/`l` sind laut `tag.d.ts` und `button.d.ts` gültig (`'xs' | 's' | 'm' | 'l' | 'xl' | 'small' | 'medium' | 'large'`). [VERIFIED: Lauf + `grep`]
**How to avoid:** Die Werte ändern (eine Zeile je Stelle), dann `error` **und** `warning` im Smoke-Test zählen. Kein Ausfiltern.

### Pitfall 8: `e2e/`-Typprüfung scheitert an fehlender DOM-Bibliothek
**What goes wrong:** `page.evaluate(() => document…)` bricht `vue-tsc --build` mit `TS2584: Cannot find name 'document'`, wenn `e2e/**` nur in `tsconfig.node.json` (ohne `dom`) liegt.
**How to avoid:** Eigene `tsconfig.e2e.json` mit `"extends": "./tsconfig.node.json"`, `"include": ["playwright.config.*", "e2e/**/*"]`, `"compilerOptions": { "lib": ["ES2024", "DOM"], "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.e2e.tsbuildinfo" }` und Eintrag in den `references` von `tsconfig.json`. Geprüft: `npm run type-check` grün, `eslint e2e playwright.config.ts` greift (meldete in der Probe eine ungenutzte Variable). `tsconfig.node.json` führt `playwright.config.*` schon in `include`. Prettier prüft nur `src/` (`prettier --check src/`). `.gitignore` um `playwright-report/`, `test-results/`, `blob-report/` ergänzen.

### Pitfall 9: Playwright-Browser-Download im Sandbox blockiert
**What goes wrong:** `npx playwright install` scheitert an der Firewall.
**Befund:** `curl https://cdn.playwright.dev/` → „Approval required for cdn.playwright.dev:443.“ (erwartet `sbx policy approval …`); `https://storage.googleapis.com/chrome-for-testing-public/` → `AccessDenied`; `https://playwright.download.prss.microsoft.com/` → 403. **Erreichbar:** `mcr.microsoft.com`, npm-Registry, PyPI, `archive.ubuntu.com`.
**How to avoid:** Docker-Image verwenden (Rezept unten). Nicht versuchen, Browser per apt/snap zu installieren.

### Pitfall 10: Ältere Sandbox-Verifikationen verwechseln Host- und Container-Architektur
**What goes wrong:** `node_modules` aus macOS im Repo-Verzeichnis (Binaries) funktioniert im Container nicht.
**How to avoid:** Scratch-Kopie (`tar --exclude=app/node_modules --exclude=app/dist … | tar -xf - -C "$S"`, `npm ci` im Sandbox = linux/arm64, Container ebenfalls arm64) und dann den Container auf `$S/app` mounten. Auf GitHub (amd64) läuft `npm ci` ohnehin frisch.

### Pitfall 11: Impressum, Hosting und Rechtliches
**What goes wrong:** Impressumsfelder bleiben Platzhalter, oder der Datenschutztext ist unvollständig.
**How to avoid:** Platzhalter in `config.ts` so setzen, dass `istPlatzhalter` sie erkennt und der Smoke-Test sowie `config.test.ts` scheitern; inhaltliche Abnahme im Text-Checkpoint. Ob GitHub Pages die IP-Adresse verarbeitet und ob ein Satz dazu nötig ist, ist eine Rechtsfrage und liegt beim Nutzer (nicht Teil dieser Recherche). [ASSUMED] Hinweis: Impressum-/Anbieterkennzeichnungspflichten (Digitale-Dienste-Gesetz, MStV) können je nach Einordnung als privates Angebot variieren; keine Rechtsberatung.

## Code Examples

### Lighthouse-Lauf je Route im Sandbox (verifiziert)
```bash
# Einmalig: Scratch-Kopie, Build, Lighthouse in ein Verzeichnis außerhalb von package.json installieren
S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app | tar -xf - -C "$S"
npm --prefix "$S/app" ci --no-audit --no-fund && npm --prefix "$S/app" run build-only
mkdir -p "$S/lh" && (cd "$S/lh" && npm init -y >/dev/null && npm i lighthouse@13.5.0 --no-audit --no-fund)

# Skript im Container: Preview starten, Chromium des Playwright-Images nutzen
cat > "$S/lh/run.sh" <<'EOS'
cd /work/app
npx vite preview --port 4173 --strictPort >/tmp/preview.log 2>&1 &
sleep 3
export CHROME_PATH=$(ls -d /ms-playwright/chromium-*/chrome-linux*/chrome | head -1)
for r in '' einnahmen ausgaben produkt/020701 geldfluss entwicklung investitionen rat-entscheidet stellenplan glossar ueber; do
  node /work/lh/node_modules/lighthouse/cli/index.js "http://localhost:4173/#/$r" \
    --only-categories=accessibility --chrome-flags="--headless=new --no-sandbox" \
    --output=json --output-path=/tmp/lh.json --quiet 2>/tmp/lh.err || { echo "FAIL $r"; continue; }
  node -e "const j=require('/tmp/lh.json');const bad=Object.values(j.audits).filter(x=>x.scoreDisplayMode==='binary'&&x.score===0).map(x=>x.id);console.log('$r'||'/',Math.round(j.categories.accessibility.score*100),bad.join(','))"
done
EOS
docker run --rm --ipc=host -v "$S":/work mcr.microsoft.com/playwright:v1.63.0-noble bash /work/lh/run.sh
```
Ergebnis dieser Sitzung (Stand vor Phase 7, ohne `/ueber`): `/` 100, `/einnahmen` 100, `/ausgaben` 100, `produkt/010101` 100, `/geldfluss` 100, `/entwicklung` 100, `/investitionen` 100, `/rat-entscheidet` 100, `/stellenplan` 100, **`/glossar` 98 (`heading-order`)**. [VERIFIED: Lauf dieser Sitzung] Ursache `heading-order`: `GlossarListe.vue` setzt `h3` je Begriff direkt unter der `h1` (`<h3 tabindex="-1">{{ eintrag.begriff }}</h3>`), die `h2` „Alle Produkte“ kommt erst danach in `GlossarPage.vue`. Behebung: eine `h2` „Begriffe“ (Heading-Rolle) vor die Begriffsliste. Das passt zu D-17/D-18 (Spec-Rolle der `h3`).

### Playwright im Sandbox (verifiziert)
```bash
S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app | tar -xf - -C "$S"
npm --prefix "$S/app" ci --no-audit --no-fund && npm --prefix "$S/app" run build-only
docker run --rm --ipc=host -v "$S/app":/work -w /work \
  mcr.microsoft.com/playwright:v1.63.0-noble npx playwright test
```
Das Image bringt Node 24 mit; `npx playwright test` nutzt das gemountete `node_modules` (`@playwright/test` 1.63.0 muss zur Image-Version `v1.63.0` passen). `webServer.command` startet `vite preview` im Container.

### Inventar je `ChartCard` (Laufzeit-DOM, Probe lieferte den Ist-Befund)
```ts
// Quelle: Probe dieser Sitzung (e2e/inventar.spec.ts im Scratch)
const m = await page.evaluate(() => {
  const luecken = [...document.querySelectorAll('.om-base-chart')]
    .filter((c) => { const k = c.closest('.om-chart-card'); return !k || !k.querySelector('table') })
    .map((c) => c.closest('section')?.querySelector('h2')?.textContent ?? 'OHNE KARTE')
  return { luecken }
})
```
**Ist-Befund:** Auf `/entwicklung` liegen zwei Diagramme („Rücklagen 2024–2029“, „Rückgang der allgemeinen Rücklage“) in einer `.om-chart-card` **ohne** `table` darin. UI-SPEC nennt „kurze Rücklagentabelle auf `/entwicklung`“ als Ausnahme (immer sichtbar); ob die Tabelle außerhalb der Karte steht, prüft der Executor. Die Probe prüft nur „irgendeine Tabelle in der Karte“; Karten mit zwei Diagrammen (`/rat-entscheidet`: 4 Diagramme in 3 Karten, `/stellenplan`: 6 in 3) brauchen laut UI-SPEC zwei Tabellen oder eine gemeinsame Tabelle, das muss der echte Inventar-Test zählen (Diagramme je Karte gegen Tabellen je Karte).

### Typografie-Wächter für alle Dateien (D-17), Skelett
```ts
// Erweiterung von app/src/lib/__tests__/stiltokens.test.ts: nur <style>-Blöcke und .css lesen
// Erlaubt (Größe): --wa-font-size-s | -m | -l | -2xl ; (Gewicht): --wa-font-weight-normal | -bold
// Verboten: Literale (px/rem/600), --wa-font-size-xl, --wa-font-weight-semibold, --wa-font-weight-body,
//           Spacing --wa-space-3xs | -2xl | -5xl; .ts-Dateien (echartsTheme.ts) bleiben außen vor
```
Heutiger Wächter: `VERBOTENE_TYPOGRAFIE_TOKENS` kennt nur `--wa-font-size-xl` und `--wa-font-weight-semibold` und gilt für sechs benannte Phase-6-Dateien (`PHASE_6_TYPOGRAFIE_DATEIEN`). Zuordnung der Bereinigung: siehe UI-SPEC-Tabelle „Token-Hygiene“.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `actions/deploy-pages@v4`, `upload-pages-artifact@v4` | v5.0.1 bzw. v5.0.0 (Node-24-Runtime) | v5.0.0 am 25. März (laut Release-Seite) | Hosted Runner genügen; SHA pinnen |
| `playwright install` über CDN im Sandbox | offizielles Docker-Image `mcr.microsoft.com/playwright:vX.Y.Z-noble` | — | Einziger Weg hier ohne Firewallfreigabe |
| Unabhängiges `puppeteer`/`chrome-launcher` für Lighthouse | Lighthouse 13.x mit `CHROME_PATH` auf das Playwright-Chromium | — | Verifiziert im Lauf |
| WA-Größen `small`/`large` | `s`/`l`/… | WA 3.x (Deprecation-Warnung in 3.14) | Zeilenweise Änderung, sonst Konsolenwarnung |

**Deprecated/outdated:** `wa-tag size="small"`, `wa-button size="large"` (in WA 3.14 gewarnt, „will be removed in the next major version“).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | WebP-Bytes sind über macOS/Linux und x86/arm identisch (nur derselbe Host getestet) | Pitfall 2, Alternatives | Gering: Empfehlung („nur fehlende Bilder rendern“) umgeht die Annahme; bei Identität darf der Diff später dazukommen |
| A2 | `#page=N` am PDF-Link funktioniert in den gängigen Browsern und der Gemeindeserver bricht ihn nicht ab (`www.ostbevern.de` ist aus dem Sandbox mit 403 nicht prüfbar) | Pattern 7/Open Questions (D-06) | Gering: schlimmstenfalls öffnet die Datei vorn |
| A3 | Die Pages-Umgebung `github-pages` erlaubt standardmäßig nur den Standardbranch zum Deployen | Pitfall 5 | Gering: `if`-Bedingung gilt ohnehin |
| A4 | GitHub Pages braucht bei GitHub Free ein öffentliches Repo; die Doku verweist nur auf „wenn Plan oder Organisation es erlauben“ | Open Questions | Mittel: Org `bitwerkstatt` muss Pages zulassen, sonst kein DEPL-02 |
| A5 | `npx playwright install --with-deps chromium` läuft auf `ubuntu-latest` wie dokumentiert (nicht im Sandbox ausführbar) | Pattern 6 | Gering; Standardweg, in D-11 so festgelegt |
| A6 | Lighthouse-Werte mit dem Playwright-Chromium entsprechen dem lokalen Chrome des Nutzers bis auf Rauschen | Code Examples | Gering: Ziel ≥ 95, Ist 98–100 |
| A7 | Größe von `quellen.json` ≈ 100–200 KB | Pitfall 4 | Gering |
| A8 | Rechtliche Einordnung des Impressums/Datenschutzes (Pflichten, GitHub-IP-Verarbeitung) | Pitfall 11 | Mittel, aber Sache des Nutzers im Text-Checkpoint |
| A9 | Weitergabe der gerenderten Seiten des Gemeinde-PDFs ist zulässig (Nutzer hat in D-06 entschieden, Urheberrecht ungeprüft) | Open Questions | Mittel: Kurzer Hinweis im Text-Checkpoint |

## Open Questions

1. **Fokus beim Öffnen: Dialog oder Schließen-Knopf?**
   - What we know: UI-SPEC fordert den Schließen-Knopf; WA 3.14 fokussiert das `<dialog>` (Quelltext gelesen).
   - What's unclear: ob der Nutzer den abweichenden Vertrag akzeptiert.
   - Recommendation: Vertrag auf „Fokus im benannten Dialog, erster Tab-Stopp Schließen-Knopf“ anpassen, im Playwright-Spec prüfen. Kein Override per Hack.

2. **D-19/D-12: Wo laufen DOM-Tests (MenueGruppe, Quelle-Fokus, 360 px)?**
   - What we know: vitest = Node, kein DOM; `jsdom`/`@vue/test-utils` sind nicht freigegeben; Playwright ist freigegeben und läuft hier über Docker.
   - What's unclear: ob eine zweite Spec-Datei (`interaktion.spec.ts`, `mobil.spec.ts`) neben dem Smoke-Test mit D-12 vereinbar ist (D-12 verbietet nur, diese Prüfungen **im Smoke-Test** auszuführen).
   - Recommendation: Eigene Spec-Dateien, in der CI nur `smoke.spec.ts` plus `interaktion.spec.ts` (schnell), `mobil.spec.ts` nur für die Verifikation (360 px ist im Deferred als CI-Smoke zurückgestellt). Messbasis: heute `scrollWidth == 360` auf allen 10 Routen.

3. **Konsolenwarnungen im Smoke-Test zählen?**
   - Recommendation: Ja, nach Behebung der `size`-Attribute (Pitfall 7).

4. **Lighthouse als Paket freigeben?**
   - D-13 nennt `npx lighthouse`, D-14 listet es nicht. Recommendation: kurzer `checkpoint:human-verify` vor dem ersten Lauf, Version 13.5.0 festschreiben.

5. **D-20: Welche Review-Punkte sind noch offen?**
   - What we know: `02-REVIEW-DISPOSITION.md` führt WR-01 und WR-02 als `fixed`, offen sind WR-03, IN-01, IN-02; `04-REVIEW-DISPOSITION.md` führt WR-04/WR-05/IN-02 als `open` und WR-01…WR-03/IN-01 ebenfalls `open` (WR-06 wurde laut STATE.md in 05-01 behoben, steht dort aber noch `open`). CONTEXT spricht von „3 Warnungen“ (02) und „WR-01…WR-05, IN-02“ (04).
   - Recommendation: Planer liest `02-REVIEW.md`, `04-REVIEW.md` und beide Dispositionen neu und legt die Triage-Liste fest; Dispositionsdateien am Ende aktualisieren. `befunde.md`-Vorzeichenbeschreibung (WR-02 der Phase 2) und PB-09/15-Kommentar mit S. 296/299 sind reine Text-/Kommentaränderungen. Jeder Diff auf `daten/` ist ein Befund für den Nutzer.

6. **Bildvolumen im Repo (18,5 MB, einmalig, danach stabil)**
   - Recommendation: akzeptieren; Q60/2 px laut Spez. 5.6 ist gesetzt. Seiten laden erst beim Öffnen (je 20–180 KB). Kein Git-LFS.

7. **Bildanzahl 231 statt 188**
   - 188 ist die Zahl der verschiedenen Werte der vier `pdf_seite`-Felder (D-01); mit `pdf_seiten`, `quelle`, `quelle_seiten` und `texte.json` kommen es auf 231 (Haushalt 108, Investitionen 43, Produkte 62, Stellenplan 7, Texte 11 verschiedene Seiten, jeweils zusätzlich zu den vorherigen). Der Planer rendert die Vereinigung aller Seitenfelder (Test über alle JSONs), nicht nur die 188.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Node.js | App-Checks, Playwright-Specs | ✓ | v22.22.1 (`app/.nvmrc`: 22) | — |
| npm Registry | `npm ci`, `npm view` | ✓ | — | — |
| uv | Pipeline-Checks | ✓ | 0.9.26 (CI pin identisch) | — |
| Python (venv) | Pipeline, Schritt 08 | ✓ | 3.12 (`pipeline/.python-version`) | — |
| `pypdfium2`, `Pillow`, `pdfplumber` | Rendern, Zeilensuche | ✓ | 5.13.0 / 12.3.0 / 0.11.10 (in `pipeline/.venv`) | — |
| Docker | Playwright-/Lighthouse-Läufe im Sandbox | ✓ | 29.8.1 | — |
| Playwright-Image `mcr.microsoft.com/playwright:v1.63.0-noble` | Playwright, Chromium für Lighthouse | ✓ | gezogen, arm64 | — |
| Playwright-Browser über CDN | native `npx playwright install` | ✗ | `cdn.playwright.dev`: „Approval required“, GCS 403 | Docker-Image; alternativ Nutzer gibt die Domain frei (`sbx policy allow network cdn.playwright.dev`) |
| Lighthouse (`npx`/npm) | A11Y-04 | ✓ | 13.5.0 installierbar (Node ≥ 22.19) | — |
| Chromium/Chrome nativ im Sandbox | — | ✗ | — | Docker-Image |
| `gh` CLI | optional | ✓ | 2.46.0 (im Sandbox nicht angemeldet, Remote fehlt) | — |
| GitHub-Remote | CI-Lauf, DEPL-02 | ✗ | `git remote -v` leer | Nutzer legt Repo an (D-10); CI-Verifikation bleibt lokal nachgestellt |
| `bitwerkstatt.github.io`, `www.ostbevern.de` | DEPL-02, PDF-Link | ✗ aus dem Sandbox | HTTP 403 | Menschlicher Checkpoint nach dem Push (D-10) |

**Missing dependencies with no fallback:** GitHub-Remote und öffentliche URL (D-10: Nutzer erledigt; kein Blocker für die Implementierung).
**Missing dependencies with fallback:** native Playwright-Browser (Docker-Image), nativer Chrome (Docker-Image).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | App: vitest 5.0.3 (`environment: 'node'`, `include: ['src/**/__tests__/*.test.ts']`); Pipeline: pytest 9.x; neu: Playwright 1.63.0 (`e2e/*.spec.ts`) |
| Config file | `app/vitest.config.ts`; `pipeline/pyproject.toml`; neu `app/playwright.config.ts`, `app/tsconfig.e2e.json` |
| Quick run command | Pipeline: `uv run --directory pipeline pytest tests/test_quellen.py -x -q`; App-vitest: `S=$(mktemp -d) && tar --exclude=app/node_modules --exclude=app/dist -cf - app \| tar -xf - -C "$S" && npm --prefix "$S/app" ci --no-audit --no-fund && npm --prefix "$S/app" run test -- src/lib/__tests__/quelle.test.ts` |
| Full suite command | Pipeline: `uv run --directory pipeline pytest -q` plus `uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data` (keine untracked Dateien); App: `npm ci`, `type-check`, `lint`, `format:check`, `test`, `build` in der Scratch-Kopie; E2E: Docker-Befehl aus „Code Examples“ |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DATA-04 | Schritt 08: jede Zeile eines Probesatzes (z. B. S. 62 Z. 01 `steuern`, ein Grundzahlwert, ein Konto) liefert eine bbox, die das gedruckte Wort enthält; Seitenmaße pdfplumber = pypdfium2; Bildmaße = 2 × Punkt ± 1 px; keine verwaisten Bilder; `null`-Bericht entsteht | pytest (echtes PDF) | `uv run --directory pipeline pytest tests/test_quellen.py -x -q` | ❌ Wave 0 |
| DATA-04 | Abdeckung: jeder `pdf_seite`/`quelle`/`pdf_seiten`-Wert der App-JSONs hat mindestens einen Beleg (`seite:{n}` Rückfall) | pytest (JSON-Walk) | `uv run --directory pipeline pytest tests/test_quellen.py -k abdeckung -q` | ❌ Wave 0 |
| DATA-04 | `alle.py` erzeugt keinen Diff an `daten` und `app/src/data` (inkl. `quellen.json`, Bericht) | CI-Schritt | `uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data` | ✅ Schritt vorhanden, Schritt 08 anhängen |
| UI-02 | `lib/quelle.ts`: Schlüsselableitung = Pipeline-Schlüssel für alle JSON-Datensätze; Prozentumrechnung der bbox (Hoch-/Querformat); Knopf nur bei vorhandenem Schlüssel | vitest | `npm --prefix "$S/app" run test -- src/lib/__tests__/quelle.test.ts` | ❌ Wave 0 |
| UI-02 | Leiste öffnet per Klick/Enter/Leertaste, Fokus im Dialog, Esc schließt, Fokus kehrt zum Auslöser zurück, Marker sichtbar, Querformat S. 291/311, ohne Marker: Hinweis | Playwright (`interaktion.spec.ts`) | Docker-Befehl, `npx playwright test e2e/interaktion.spec.ts` | ❌ Wave 0 |
| A11Y-01 | Je `.om-chart-card` mit Diagramm: Anzahl Tabellen ≥ Anzahl Diagramme (oder gemeinsame Tabelle), `beschreibung` vorhanden, geschlossene Ausnahmeliste | Playwright (Laufzeit-DOM) und/oder vitest-Quelltext-Scan | Docker-Befehl, `e2e/inventar.spec.ts` | ❌ Wave 0 |
| A11Y-02 | Fokus auf `h1` nach Menüklick je Route, `document.title` endet auf „– Ostbevern Money“; emulierte reduzierte Bewegung: Drawer/Details öffnen ohne Übergang; Diagramme `animation: false` | Playwright (`page.emulateMedia({ reducedMotion: 'reduce' })`) | Docker-Befehl | ❌ Wave 0 |
| A11Y-03 | `documentElement.scrollWidth <= innerWidth` bei 360×640 auf allen 11 Routen, auch mit offener Leiste und offenem Menü-Drawer; Ziele ≥ 44 px | Playwright (`mobil.spec.ts`, nicht im Smoke-Pfad) | Docker-Befehl, `e2e/mobil.spec.ts` | ❌ Wave 0 (Probe lief grün: 10/10) |
| A11Y-04 | Lighthouse a11y je Route ≥ 95 (Tabelle im Verifikationsbericht) | manuell/Skript | Lighthouse-Rezept (siehe Code Examples) | ❌ Wave 0 (Skript) |
| QUAL-02 | je Route: Überschrift, keine Konsolenfehler/-warnungen, Diagramme mit Daten, kein `.invalid`, axe ohne Verstöße, keine Fremd-Requests | Playwright (`smoke.spec.ts`) | Docker-Befehl bzw. CI `npm run test:e2e` | ❌ Wave 0 |
| UI-06 | Du-Anrede-Test über `texte.json`, `.vue`-Templates, `aria-label`/`title`/`alt` mit geschlossener Ausnahmeliste; Text-Checkpoint | vitest | `npm --prefix "$S/app" run test -- src/lib/__tests__/duanrede.test.ts` | ❌ Wave 0 |
| UI-03/D-07 | `config.test.ts`: `KONTAKT_EMAIL`, `ORIGINAL_PDF_URL` und Impressumsfelder sind keine Platzhalter | vitest | `npm --prefix "$S/app" run test -- src/lib/__tests__/config.test.ts` | ✅ erweitern |
| D-17 | Typografie-Wächter für alle `.vue`/`.css` | vitest | `npm --prefix "$S/app" run test -- src/lib/__tests__/stiltokens.test.ts` | ✅ erweitern |
| D-19 | `MenueGruppe`: Enter/Leertaste, Escape → Fokus am Schalter, Tab verlässt Gruppe schließt, Klick außerhalb, aktiver Eintrag `aria-current`, Drawer mobil | Playwright | Docker-Befehl, `e2e/interaktion.spec.ts` | ❌ Wave 0 |
| Menü | `menue.test.ts`: benannte Ausnahmeliste für Fußzeilenrouten (`ueber`) | vitest | `npm --prefix "$S/app" run test -- src/lib/__tests__/menue.test.ts` | ✅ anpassen |
| E4-Backstop | `BaseChart`/`DatenTabelle`: Skeleton bei `laedt`, Fehlertext bei `fehler`, Leerzustand | Quelltext-/Logiktest (vitest) oder Playwright mit erzwungenem Zustand | siehe Offene Annahme 4 im UI-SPEC | ❌ Wave 0 |
| DEPL-01 | Workflow-Datei: Jobs, SHAs, Berechtigungen, Bedingungen | statischer Test oder Review (YAML-Lint) | `grep` auf `permissions`, `if:` | ❌ Wave 0 |
| DEPL-02 | Öffentliche URL lädt (Icons, Belegbild, Direktaufruf `/#/ausgaben`, `/#/ueber`, Fußzeile, PDF-Link) | menschlicher Checkpoint | — | manuell (D-10) |

### Sampling Rate
- **Per task commit:** gezielte pytest-Datei bzw. gezielte vitest-Datei in der Scratch-Kopie plus `type-check`/`lint`/`format:check`.
- **Per wave merge:** volle Pipeline-Suite (≈ 5,5 min), `alle.py` mit Diff-Prüfung, komplette App-Kette in der Scratch-Kopie, danach Playwright im Docker-Image.
- **Phase gate:** alles grün, Lighthouse-Tabelle aller 11 Routen ≥ 95, Du-Test grün und Texte abgenommen, 360-px-Liste, vor `/gsd-verify-work`.

### Wave 0 Gaps
- [ ] `pipeline/tests/test_quellen.py` — DATA-04 (Suche, Maße, Abdeckung, Bericht)
- [ ] `app/src/lib/__tests__/quelle.test.ts` — Schlüssel, Prozentumrechnung, Abdeckung (JSON → quellen.json)
- [ ] `app/src/lib/__tests__/duanrede.test.ts` — UI-06
- [ ] `app/e2e/smoke.spec.ts`, `app/e2e/interaktion.spec.ts`, `app/e2e/mobil.spec.ts`, `app/e2e/inventar.spec.ts`, `app/playwright.config.ts`, `app/tsconfig.e2e.json`
- [ ] `npm install -D @playwright/test@1.63.0 @axe-core/playwright@4.13.0` und Skript `"test:e2e": "playwright test"` in `app/package.json`
- [ ] `.gitignore`: `playwright-report/`, `test-results/`, `blob-report/`
- [ ] Lighthouse-Rezept als Skript (nicht in `package.json`), z. B. unter `.planning/phases/07-…/` oder `scripts/`

## Security Domain

`security_enforcement` ist in `.planning/config.json` aktiv (`security_asvs_level: 1`, `security_block_on: high`).

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Statische Seite, kein Login |
| V3 Session Management | no | Keine Sitzungen, keine Cookies (Datenschutzaussage wird per Smoke-Test technisch gestützt) |
| V4 Access Control | no | Kein Backend; Deployment-Rechte siehe V14 |
| V5 Input Validation / Output Encoding | yes | Kein `v-html`; Impressum/Texte aus Code bzw. `config.ts`; `bbox`-Zahlen als `number` typisiert; Belegschlüssel nur aus festen Mustern; Links `rel="noopener noreferrer"` |
| V6 Cryptography | no | Kein eigenes Krypto; `id-token` nutzt GitHub-OIDC |
| V10/V14 Build & Deploy / Konfiguration | yes | SHA-gepinnte Actions, Least-Privilege-`permissions`, Deploy nur von `main`, `concurrency`, keine Secrets |

### Known Threat Patterns for diesen Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Supply-Chain (neue npm-/PyPI-Pakete, `npx lighthouse`) | Tampering | Nur freigegebene Pakete (D-14), `package-lock.json`/`uv.lock` commiten, Lighthouse-Version fest, kein Postinstall (geprüft) |
| Workflow-Rechte zu weit (Pages-Schreibrecht im PR) | Elevation of Privilege | `pages: write`/`id-token: write` nur im Deploy-Job, Bedingung gegen `pull_request`, Forks deployen nie |
| Unpinned Actions | Tampering | Vollständige Commit-SHAs mit Versionskommentar (wie `ci.yml`) |
| Fremde Requests/Tracker | Information Disclosure | Smoke-Test bricht bei Requests an fremde Hosts ab; Icons und Belegbilder selbst gehostet; Ist: 0 Fremd-Requests auf allen Routen |
| XSS über Textfelder | Tampering | Interpolation statt `v-html` (Quelltext-Scan existiert); Impressum aus `config.ts` |
| Offene Weiterleitung/Tabnabbing | Spoofing | `target="_blank" rel="noopener noreferrer"` für externe Links; `#page=` hängt nur an die feste `ORIGINAL_PDF_URL` |
| Personenbezogene Daten im Datensatz | Information Disclosure | Mitarbeitendennamen werden nicht ausgeliefert (Phase 3/4); Belegbilder zeigen **ganze PDF-Seiten**, daher prüfen, ob eine referenzierte Seite Personennamen enthält (insbesondere Stellenplan S. 284–290, Zuwendungen an Fraktionen S. 307/308) und das im Text-Checkpoint dokumentieren — **neues Risiko dieser Phase** |
| Optional: Content-Security-Policy | Tampering | GitHub Pages setzt keine Header; ein `<meta http-equiv="Content-Security-Policy">` wäre möglich, aber nicht verifiziert [ASSUMED]; nicht Teil der Pflichtanforderungen |

Hinweis zu Personennamen: Phase 3/4 hat Mitarbeitendennamen aus `produkte.json` ferngehalten (CLAUDE.md: „Mitarbeitendennamen werden extrahiert, aber nicht ausgeliefert“). Die Quellenleiste liefert nun ganze Seitenabbilder aus; wenn eine referenzierte Seite Namen im Klartext zeigt, widerspricht das dieser Constraint. Planer fügt eine Prüfaufgabe hinzu (Seiten mit bekannten Namen prüfen; falls nötig Seite aus dem Beleg-Satz nehmen und `bbox: null` ohne Bild oder Schwärzung klären). [ASSUMED: ob solche Namen auf den referenzierten Seiten stehen, wurde in dieser Sitzung nicht geprüft]

## Project Constraints (from CLAUDE.md)

Aus `/Users/thma/repos/bitwerkstatt/ostbevern_money/.claude/CLAUDE.md` (Projekt) und `/Users/thma/repos/bitwerkstatt/CLAUDE.md` (Sandbox):
- **Tech stack Pipeline:** Python ≥ 3.12, uv, pdfplumber, polars, typer, pytest, ruff. Befehle immer mit `uv run --directory pipeline …` vom Repo-Root.
- **Tech stack App:** Vue 3, TypeScript, Vite, Web Awesome (einzeln in `app/src/main.ts` importiert, Icons selbst gehostet unter `app/public/icons`), ECharts nur über registrierte Module in `echartsTheme.ts`, Hash-Router, Node 22.
- **Genauigkeit:** Abweichungen über 1 € gelten als Fehler; die Daten-JSONs und CSVs dürfen sich durch Phase 7 nicht ändern (D-20).
- **Datenschutz:** Mitarbeitendennamen nicht ausliefern (siehe Sicherheitsbefund zu ganzen Seitenbildern).
- **Sprache:** Deutsch, durchgehend Du-Anrede. Deutsche Bezeichner ohne Umlaute in Code und Daten.
- **Beträge** als int-Euro, Formatierung nur über `app/src/charts/format.ts`; **nur 1-basierte PDF-Seiten** (`pdf_seite`).
- **Keine Jahrgangswerte im Code:** Haushaltsjahr, PDF-Pfad, Seitenbereiche usw. nur über `ostbevern.konfiguration.lade_jahrgang`/`lade_sollwerte`; `STANDARD_JAHR` an genau einer Stelle; jedes Pipeline-Skript nimmt `--jahr`.
- **Pipeline-Skripte** sind dünne typer-Einstiegspunkte, Logik in `pipeline/ostbevern/`; generierte Daten unter `daten/` werden eingecheckt.
- **Basiskomponenten** behalten Namen und Props (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `format.ts`, `echartsTheme.ts`, `bildschirm.ts`).
- **Farben** ausschließlich über `--wa-*`-Tokens, Chartfarben aus `echartsTheme.ts`; CSS-Klassen mit Präfix `om-`; Beispielwerte nur hinter dem `ChartCard`-Flag `beispieldaten`.
- **Keine Drittanbieter-Requests zur Laufzeit.**
- **Beim Commit nur explizit benannte Pfade stagen.**
- **GSD-Workflow:** Dateiänderungen nur innerhalb eines GSD-Workflows.
- **CI lokal nachstellen:** `(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)` und `(cd app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run test && npm run build)`; im Sandbox die App-Kette in einer Scratch-Kopie (macOS-Binaries in `app/node_modules`).
- **Sandbox:** `/etc/sandbox-persistent.sh` nie mit Shell-Completions füllen; für Werkzeuge im PATH `bash -l -c "…"` nutzen.

## Sources

### Primary (HIGH confidence)
- Installierter Quelltext `app/node_modules/@awesome.me/webawesome@3.14.0/dist` (Drawer `chunk.2UZFSBAI.js`, `chunk.L6CIKOFQ.js`, `drawer.d.ts`, `tag.d.ts`, `button.d.ts`) — Fokus, Fokusrückgabe, Animation, Reduced-Motion-Lage
- Läufe dieser Sitzung: `pipeline/.venv` (pypdfium2 5.13.0, Pillow 12.3.0, pdfplumber 0.11.10) gegen `raw_data/haushalt-2026.pdf`; Playwright 1.63.0 und Lighthouse 13.5.0 im Docker-Image `mcr.microsoft.com/playwright:v1.63.0-noble` gegen `vite preview`
- `git ls-remote` für `actions/upload-pages-artifact`, `actions/deploy-pages`, `actions/configure-pages`, `actions/checkout`, `actions/setup-node`, `actions/upload-artifact`
- Projektdateien: `07-CONTEXT.md`, `07-UI-SPEC.md`, `REQUIREMENTS.md`, `STATE.md`, `.github/workflows/ci.yml`, `app/package.json`, `app/vite.config.ts`, `app/vitest.config.ts`, `app/src/config.ts`, `app/src/lib/menue.ts`, `app/src/router/index.ts`, `app/src/components/BaseChart.vue`, `pipeline/ostbevern/pdf.py`, `pipeline/pyproject.toml`, `pipeline/uv.lock`, `daten/aufbereitet/*.csv`, `daten/manuell/*.csv`

### Secondary (MEDIUM confidence)
- github.com/actions/deploy-pages (Berechtigungen, Inputs, Beispiel-Workflow; Release-Hinweis zu Node 24) — [CITED: https://github.com/actions/deploy-pages]
- github.com/actions/upload-pages-artifact (Inputs, Artefaktformat) — [CITED: https://github.com/actions/upload-pages-artifact]
- docs.github.com Pages-Publishing-Source (Quelle „GitHub Actions“, Deploy für PRs übersprungen, Plan/Sichtbarkeit nur allgemein) — [CITED: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site]
- Münster-Vorbild (`codeformuenster/haushalt-muenster-2026`): Pipeline-Skripte `quellen_zuschuesse.py`/`quellen_planspiel.py` unter `scripts/pipeline/`, Schema `{pdf, band, seiten{n:{bild}}, posten{nr:{seite, box, csv, zeile, zellen}}}` — nur als Orientierung; die Hilfsfunktionen (`pdf_box`, `rendere_seite`) liegen in einer nicht abgerufenen `quellen.py`

### Tertiary (LOW confidence)
- Keine tragenden LOW-Quellen; offene Annahmen siehe Assumptions Log.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Versionen per Registry geprüft, Pakete durch D-13/D-14 gesetzt, Lauf im Sandbox.
- Architecture: HIGH für Pipeline-Schritt und Koordinaten (Overlay verifiziert), MEDIUM für die konkrete Schlüsselgrammatik (Vorschlag, Planer entscheidet) und den `null`-Anteil.
- Pitfalls: HIGH — Mehrzahl durch Messung oder Quelltext belegt; Cross-Plattform-WebP und Rechtsfragen als `[ASSUMED]` markiert.

**Research date:** 2026-10-06
**Valid until:** 2026-11-05 (Playwright/Lighthouse/Actions bewegen sich schnell; bei neuer Playwright-Version Image-Tag und `package.json` gemeinsam anheben)
