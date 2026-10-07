---
phase: "7"
slug: "feinschliff-und-ver-ffentlichung"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-10-07"
---

# Phase 7 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Haushalts-PDF → Schritt 08 | Zeilensuche und Seiten-Rendering aus dem Gemeinde-PDF | Seitenbilder mit möglichen Personennamen (Datenschutz) |
| Pipeline → App-Daten | `quellen.json`, WebP-Seiten unter `app/public/quellen/` | Belegschlüssel, Rechtecke (Integrität der Belege) |
| App → Browser | Statische Seite, Quell-Leiste, externe Links | Keine Nutzerdaten; nur Same-Origin-Requests |
| CI → GitHub Pages | Build, Upload, Deploy mit `pages: write` / `id-token: write` | Veröffentlichtes Artefakt (öffentlich) |
| Paketquellen → Sandbox/CI | npm, PyPI, Playwright-Browser, lighthouse (einmalig) | Lieferkette |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-07-01 | Tampering | quellen.finde_planzeile | high | mitigate | Zeilennummer + Betrag + genau ein Kandidat, sonst Grund (`quellen.py:273-299`, Tests `test_quellen.py:114,247,255,263`) | closed |
| T-07-02 | Information Disclosure | belegbilder.rendere_seiten | high | mitigate | `BelegbildFehler` vor dem Schreiben (`belegbilder.py:76-86`); faktische Kontrolle über `ProdukteFehler` (`produkte.py:879-884`) | closed |
| T-07-03 | Tampering | QuelleKnopf, QuelleSeitenleiste | medium | mitigate | Kein `v-html`/`innerHTML`; Guard `quelltext.test.ts:68,209-217` | closed |
| T-07-04 | Spoofing | Link zum Original-PDF | low | mitigate | Ganzzahlige Seite ≥ 1 (`quelle.ts:184-189`); `rel="noopener noreferrer"` an allen `_blank`-Links | closed |
| T-07-05 | Tampering | bildUrl, bild_name | low | mitigate | Namen nur `s{nnn:03d}.webp`; BASE_URL-Präfix; Same-Origin-Prüfung `quelle.spec.ts:238-250` | closed |
| T-07-06 | Tampering | D-20-Korrekturen | high | mitigate | CI-Reproduzierbarkeitsgate `ci.yml:44-52`; 07-02-Commits ohne Datenänderung | closed |
| T-07-07 | Tampering | lies_befunde, ve_uebersicht, pruefe_text | medium | mitigate | Fail-fast-Guards `pruefung.py:341-384,682,1747`, `texte.py:189-212` mit Tests | closed |
| T-07-08 | Information Disclosure | Produktinformationen-Bilder | high | mitigate | `personenfeld_rechtecke` + Schwärzung mit 2 px Überstand; Geometrie- und Pixeltest `test_belegbilder.py:205,231` | closed |
| T-07-09 | Information Disclosure | Übrige Belegseiten | medium | mitigate | Datenschutz-Prüfliste `quellenbelege.md:82-236`, Hook `schwaerzen_nach`; Nutzerentscheidung 07-10 | closed |
| T-07-10 | Tampering | Suche je Belegtyp | high | mitigate | Finder liefern `None` + Grund bei 0 oder >1 Treffern; Duplikat-Test `test_quellen.py:489` | closed |
| T-07-11 | Repudiation | Belege ohne Rechteck | medium | mitigate | Bericht durch Schritt 08, CI-Diff auf `daten/`, Test `test_quellen.py:522` | closed |
| T-07-12 | Tampering | quellen.json, Bilder | medium | mitigate | Rundung, Sortierung, nur fehlende Bilder rendern; CI-Prüfung auf ungetrackte Dateien `ci.yml:57-60` | closed |
| T-07-13 | Denial of Service | Stiländerungen | low | accept | AR-01 | closed |
| T-07-14 | Spoofing | UeberPage, Fußzeile | medium | mitigate | Inoffiziell-Hinweis, Tests `config.test.ts:123,131-133,178-181` | closed |
| T-07-15 | Info Disclosure / Repudiation | Impressum-Platzhalter | high | mitigate | Platzhalter-Prädikate, Smoke-Check auf `.invalid`, echte Werte erst nach Abnahme (b29be89) | closed |
| T-07-16 | Spoofing | Externe Links | low | mitigate | `rel`-Anzahl = `_blank`-Anzahl (`config.test.ts:135-142,206-213`) | closed |
| T-07-17 | Tampering | Kachel- und Tabellenschlüssel | medium | mitigate | Schlüssel nur über `belegSchluessel`; Auflösung per `findeBeleg` getestet | closed |
| T-07-18 | Tampering | Schlüssel /einnahmen, /ausgaben | medium | mitigate | `quelle-leitfragen.test.ts:60-195` über alle Jahre und Modi | closed |
| T-07-19 | Tampering | Zuschuss-, Maßnahmen-, Stellenschlüssel | medium | mitigate | `quelle-kontext.test.ts:60-163` | closed |
| T-07-20 | Repudiation | Ausnahmeliste Inventar | medium | mitigate | Geschlossene Liste mit einem begründeten Eintrag (`inventar.spec.ts:8-20`), läuft in CI | closed |
| T-07-21 | Repudiation | Texte, /ueber | medium | mitigate | Abnahme wörtlich in `07-10-SUMMARY.md`; Commit-Reihenfolge 560befa vor b29be89 | closed |
| T-07-22 | Information Disclosure | Seitenbilder mit Namen außerhalb der Personenfelder | high | mitigate | Nutzerentscheidung 07-10 (Seiten 9, 17, 18, 32, 48, 284 freigegeben; s072/s127 bestätigt); S. 75 und 95 als Fehltreffer geprüft (siehe Hinweise) | closed |
| T-07-23 | Spoofing | Impressum | medium | mitigate | Test „veröffentlichungsbereit“ (`config.test.ts:92-105`), Smoke-Check | closed |
| T-07-24 | Elevation of Privilege | ci.yml Deploy-Rechte | high | mitigate | Global `contents: read`; `pages: write`/`id-token: write` nur im Deploy-Job, nur `main`, nie für PRs | closed |
| T-07-25 | Tampering | Third-party Actions | high | mitigate | Alle 5 `uses:` auf 40-stellige SHA gepinnt | closed |
| T-07-26 | Information Disclosure | Laufzeit-Requests | medium | mitigate | Smoke- und Quelle-Spec scheitern bei Fremd-Origin; läuft in CI | closed |
| T-07-27 | Spoofing | Kontakt in Fußzeile/Impressum | medium | mitigate | Smoke-Check auf `.invalid` je Route | closed |
| T-07-28 | Tampering | lighthouse-Installation | high | mitigate | Version 13.5.0 gepinnt, `--ignore-scripts`, nur Scratch-Verzeichnis, nicht in package.json/CI; Freigabe „approved“ | closed |
| T-07-29 | Information Disclosure | Erster öffentlicher Push | high | mitigate | Datenschutzprüfung (07-10) vor dem Push; Push durch den Nutzer | closed |
| T-07-SC | Tampering | npm/pip-Installationen, CI-Browser-Download | high | mitigate | Exakte Pins, Lockfiles, `uv sync --locked`, keine neuen Abhängigkeiten außer 07-01 | closed |
| T-07-30 | Repudiation | app/e2e/kacheln.spec.ts | medium | mitigate | Im Playwright-Projekt `ci` (`playwright.config.ts` ignoriert nur mobil/textliste); geschlossene Routenliste `KACHEL_ROUTEN` mit Klassifikationstest (`kacheln.spec.ts:32,362-368`); feste `TOLERANZ = 0.5` (`:29`); rote Ausgangsmessung in 07-13-SUMMARY | closed |
| T-07-31 | Tampering | KennzahlKachel-Beträge | medium | mitigate | `git diff --quiet a02a28c HEAD -- pipeline daten app/src/data app/src/charts/format.ts` leer; Spec prüft eine Zeile (`getClientRects`, `:183`) und Größe `--wa-font-size-l` (`:112-175`) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-01 | T-07-13 | Token-Wechsel innerhalb der freigegebenen Skala; axe und Lighthouse (100 auf 11 Routen) ohne Befund | Planer (07-04-PLAN) | 2026-10-06 |
| AR-02 | T-07-SC (07-02 … 07-10) | Keine neue Abhängigkeit; Git-Historie bestätigt Änderungen nur in 07-01 | Planer (Threat-Modelle) | 2026-10-06 |
| AR-03 | T-07-09, T-07-22 | Seiten 9, 17, 18, 32, 48, 284 ungeschwärzt veröffentlicht (Amts- und Unterzeichnerrollen) | Nutzer (07-10-Abnahme) | 2026-10-06 |
| AR-04 | T-07-22 | Veröffentlichung gerenderter Seiten des Gemeinde-PDFs | Nutzer (07-10-Abnahme) | 2026-10-06 |
| AR-05 | T-07-15, T-07-23 | Impressum mit eigenem Namen und Anschrift; IP-Satz zu GitHub Pages | Nutzer (07-10-Abnahme) | 2026-10-06 |
| AR-06 | T-07-28 | Einmalige Nutzung von lighthouse@13.5.0 ohne Lockfile für Unterabhängigkeiten | Nutzer („approved“, 07-12) | 2026-10-07 |
| AR-07 | T-07-29 | Öffentliches Repository und GitHub-Pages-Deployment | Nutzer („veröffentlicht“, 07-12) | 2026-10-07 |
| AR-09 | T-07-SC (07-13) | Keine neue Abhängigkeit (package.json, package-lock.json, uv.lock unverändert seit a02a28c); npm ci nur in Scratch-Kopien | Planer (07-13-PLAN) | 2026-10-07 |
| AR-08 | T-07-29 | `raw_data/haushalt-2026.pdf` (ungeschwärztes Original der Gemeinde) ist im öffentlichen Repository; dieselbe Datei ist bei der Gemeinde öffentlich verfügbar und verlinkt; nicht in `app/dist` | Nutzer (Sicherheitsprüfung) | 2026-10-07 |

*Accepted risks do not resurface in future audit runs.*

---

## Hinweise aus dem Audit (ändern keinen Status)

1. **T-07-02:** Der `BelegbildFehler`-Guard greift in der Produktion praktisch nicht, weil Produktinformationen-Seiten ohne Rechtecke als `ohne_personenfelder` durchgereicht werden (`quellen.py:1446-1451`). Die wirksame Kontrolle ist `ProdukteFehler` (`produkte.py:879-884`) plus Geometrie- und Pixeltest.
2. **T-07-22:** Die Prüfliste nennt auch S. 75 („Bürgermeister“, Z. 20) und S. 95 („Telefon“, Z. 22). Beide wurden im PDF geprüft: Fehltreffer ohne Personennamen (Aufwandsbeschreibungen). Keine Offenlegung.
3. **T-07-29:** `raw_data/haushalt-2026.pdf` ist seit Phase 1 versioniert und wurde mit dem Push öffentlich, einschließlich der Mitarbeitendennamen, die die Seitenbilder schwärzen. Es ist dieselbe öffentliche Datei der Gemeinde, auf die `ORIGINAL_PDF_URL` verlinkt; das ausgelieferte `app/dist` enthält sie nicht. Vom Nutzer als Risiko akzeptiert (AR-08).
4. **T-07-28 / T-07-SC:** lighthouse wurde ohne Lockfile installiert; Restrisiko begrenzt (keine Install-Skripte, Scratch-Verzeichnis, einmalig, nicht in CI).
5. **T-07-01:** Zeilen mit Betrag 0 werden nur über die Zeilennummer gefunden (`quellen.py:291`), weiterhin mit genau einem Treffer.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-10-07 | 30 | 30 | 0 | gsd-security-auditor (ASVS L1, block_on high) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-10-07

## Security Audit 2026-10-07

| Metric | Count |
|---|---|
| Threats found | 32 |
| Closed | 32 |
| Open | 0 |
