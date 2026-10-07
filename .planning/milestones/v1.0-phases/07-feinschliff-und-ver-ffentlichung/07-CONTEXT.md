# Phase 7: Feinschliff und Veröffentlichung - Context

**Gathered:** 2026-10-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Die App wird belegbar, barrierefrei, mobil nutzbar, geprüft und öffentlich erreichbar:

- **Quellenbelege (DATA-04, UI-02):** Pipeline-Schritt `08_quellenbelege.py` erzeugt `quellen.json` und WebP-Seiten unter `app/public/quellen/`. Die App öffnet an Kennzahlen und Tabellenzeilen über „Quelle anzeigen“ eine Seitenleiste mit markierter Zeile.
- **Barrierefreiheit (A11Y-01…04):** Tabellenalternative zu jedem Diagramm, Fokus beim Routenwechsel, Kontraste, `prefers-reduced-motion`, nutzbar ab 360 px, Lighthouse a11y ≥ 95 auf allen Routen.
- **Qualität (QUAL-02, UI-06):** Playwright-Smoke-Test mit axe-Prüfung in der CI. Ein Textdurchgang stellt Deutsch und Du-Anrede sicher.
- **Veröffentlichung (DEPL-01, DEPL-02):** Deploy-Job in GitHub Actions auf GitHub Pages, öffentliche URL `https://bitwerkstatt.github.io/ostbevern-money/`.
- Dazu kommen: die Seite „Über dieses Projekt“ (Impressum und Datenschutz) und das Abarbeiten der offenen Review-Restpunkte (D-17…D-20).

Nicht enthalten sind neue Inhaltsseiten, Spiele (v2) und weitere Haushaltsjahre.

</domain>

<decisions>
## Implementation Decisions

### Quellenbelege
- **D-01:** **„Quelle anzeigen“ gibt es an jedem Wert mit `pdf_seite`.** Das sind Kennzahlkacheln, alle `DatenTabelle`-Zeilen mit Seitenbezug und die Produktseite. Es gibt einen einzigen Mechanismus für alles, keine Auswahl „prominenter“ Werte. Heute verweisen die App-JSONs auf 188 verschiedene PDF-Seiten.
- **D-02:** **Die Seitenleiste zeigt die ganze PDF-Seite als WebP.** Gerendert wird nach Spez. 5.6 (2 px je PDF-Punkt, Qualität 60), ein Bild je Seite, das mehrere Werte nutzen. Das Zeilenrechteck (`bbox` aus `quellen.json`) wird als Overlay über das Bild gezeichnet, und die Ansicht scrollt zur markierten Zeile. Spaltenköpfe und Planüberschrift bleiben so als Kontext sichtbar. Gerendert werden nur Seiten, die tatsächlich referenziert sind, nicht alle 400.
- **D-03:** **Wird kein Rechteck gefunden, zeigt die Leiste die Seite ohne Markierung mit einem Hinweis.** Das betrifft etwa gerundete Vorberichtswerte in T€ oder berechnete Werte. Der Hinweis lautet sinngemäß „Zeile nicht automatisch markiert“. Bei berechneten Werten (`BerechnetEtikett`) steht dort, woraus sie berechnet sind. Die Pipeline bricht nicht ab, schreibt aber einen Bericht aller Werte ohne `bbox` unter `daten/pruefberichte/`. So wird die Lücke sichtbar und nicht stillschweigend hingenommen.
- **D-04:** **Die Leiste ist ein `wa-drawer` rechts, auf schmalen Bildschirmen vollbreit.** Sie hat eine Fokusfalle, Esc schließt sie, und danach kehrt der Fokus zum auslösenden Knopf zurück. Es gibt keinen URL-Zustand für die Quelle. Grundlage ist das Muster der Münster-Komponente `QuelleSeitenleiste`.

### Veröffentlichung
- **D-05:** **Die App liegt im GitHub-Account bzw. der Organisation `bitwerkstatt`, im Repo `ostbevern-money`.** Die öffentliche URL ist `https://bitwerkstatt.github.io/ostbevern-money/`. Eine eigene Domain gibt es nicht. `base: './'` und der Hash-Router bleiben.
- **D-06:** **`ORIGINAL_PDF_URL`** in `app/src/config.ts` ist die offizielle Gemeinde-Datei: `https://www.ostbevern.de/_Resources/Persistent/3/2/6/0/3260f0ed6ed16745ad93c953c061f765866667a6/Haushalt%202026%20komplett.pdf`. Es wird keine eigene Kopie des PDFs ausgeliefert, nur die gerenderten Belegseiten (D-02). Weil die URL direkt auf die PDF-Datei zeigt, kann ein seitengenauer Link `#page=X` ergänzt werden. Ob, entscheidet der Planer.
- **D-07:** **`KONTAKT_EMAIL` = `mail@thomas-manthey.de`.** Damit ist P5 D-17 erfüllt. Die bestehende `.invalid`-Prüfung (`config.test.ts`, `istPlatzhalter`) bleibt und läuft zusätzlich im Smoke-Test.
- **D-08:** **Es gibt eine neue Seite „Über dieses Projekt“** (Route, verlinkt aus der Fußzeile). Sie enthält Impressum (verantwortliche Person, Kontakt), einen Datenschutzsatz („keine Cookies, kein Tracking, keine Drittanbieter-Requests, Hosting bei GitHub Pages“), den Hinweis „inoffizielles Projekt“ und den Dank an Code for Münster. Name und Anschrift für das Impressum fragt der **Text-Checkpoint (D-15)** ab. Die Texte nimmt der Nutzer dort ab.
- **D-09:** **Deployt wird bei jedem Push auf `main`, aber nur wenn die CI grün ist.** Dazu kommt ein manueller `workflow_dispatch`. Ein eigener Deploy-Job hängt von `pipeline`, `app` und dem Smoke-Test ab und nutzt `actions/upload-pages-artifact` und `actions/deploy-pages`, beide SHA-gepinnt. Die Rechte `pages: write` und `id-token: write` gelten nur für den Deploy-Job. Global bleibt `contents: read`.
- **D-10:** **Das GitHub-Repo legt der Nutzer selbst an** und macht den ersten Push. Der Plan liefert den Workflow und eine kurze Anleitung (README oder Plan-Checkpoint): Repo anlegen, Remote setzen, Pages-Quelle auf „GitHub Actions“ stellen. Die Verifikation der öffentlichen URL (DEPL-02) ist ein menschlicher Checkpoint nach diesem Push. Der Executor legt **kein** Repo an und pusht nicht ungefragt.

### Prüfungen
- **D-11:** **Der Playwright-Smoke-Test läuft in der CI vor dem Deployment** und blockiert es bei einem Fehler. Er nutzt `@playwright/test`, und in der CI wird nur Chromium installiert (`npx playwright install --with-deps chromium`). Geprüft wird gegen `vite preview` des Produktions-Builds. Je Route wird geprüft: Die Seite rendert, es gibt keine Konsolenfehler, die Diagramme enthalten Daten, und es gibt keine `.invalid`-Platzhalter. Er kann ein eigener CI-Job oder ein Schritt im `app`-Job sein. Das entscheidet der Planer.
- **D-12:** **Der Smoke-Test deckt alle Routen ab, nur in der Desktop-Ansicht.** Das sind alle Menürouten, `/glossar`, die neue Seite „Über dieses Projekt“ und `/produkt/:code` für ein Beispielprodukt. Die Nutzbarkeit bei 360 px (A11Y-03) und das Öffnen der Quellenleiste werden **nicht** im Smoke-Test geprüft, sondern über Komponententests bzw. die Verifikation (VERIFICATION/UAT).
- **D-13:** **Barrierefreiheit wird zweistufig nachgewiesen.** `@axe-core/playwright` prüft im Smoke-Test jede Route und blockiert bei Verstößen. Dazu kommt ein **einmaliger Lighthouse-Lauf** auf allen Routen, mit dem a11y-Wert je Route im Verifikationsbericht (Ziel ≥ 95). Lighthouse kommt nicht als Abhängigkeit in die `package.json` und läuft nicht in der CI. Es wird einmalig über `npx` bzw. einen lokalen Chrome aufgerufen.
- **D-14:** **Paketfreigabe:** Der Nutzer hat in dieser Diskussion `@playwright/test` und `@axe-core/playwright` (npm, dev) sowie `pypdfium2` und `Pillow` (PyPI, zum Rendern der WebP-Seiten) freigegeben. Installiert werden die neuesten stabilen Versionen **ohne weiteren Checkpoint**. Lockfiles werden aktualisiert. Für jedes andere neue Paket gilt weiterhin die Regel aus Phase 1: vorher freigeben lassen.

### Text- und Aufräumdurchgang
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

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` §4.4 (`quellen.json`: Schlüssel → `{pdf_seite, bbox, bild}`), §5.1/§5.2 (Werkzeuge, Schritt `08_quellenbelege.py`), §5.6 (Quellenbelege: 2 px/pt, WebP Q60, Seitenleiste), §6.15 (gemeinsame UI-Elemente), §8 (Qualität, Playwright-Smoke-Test), §9 P7

### Projekt & Anforderungen
- `.planning/PROJECT.md` — Core Value, Constraints (Barrierefreiheit, keine Drittanbieter-Requests, Datenschutz), Key Decisions (Paketfreigabe, SHA-gepinnte Actions)
- `.planning/REQUIREMENTS.md` — DATA-04, UI-02, UI-06, A11Y-01…04, QUAL-02, DEPL-01, DEPL-02
- `.planning/ROADMAP.md` Phase 7 — Erfolgskriterien 1–5

### Vorentscheidungen
- `.planning/phases/05-leitfragen-seiten/05-CONTEXT.md` — D-17 (Kontakt-Platzhalter als Deployment-Gate), D-13 (Menü, Fokussteuerung), D-08 (Farben/Kontraste), D-12 (mobile Alternative)
- `.planning/phases/06-kontext-seiten/06-CONTEXT.md` — D-19 (Menügruppe „Mehr wissen“)
- `.planning/phases/05-leitfragen-seiten/05-UI-SPEC.md`, `.planning/phases/06-kontext-seiten/06-UI-SPEC.md` — Design-Vertrag, Typografie- und Spacing-Skala (für D-17/D-18)
- `.planning/phases/05-leitfragen-seiten/05-UI-REVIEW.md` — Token-Hygiene (D-17)
- `.planning/phases/06-kontext-seiten/06-UI-REVIEW.md` — Kosmetik und MenueGruppe-Test (D-18, D-19)
- `.planning/phases/02-kernzahlen/02-REVIEW.md`, `.planning/phases/02-kernzahlen/02-REVIEW-DISPOSITION.md` — offene Warnungen (D-20)
- `.planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW.md`, `.planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md` — WR-01…WR-05, IN-02 (D-20)

### Code
- `app/src/config.ts` — `KONTAKT_EMAIL`, `ORIGINAL_PDF_URL`, `istPlatzhalter` (D-06, D-07)
- `.github/workflows/ci.yml` — bestehende Jobs `pipeline`/`app`, SHA-Pins, `contents: read` (D-09, D-11)
- `pipeline/jahrgaenge/2026.toml` — PDF-Pfad und Jahrgangswerte (Schritt 08 liest von dort)

### Extern
- Münster-Vorbild `codeformuenster/haushalt-muenster-2026`: `quellen.py` und `QuelleSeitenleiste` (Muster für D-01…D-04, Erlaubnis liegt vor)
- GitHub-Pages-Deployment mit `actions/deploy-pages` (D-09)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `KennzahlKachel.vue`, `DatenTabelle.vue` + `components/datenTabelle.ts`: Einbaupunkte für den Knopf „Quelle anzeigen“ (D-01)
- `ChartCard.vue`: Rahmen jedes Diagramms, Ansatzpunkt für den Inventar-Test (D-16)
- `BerechnetEtikett.vue`: Kennzeichnung berechneter Werte, liefert den Hinweistext bei fehlendem bbox (D-03)
- `MenueGruppe.vue`, `lib/menue.ts`, `lib/menueVersatz.ts`: Testobjekt für D-19, Menüeintrag für „Über dieses Projekt“ bzw. Fußzeilenlink
- `lib/bewegung.ts`: `prefers-reduced-motion`-Logik ist bereits vorhanden
- `lib/ansage.ts`, `lib/sprungziel.ts`: Fokus und Ansage beim Routenwechsel sind vorhanden. Phase 7 prüft sie auf allen Routen.
- `lib/bildschirm.ts`: Breakpoint für die vollbreite Leiste mobil (D-04)
- `src/lib/__tests__/stiltokens.test.ts`: Typografie-Wächter, wird auf alle Dateien ausgeweitet (D-17)
- `src/lib/__tests__/config.test.ts`: Platzhalterprüfung (D-07)

### Established Patterns
- Die App-JSONs tragen bereits `pdf_seite` an vielen Datensätzen (`haushalt.json` 132×, `investitionen.json` 145×, `produkte.json` 449×, `stellenplan.json` 162×, zusammen 188 verschiedene Seiten). Bisher speichert keine CSV Koordinaten bzw. bbox. Schritt 08 muss die Zeilen auf der Seite neu finden.
- Die Pipeline-Schritte 01–07 sind dünne typer-Skripte mit Logik in `pipeline/ostbevern/` und laufen über `alle.py --jahr`. Schritt 08 reiht sich ein, und die CI-Diff-Prüfung gilt dann auch für `app/public/quellen/` und `quellen.json`. Das Rendern muss deterministisch sein, sonst schlägt der Diff fehl.
- Texte nur aus Daten mit Platzhaltern, kein `v-html`, CSS-Präfix `om-`, nur `--wa-*`-Tokens, Du-Anrede
- Neue Pipeline-Texte (Impressum und „Über“) laufen über `daten/manuell/texte/` und Schritt 07 oder sind statischer App-Text ohne Zahlen. Das entscheidet der Planer, die Regeln gelten in beiden Fällen.
- App-Checks laufen im Linux-Sandbox in einer Scratch-Kopie, weil `app/node_modules` macOS-Binaries enthält. Das gilt auch für Playwright.

### Integration Points
- `app/src/App.vue` (Fußzeile Z. ~191/202): PDF-Link, Kontakt, neuer Link „Über dieses Projekt“
- `app/src/router/index.ts`: neue Route für „Über dieses Projekt“ mit `meta.titel`
- `pipeline/alle.py`: Schritt 08 anhängen. `app/public/quellen/` und `app/src/data/quellen.json` kommen dazu (Ort entscheidet der Planer).
- `.github/workflows/ci.yml`: Smoke-Test plus axe und der Deploy-Job

</code_context>

<specifics>
## Specific Ideas

- Öffentliche URL: `https://bitwerkstatt.github.io/ostbevern-money/`
- PDF-Link: `https://www.ostbevern.de/_Resources/Persistent/3/2/6/0/3260f0ed6ed16745ad93c953c061f765866667a6/Haushalt%202026%20komplett.pdf`
- Kontakt: `mail@thomas-manthey.de`
- Die Quellenleiste soll sich wie bei Münster anfühlen: ganze Seite, markierte Zeile, Kontext sichtbar.

</specifics>

<deferred>
## Deferred Ideas

- Verlinkbare Quellenbelege (`?quelle=…` im URL-Zustand) — bewusst nicht in v1 (D-04)
- Smoke-Test bei 360 px und für alle 63 Produktseiten — bewusst nicht im Smoke-Test (D-12). Ein späterer Ausbau ist möglich.
- Lighthouse CI als dauerhaftes CI-Gate — derzeit einmaliger Lauf (D-13)
- Eigene Domain für die App — derzeit nur github.io
- `/gsd-secure-phase 04` steht weiter aus (Blocker aus STATE.md). Das ist nicht Teil dieser Diskussion, sollte aber vor dem Abschluss des Meilensteins erledigt werden.

</deferred>

---

*Phase: 07-feinschliff-und-veroeffentlichung*
*Context gathered: 2026-10-06*
