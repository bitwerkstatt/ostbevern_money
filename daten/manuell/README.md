# Manuell abgeschriebene Vorberichtstabellen

Dieser Ordner enthält Vorberichtstabellen, die von Hand aus `raw_data/haushalt-2026.pdf`
abgeschrieben wurden (D-09, MANU-07), weil sie als reiner Fließtext mit Tabellenlayout
gedruckt sind und sich mit dem koordinatenbasierten Pipeline-Parser nicht zuverlässig
automatisiert extrahieren lassen. Die Abschrift ist **einmalig**: Nach dem Commit
überschreibt **kein Pipeline-Schritt** diese Dateien — `ostbevern.schema.schreibe_vorbericht_csv`
wird nur bei der Abschrift selbst und in Tests aufgerufen. Tippfehler fängt
[Regel 5](../pruefberichte/befunde.md) ab (zweistufiger Soll/Ist-Vergleich gegen die
gedruckte Gesamtzeile und den Gesamtergebnisplan); die CI prüft zusätzlich, dass sich
dieser Ordner bei einem erneuten Pipeline-Lauf nie ändert (D-24).

## Spaltenformat (`VORBERICHT_SPALTEN`, `ostbevern/schema.py`)

Jede Datei folgt demselben Langformat — eine Zeile je Posten, Jahr und Wertart:

| Spalte | Bedeutung |
|---|---|
| `tabelle` | Tabellenname, identisch zum Dateinamen ohne `.csv` |
| `position` | Gedruckte Reihenfolge der Zeile (1-basiert); die Gesamtzeile hat die höchste Position |
| `posten` | Schlüssel in Snake-Case ohne Umlaute, z. B. `grundsteuer_a` |
| `posten_name` | Gedruckter Name, wortwörtlich abgeschrieben (inkl. Abkürzungen wie „Krankenhausinvestitionsuml.“) |
| `ist_gesamt` | `true` für die gedruckte Gesamtzeile, sonst `false`; genau eine je (`tabelle`, `jahr`) |
| `jahr` | Haushaltsjahr der Spalte |
| `wertart` | `ergebnis` (Spalte „2024 vorl. RE“), `ansatz` oder `planung` — abgeleitet aus den Ergebnisplan-Spaltenköpfen der Jahrgangsdatei, nie von Hand eingetragen |
| `betrag_teur` | Betrag **in T€, exakt wie gedruckt** (D-05) — nie Euro, nie angepasst, auch wenn er von anderen Quellen abweicht |
| `anmerkung` | Fußnotentext oder sonstige Erläuterung zur Zeile, leer wenn keine vorhanden |
| `quelle` | 1-basierte PDF-Seite der gedruckten Zeile |

## Dateien

### `steuerarten.csv`

Vorbericht Tabelle 2.1.1 „Steuern und ähnliche Abgaben“ (S. 27): die acht Steuerarten
(Grundsteuer A/B, Gewerbesteuer, Anteil Einkommen-/Umsatzsteuer, Vergnügungs- und
Hundesteuer, Kompensationszahlungen) plus Gesamtzeile, für 2024–2029. Die Posten-Summe
trifft die gedruckte Gesamtzeile und die GEP-Zeile 01 in allen sechs Jahren exakt
(Regel 5 ohne Befund).

### `zuwendungen.csv`

Vorbericht Tabelle 2.1.2 „Zuwendungen und allgemeine Umlagen“ (S. 28): Schlüsselzuweisung,
Zuweisungen für lfd. Zwecke, Auflösung von Sonderposten, Gesamt. Zwei bekannte, im PDF
selbst liegende Abweichungen sind in `../pruefberichte/befunde.md` dokumentiert:

- 2025 ergibt die Posten-Summe 4.968 T€ gegenüber gedruckten 4.967 T€ (Δ 1 T€).
- 2026 ergibt die Posten-Summe 3.108 T€ gegenüber gedruckten 3.109 T€ (Δ 1 T€), und die
  gedruckte Gesamtzeile (3.109 T€ = 3.109.000 €) weicht um 4.200 € von der GEP-Zeile 02
  (3.113.200 €) ab (Spez. 3.8). Die App weist diese Differenz als eigenen, berechneten
  Posten „Sonstige“ aus (`ostbevern.app_daten.baue_vorbericht_tabelle`).

### `transferaufwendungen.csv`

Vorbericht Tabelle 2.2.5 „Transferaufwendungen“ (S. 45–46): zehn Posten (Wasser- und
Bodenverband, Zuschüsse an Kindertageseinrichtungen, Zuschuss an das Kinder- und
Jugendwerk, Zuschuss an die OGS, Zuschüsse für lfd. Zwecke, Sozialleistungen,
Gewerbesteuerumlage, Krankenhausinvestitionsumlage, Kreisumlage, Verlustübernahme BBO)
plus Gesamt.

**Kreisumlage, Fußnote (S. 46):** Der Vorbericht druckt den Betrag des Haushaltsjahrs als
„10.1473“ — die Fußnotenziffer 3 ist ohne Leerzeichen an 10.147 angeklebt. Gespeichert ist
der korrigierte Wert `10147` (T€) mit einer Anmerkung, die auf die Fußnote verweist: Zur
Entlastung des Haushalts 2026 wird eine Rückstellung aus dem Jahresabschluss 2024 in Höhe
von 1.325.478 € aufgelöst, die Umlage 2026 liegt bei rd. 11,5 Mio. € (Kreisumlage brutto =
netto + Rückstellungsauflösung, siehe `meta.json`, D-10). Der hier gespeicherte Betrag ist
die Kreisumlage **netto**.

Drei weitere Jahre (2027–2029) haben eine gedruckte Rundungsdifferenz von 1 T€ zwischen
Posten-Summe und Gesamtzeile; dokumentiert in `../pruefberichte/befunde.md`.

**Weitergabe an Kreis und Land (D-01):** Die drei Posten Kreisumlage, Gewerbesteuerumlage
und Krankenhausinvestitionsumlage ergeben in jedem Jahr 2024–2029 (× 1000, Toleranz
±3.000 €) die Zeile 15 des Teilergebnisplans von Produkt 160101 (S. 281) — geprüft von
Regel 5 über `[layout.weitergabe_kreis_land]` in `pipeline/jahrgaenge/2026.toml`.

### `kita_zuschuesse.csv`

Aufschlüsselung der sieben Kindertageseinrichtungen (S. 46) für das Haushaltsjahr 2026 —
die Tabelle druckt nur diese eine Spalte, nicht den ganzen Finanzplanungszeitraum
(MANU-04). Die Summe der sieben Einrichtungen (559 T€) entspricht sowohl der gedruckten
Gesamtzeile dieser Tabelle als auch dem Transferaufwendungen-Posten „Zuschüsse an
Kindertageseinr.“ desselben Jahres — beides prüft Regel 5.
