# Milestones

## v1.0.1 Restpunkte (Shipped: 2026-10-09)

**Phases completed:** 2 phases, 28 plans, 69 tasks

**Key accomplishments:**
- Jahreszahlen in den Erklärtexten sind nur noch `{{jahr.…|jahr}}`-Platzhalter (relative Schlüssel plus `jahr.fest_JJJJ`), `pruefe_text` und das neue `pruefe_titel` lehnen jede getippte Jahreszahl 1900-2099 ab, und die jahrneutralen Texte bleiben für jedes Jahr sichtbar.
- Die Regel „rd.“/„rund“ mit U+00A0 steht jetzt nur in charts/format.ts, die Geldfluss-Lesehilfe unterscheidet vier Bilanzfälle (genau nur ohne jeden Ausgleich), und /geldfluss und /ausgaben teilen sich minderaufwandBetrag, die bei Z. 27 > 0 laut wirft.
- Alle drei Stellenplan-Kacheln tragen jetzt "berechnet" samt Herleitung und nennen nur ihre eigenen PDF-Seiten; eine gemeinsame Pruefung `einwohnerZahl()` macht eine fehlende Einwohnerzahl zum lauten Datenfehler statt zur Spalte voller Striche.
- Zwölf handgebaute „rd.“-Kopien in Tabellen, Kacheln, Treemap, Drilldown und Zeitreihen laufen jetzt über EuroBetrag bzw. betragMitHinweis/kurzMitHinweis aus charts/format.ts (05/WR-01, TXT-04).
- `zusammen()` sagt jetzt, ob die Summe gedruckt oder von der App gebildet ist, die Zeile „Zusammen“ der Zuschüsse entsteht über `EuroBetrag` mit Etikett nur bei berechneter Summe, die drei rd.-Altkopien in `ZuschussListe` sind weg, und die Filtersumme auf /investitionen trägt das Etikett „berechnet“.
- Scrollbare DatenTabelle-Rahmen sind nur noch bei Ueberlauf fokussierbare Regionen mit genau einem Namen (Caption per aria-labelledby, useId), jeder Linkklick im 360-px-Drawer schliesst das Menue und setzt den Fokus auf die h1, und menueVersatz wird per Playwright statt per Quelltext geprueft.
- Neuer Waechter-Test rdregel.test.ts (import.meta.glob ?raw, Kommentare entfernt, fail-first gegen die Vorphasen-SteuerZeitreihe.vue) sperrt die rd.-Regel auf charts/format.ts; dazu Token-Waechter-Grenzen und D-14-Begruendungen in allen Quelltext-Tests.
- Typisierte Fehler fuer Division durch 0 (06/IN-08) und negative Jahrgangs-Anzahlen (01/IN-04), Glossar-Invariante absaetze[0] (05/IN-11), einmaliges pdf_relativ (01/IN-02) sowie aktualisierter CI-Block in CLAUDE.md und ci.yml-Kopfkommentar, mit byte-identischer Pipeline-Ausgabe.
- Warn-Icon im Beispieldaten-Callout, verwaiste beispieldaten.json entfernt, eine Flächenfarbe (`flaechenFarbe()`) nur aus echartsTheme.ts, zwei-Marker-`alsRgb` und die Markup-/Vergleichs-Nits aus 06/IN-06.
- Fuenf Varianten von "Index des Haushaltsjahrs suchen, sonst werfen" und zwei `wertartAn`-Kopien durch `haushaltsjahrIndex()`/`wertartAn()` in `lib/jahr.ts` ersetzt, dazu `postenEintrag()` und `anzahlText` — reine Deduplizierung, alle Zahlen und generierten Daten byte-identisch.
- Neues Modul lib/hilfsfunktionen.ts (quellenZeile, jahreListe, klickIndex ohne Datenzugriff) und ein einziger useMassnahmenFilter-Aufruf je Seite, den die Filterzeile als Prop steuerung erhält
- Die drei Review-Ledger (01, 05, 06) stehen auf `open: 0`: 27 der 28 offenen Befunde sind mit Plan und Commit-Hash als fixed belegt, 06/WR-01 ist mit UAT 06 Test 1 und PROJECT.md:138 als skipped begründet; die CI-identische Prüfkette ist auf dem Endstand der Phase grün.
- Security register of phase 4 with all 21 threats closed against the code after phase 8, each row backed by a file:line read in this plan and tests that ran green with zero skips
- Pure `tabellenRahmen` rule keeps every overflowing DatenTabelle frame focusable, role-bearing and named (blank `beschriftung` falls back to „Tabelle“), tests proven red first, ledger 08 on `open: 0`, 08-VERIFICATION renewed.
- Ein gepinnter CI-Gesamtlauf (681 pytest-Tests ohne Skip, alle.py mit Regeln 1-10 grün und byte-identisch, 2162 Vitest-Tests, Playwright ci 89, mobil 41, texte 1) als gemeinsame Evidenz in 09-BASISLAUF.md
- 01-VERIFICATION.md von Phase 1 neu erstellt: alle zehn Wahrheiten und fünf Roadmap-Kriterien gegen den Code nach Phase 8 geprüft, Ergebnis passed 10/10 mit Fingerprint v3, ohne Lücken und ohne Regression.
- 02-VERIFICATION.md von Phase 2 neu goal-backward gegen den Endstand nach Phase 8 geschrieben: status passed, 5/5 Roadmap-Kriterien, 10/10 Anforderungen, re_verification-Block und fingerprintierter covered_digest (v3), `verification.status` meldet nicht mehr stale.
- Phase 3 neu goal-backward gegen den Endstand verifiziert: 12 von 12 Wahrheiten, status passed, Fingerprint v3, kein stale mehr
- Phase 4 (Manuelle Daten und App-Daten) ist goal-backward gegen den Endstand nach Phase 8 neu verifiziert: `04-VERIFICATION.md` steht auf `passed` (10/10), trägt einen frischen v3-Fingerprint auf Archivpfaden und liest sich nicht mehr als stale.
- Phase 5 (Leitfragen-Seiten) goal-backward gegen den Endstand nach Phase 8 neu verifiziert: 11/11 Wahrheiten in Code und Daten belegt, keine Regression, Status `human_needed` mit fünf ehrlich offenen Browserpunkten, Fingerprint v3, nicht mehr stale
- Phase 6 (Kontext-Seiten) neu goal-backward gegen den Endstand nach Phase 7 und 8 verifiziert: 6/6 Wahrheiten, 15 von 15 Anforderungen erfuellt, Fingerprint v3, `verification.status` = passed statt stale
- Phase 7 (Feinschliff und Veröffentlichung) goal-backward gegen den Endstand nach Phase 8 und dem D-20-Fix neu verifiziert: `07-VERIFICATION.md` meldet `passed` (4 von 5 Kriterien vom Verifier geprüft, Deploy und Gerätecheck als vom Nutzer bestätigt gekennzeichnet) und ist mit `verification.fingerprint` nicht mehr stale.
- Drei erledigte Eintraege (Code-Review-Restbefunde, secure-phase 04, Milestone-Audit) aus STATE.md Blockers/Concerns entfernt, jeweils mit Beleg; Deploy-/Geraetecheck-Vermerk in REQUIREMENTS.md ergaenzt.
- Audit-Datei fuer v1.0 und v1.0.1 mit Phasentabelle 1-9, allen 102 Anforderungen aus REQUIREMENTS, VERIFICATION und SUMMARY (97 satisfied, 5 partial) und den Nyquist-Befunden als deferred tech_debt
- Integration der Datenkette 8/8 wired, End-to-End-Flüsse 4/7 complete, und eine nach D-10 triagierte Lückenliste mit 23 Zeilen, aus der drei Kernaussage-Lücken (fester Superlativ, „PDF-Seite“ im Singular, Grundsteuer ohne „berechnet“) an Plan 09-14 gehen
- Drei Lücken der Kernaussage (Superlativ auf der Startseite, „PDF-Seite“ im Singular, fehlendes Etikett „berechnet“ an „Grundsteuer (A+B)“) mit je einem vorher roten Test behoben und im Audit mit Fix- und Test-Hash als fixed belegt; alle.py byte-identisch.
- Die nach 09-14 wieder veralteten Berichte 05, 06 und 08 mit Nachtrag und neuem Digest belegt, die volle CI-Kette auf dem Endstand grün (681 pytest ohne Skip, alle.py byte-identisch, Playwright 89 und 41), Audit auf `tech_debt` finalisiert und SEC-01, AUD-01 bis AUD-03 abgehakt.
- A11Y-03 (v1.0.1) ist mit gekennzeichnetem Nutzerbeleg 08-UAT Test 1 durchgehend satisfied: Audit 98/102, G-09-11 closed, 08-VERIFICATION.md konsistent passed mit frischem Digest, ohne Code- oder Datenaenderung.

**Timeline:** 3 days (2026-10-07 → 2026-10-09), 217 commits
**Git range:** `01c7311` → `b329e4a`

**Closeout:** override_closeout
- Milestone-Audit `v1.0.1-MILESTONE-AUDIT.md`: Status `tech_debt`, Anforderungen 17/17, Integration 8/8, Flows 7/7.
- Known verification overrides: 1 newly acknowledged (05/05-VERIFICATION.md, human_needed, archiviert v1.0), 0 carried forward.
- Akzeptierte technische Schuld: Ledger `09-REVIEW-DISPOSITION.md` mit `open: 6` (WR-01..03, IN-01..03), darunter der sichtbare Befund 09/WR-02 (unsortierte PDF-Seitenangaben).

---

## v1.0 MVP (Shipped: 2026-10-07)

**Delivered:** Öffentliche, statische App unter https://bitwerkstatt.github.io/ostbevern_money/, die den Haushalt 2026 der Gemeinde Ostbevern mit den Leitfragen „Woher?“ und „Wofür?“ erklärt. Jede Zahl stammt aus einer geprüften Python-Pipeline über das 400-seitige ProFIS+-PDF.

**Phases completed:** 7 phases (1–7), 68 plans, 160 tasks
**Timeline:** 7 days (2026-10-01 → 2026-10-07), 674 commits
**Code:** ~25.500 LOC Python (Pipeline), ~29.900 LOC TypeScript/Vue (App inkl. e2e)
**Git range:** `31105eb` (initial commit) → `01c7311`

**Key accomplishments:**
- Pipeline klassifiziert alle 400 PDF-Seiten und extrahiert Gesamt- und Teilpläne, Produktinformationen, Grundzahlen, Erläuterungen, Investitionen, VE-Fälligkeiten und den Stellenplan über Koordinaten-Parser. Alle Jahrgangswerte stehen in `jahrgaenge/2026.toml`.
- Die zehn Prüfregeln sind grün, z. B. Formelketten über 6550 Werte, Anhang-B-Sollwerte, Querschnitte, Investitionssummen und Vollständigkeit aller 63 Produkte. Jede gedruckte Abweichung ist einzeln mit Seite in `befunde.md` belegt. `alle.py` erzeugt `daten/` und `app/src/data/` byte-identisch, die CI prüft das.
- Leitfragen-Seiten: Start mit Kennzahlen, Einnahmen, Ausgaben mit Treemap-Drilldown und herausgelöster „Weitergabe an Kreis und Land“, Produktseiten für alle 63 Produkte, Geldfluss-Sankey und Glossar.
- Kontextseiten: Entwicklung 2024–2029 mit Rücklagen, Investitionen und Schulden, „Worüber entscheidet der Rat?“, Stellenplan und der Hinweis „Was nicht im Haushalt steht“.
- Quellenbelege: 2496 Werte sind mit Zeilenrechteck auf gerenderten, geschwärzten PDF-Seiten belegt und lassen sich über „Quelle anzeigen“ öffnen.
- Barrierefreiheit und Betrieb: Lighthouse-a11y 100 auf allen 11 Routen, axe-Smoke-Test und 360-px-Prüfungen in Playwright, Du-Anrede-Wächter. Der Deploy auf GitHub Pages läuft nur nach grüner CI.

**Closeout:** override_closeout
- Kein Milestone-Audit (`/gsd-audit-milestone`) durchgeführt. Der Nutzer hat entschieden, ohne Audit abzuschließen.
- Known verification overrides: 7 Phasen mit Verifikationsstatus „stale“ (VERIFICATION.md älter als spätere Commits), vom Nutzer akzeptiert. 0 Artefakte acknowledged, 0 aus früheren Abschlüssen übernommen.
- Drei Debug-Sessions (`glossar-sprung-scrollt-zu-weit`, `kachel-kreisumlage-480px`, `produkt-glossarbegriff-ueberlappung`) hat der Nutzer beim Abschluss als gelöst markiert.
- Anforderungen: 85/85 v1-Anforderungen abgehakt.

**Nachtrag 2026-10-09 (v1.0.1, Phase 9):** Audit und Re-Verifikation in v1.0.1 / Phase 9 nachgeholt. Der Bericht `.planning/v1.0-MILESTONE-AUDIT.md` prüft v1.0 und v1.0.1 gemeinsam (Status `tech_debt`, keine offene Lücke der Kernaussage, 98 von 102 Anforderungen ohne Vorbehalt, die übrigen vier mit begründet zurückgestellten Browser-Belegen). Die sieben Verifikationen der Phasen 1–7 sind erneuert und stehen nicht mehr auf „stale“. `04-SECURITY.md` liegt mit `threats_open: 0` vor. Der Closeout-Text darüber bleibt als historischer Stand unverändert.

---
