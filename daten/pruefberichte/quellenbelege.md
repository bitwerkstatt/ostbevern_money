# Quellenbelege – Werte ohne Markierung

Schritt 08 (`pipeline/08_quellenbelege.py`) sucht zu jedem Wert mit PDF-Seite die Zeile
auf der Seite (Beschriftung oder Zeilennummer plus Betrag des Haushaltsjahrs). Ohne genau
einen Treffer bekommt der Beleg kein Rechteck; die App zeigt dann die Seite ohne
Markierung mit einem Hinweis. Diese Datei wird bei jedem Lauf neu geschrieben.

## Überblick

| Art | Belege | ohne Markierung |
|---|---|---|
| ep (Ergebnisplanzeilen) | 1508 | 0 |
| fp (Finanzplanzeilen) | 41 | 0 |
| vb (Vorberichtsposten) | 145 | 20 |
| meta (Meta-Werte) | 19 | 4 |
| gz (Grundzahlen) | 220 | 4 |
| pr (Produktseiten) | 63 | 0 |
| inv (Investitionsmaßnahmen) | 137 | 0 |
| ve (VE-Fälligkeiten) | 6 | 0 |
| sd (Schuldenstand) | 3 | 1 |
| sp (Stellenplan) | 123 | 4 |
| seite (Seitenbelege) | 231 | – |

## vb – Vorberichtsposten

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `vb:eigenkapital:bilanzieller_verlustvortrag` | 311 | betrag_fehlt |
| `vb:eigenkapital:verrechnung_bilanzierungshilfe` | 311 | betrag_fehlt |
| `vb:kostenerstattungen:erst_fuer_essen_in_der_mensa_und_den_ogs` | 32 | betrag_fehlt |
| `vb:kostenerstattungen:erst_v_gemeinden_und_sonst_oeffentlicher_bereich` | 32 | betrag_fehlt |
| `vb:leistungsentgelte:aufloesung_von_sonderposten_aus_beitraegen_und_gebuehren` | 30 | betrag_fehlt |
| `vb:sachaufwand:strassenbeleuchtung_verkehrssicherungsanlagen` | 36 | betrag_fehlt |
| `vb:sonstige_aufwendungen:pruefungsaufwendungen_gerichts_und_sachverstaend` | 48 | betrag_fehlt |
| `vb:sonstige_aufwendungen:wertbericht_zu_forderungen_und_sachanlagen` | 48 | betrag_fehlt |
| `vb:sonstige_ertraege:aufloesung_sonstiger_sonderposten` | 33 | betrag_fehlt |
| `vb:sonstige_ertraege:sonstige` | 33 | berechnet |
| `vb:transferaufwendungen:zuschuss_kinder_jugendwerk` | 46 | betrag_fehlt |
| `vb:zuschuesse_lfd_zwecke:ferienfreizeit_jugendliche` | 47 | nicht_gefunden |
| `vb:zuschuesse_lfd_zwecke:jekits_eigenanteil_schule_fuer_musik` | 47 | nicht_gefunden |
| `vb:zuschuesse_lfd_zwecke:kulturtragende_vereine` | 47 | nicht_gefunden |
| `vb:zuschuesse_lfd_zwecke:restaurierung_private_denkmale` | 47 | nicht_gefunden |
| `vb:zuschuesse_lfd_zwecke:schulsozialarbeit` | 47 | nicht_gefunden |
| `vb:zuschuesse_lfd_zwecke:sportfoerderrichtlinie` | 47 | nicht_gefunden |
| `vb:zuschuesse_lfd_zwecke:vhs` | 47 | nicht_gefunden |
| `vb:zuschuesse_lfd_zwecke:zuschuesse_dritte_soziales_leben` | 47 | nicht_gefunden |
| `vb:zuwendungen:sonstige` | 28 | berechnet |

## meta – Meta-Werte

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `meta:kreisumlage.brutto` | 46 | berechnet |
| `meta:vorbericht_werte.bbo_verlustausgleich_wirtschaftsplan` | 48 | nicht_gefunden |
| `meta:vorbericht_werte.hsk_schwelle_ein_jahr` | 23 | nicht_gefunden |
| `meta:vorbericht_werte.konzessionsabgabe_gas` | 33 | mehrdeutig |

## gz – Grundzahlen

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `gz:010301:5` | 77 | nicht_gefunden |
| `gz:010601:8` | 85 | nicht_gefunden |
| `gz:050103:1` | 183 | nicht_gefunden |
| `gz:050103:2` | 183 | nicht_gefunden |

## sd – Schuldenstand

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `sd:liquiditaetskredite` | 310 | betrag_fehlt |

## sp – Stellenplan

| Schlüssel | PDF-Seite | Grund |
|---|---|---|
| `sp:tarif:2:-` | 285 | mehrdeutig |
| `sp:tarif:4:-` | 285 | betrag_fehlt |
| `sp:tarif:5:-` | 285 | betrag_fehlt |
| `sp:tarif:6:-` | 285 | betrag_fehlt |

## Datenschutz-Prüfliste

Belegseiten, deren Text eines der Stichwörter aus `layout.quellenbelege.pruefwoerter`
enthält (Seite, Stichwort, 1-basierter Zeilenindex auf der Seite; bewusst ohne
Textauszug). Namen außerhalb der Personenfelder der Produktseiten werden nicht
automatisch geschwärzt: Wer ein Etikett vor der zu schwärzenden Zeile kennt, trägt es
in `layout.quellenbelege.schwaerzen_nach` ein.

| Seite | Stichwort | Zeile | geschwärzt |
|---|---|---|---|
| 9 | Bürgermeister | 36 | nein |
| 9 | Kämmerin | 36 | nein |
| 17 | Bürgermeister | 10 | nein |
| 18 | Bürgermeister | 27 | nein |
| 18 | Kämmerer | 27 | nein |
| 32 | Sachbearbeit | 28 | nein |
| 48 | Bürgermeister | 37 | nein |
| 72 | Sachbearbeit | 7 | ja |
| 72 | Verantwortlich | 6 | ja |
| 74 | Ansprechpartner | 14 | nein |
| 74 | Bürgermeister | 5 | nein |
| 74 | Bürgermeister | 9 | nein |
| 74 | Sachbearbeit | 7 | ja |
| 74 | Verantwortlich | 6 | ja |
| 75 | Bürgermeister | 20 | nein |
| 76 | Sachbearbeit | 7 | ja |
| 76 | Verantwortlich | 6 | ja |
| 79 | Bürgermeister | 31 | nein |
| 79 | Bürgermeister | 45 | nein |
| 79 | Sachbearbeit | 7 | ja |
| 79 | Verantwortlich | 6 | ja |
| 81 | Sachbearbeit | 8 | ja |
| 81 | Verantwortlich | 7 | ja |
| 84 | Sachbearbeit | 8 | ja |
| 84 | Verantwortlich | 7 | ja |
| 88 | Sachbearbeit | 7 | ja |
| 88 | Verantwortlich | 6 | ja |
| 92 | Sachbearbeit | 9 | ja |
| 92 | Verantwortlich | 8 | ja |
| 94 | Bürgermeister | 5 | nein |
| 94 | Sachbearbeit | 7 | ja |
| 94 | Verantwortlich | 6 | ja |
| 95 | Telefon | 22 | nein |
| 96 | Sachbearbeit | 7 | ja |
| 96 | Verantwortlich | 6 | ja |
| 98 | Sachbearbeit | 7 | ja |
| 98 | Verantwortlich | 6 | ja |
| 103 | Sachbearbeit | 7 | ja |
| 103 | Verantwortlich | 6 | ja |
| 105 | Sachbearbeit | 7 | ja |
| 105 | Verantwortlich | 6 | ja |
| 107 | Sachbearbeit | 8 | ja |
| 107 | Verantwortlich | 7 | ja |
| 109 | E-Mail | 29 | nein |
| 109 | Sachbearbeit | 7 | ja |
| 109 | Verantwortlich | 6 | ja |
| 113 | Sachbearbeit | 8 | ja |
| 113 | Verantwortlich | 7 | ja |
| 116 | Sachbearbeit | 7 | ja |
| 116 | Verantwortlich | 6 | ja |
| 118 | Sachbearbeit | 7 | ja |
| 118 | Verantwortlich | 6 | ja |
| 120 | Sachbearbeit | 8 | ja |
| 120 | Verantwortlich | 7 | ja |
| 127 | Sachbearbeit | 7 | ja |
| 127 | Verantwortlich | 6 | ja |
| 130 | Sachbearbeit | 7 | ja |
| 130 | Verantwortlich | 6 | ja |
| 132 | Sachbearbeit | 7 | ja |
| 132 | Verantwortlich | 6 | ja |
| 134 | Sachbearbeit | 7 | ja |
| 134 | Verantwortlich | 6 | ja |
| 136 | Sachbearbeit | 7 | ja |
| 136 | Verantwortlich | 6 | ja |
| 138 | Bürgermeister | 14 | nein |
| 138 | Sachbearbeit | 7 | ja |
| 138 | Verantwortlich | 6 | ja |
| 140 | Sachbearbeit | 7 | ja |
| 140 | Verantwortlich | 6 | ja |
| 151 | Sachbearbeit | 7 | ja |
| 151 | Verantwortlich | 6 | ja |
| 155 | Sachbearbeit | 7 | ja |
| 155 | Verantwortlich | 6 | ja |
| 158 | Sachbearbeit | 7 | ja |
| 158 | Verantwortlich | 6 | ja |
| 162 | Sachbearbeit | 8 | ja |
| 162 | Verantwortlich | 7 | ja |
| 165 | Sachbearbeit | 7 | ja |
| 165 | Verantwortlich | 6 | ja |
| 167 | Sachbearbeit | 8 | ja |
| 167 | Verantwortlich | 7 | ja |
| 171 | Sachbearbeit | 7 | ja |
| 171 | Verantwortlich | 6 | ja |
| 174 | Sachbearbeit | 7 | ja |
| 174 | Verantwortlich | 6 | ja |
| 176 | Sachbearbeit | 7 | ja |
| 176 | Verantwortlich | 6 | ja |
| 181 | Sachbearbeit | 8 | ja |
| 181 | Verantwortlich | 7 | ja |
| 183 | Sachbearbeit | 7 | ja |
| 183 | Verantwortlich | 6 | ja |
| 185 | Sachbearbeit | 8 | ja |
| 185 | Verantwortlich | 7 | ja |
| 188 | Sachbearbeit | 7 | ja |
| 188 | Verantwortlich | 6 | ja |
| 190 | Sachbearbeit | 7 | ja |
| 190 | Verantwortlich | 6 | ja |
| 194 | Sachbearbeit | 8 | ja |
| 194 | Verantwortlich | 7 | ja |
| 197 | Sachbearbeit | 9 | ja |
| 197 | Verantwortlich | 7 | ja |
| 200 | Sachbearbeit | 7 | ja |
| 200 | Verantwortlich | 6 | ja |
| 205 | Sachbearbeit | 8 | ja |
| 205 | Verantwortlich | 7 | ja |
| 211 | Sachbearbeit | 8 | ja |
| 211 | Verantwortlich | 7 | ja |
| 215 | Sachbearbeit | 9 | ja |
| 215 | Verantwortlich | 8 | ja |
| 218 | Sachbearbeit | 8 | ja |
| 218 | Verantwortlich | 7 | ja |
| 222 | Sachbearbeit | 7 | ja |
| 222 | Verantwortlich | 6 | ja |
| 224 | Sachbearbeit | 7 | ja |
| 224 | Verantwortlich | 6 | ja |
| 226 | Sachbearbeit | 8 | ja |
| 226 | Verantwortlich | 7 | ja |
| 228 | Sachbearbeit | 7 | ja |
| 228 | Verantwortlich | 6 | ja |
| 232 | Sachbearbeit | 7 | ja |
| 232 | Verantwortlich | 6 | ja |
| 241 | Sachbearbeit | 8 | ja |
| 241 | Verantwortlich | 7 | ja |
| 247 | Sachbearbeit | 8 | ja |
| 247 | Verantwortlich | 7 | ja |
| 250 | Sachbearbeit | 7 | ja |
| 250 | Verantwortlich | 6 | ja |
| 253 | Sachbearbeit | 7 | ja |
| 253 | Verantwortlich | 6 | ja |
| 258 | Sachbearbeit | 7 | ja |
| 258 | Verantwortlich | 6 | ja |
| 261 | Sachbearbeit | 7 | ja |
| 261 | Verantwortlich | 6 | ja |
| 264 | Sachbearbeit | 7 | ja |
| 264 | Verantwortlich | 6 | ja |
| 269 | Sachbearbeit | 7 | ja |
| 269 | Verantwortlich | 6 | ja |
| 273 | Sachbearbeit | 8 | ja |
| 273 | Verantwortlich | 6 | ja |
| 276 | Sachbearbeit | 7 | ja |
| 276 | Verantwortlich | 6 | ja |
| 280 | Sachbearbeit | 7 | ja |
| 280 | Verantwortlich | 6 | ja |
| 284 | Bürgermeister | 13 | nein |

## Seiten mit Schwärzung

Seiten, deren Belegbild schwarze Rechtecke über Personenfeldern trägt.

| Seite | Rechtecke |
|---|---|
| 72 | 2 |
| 74 | 2 |
| 76 | 2 |
| 79 | 6 |
| 81 | 4 |
| 84 | 4 |
| 88 | 5 |
| 92 | 3 |
| 94 | 4 |
| 96 | 2 |
| 98 | 3 |
| 103 | 6 |
| 105 | 3 |
| 107 | 3 |
| 109 | 3 |
| 113 | 6 |
| 116 | 6 |
| 118 | 5 |
| 120 | 2 |
| 127 | 8 |
| 130 | 4 |
| 132 | 6 |
| 134 | 5 |
| 136 | 5 |
| 138 | 5 |
| 140 | 3 |
| 151 | 2 |
| 155 | 2 |
| 158 | 2 |
| 162 | 2 |
| 165 | 2 |
| 167 | 2 |
| 171 | 2 |
| 174 | 2 |
| 176 | 2 |
| 181 | 4 |
| 183 | 3 |
| 185 | 3 |
| 188 | 2 |
| 190 | 2 |
| 194 | 2 |
| 197 | 4 |
| 200 | 4 |
| 205 | 2 |
| 211 | 5 |
| 215 | 2 |
| 218 | 3 |
| 222 | 2 |
| 224 | 2 |
| 226 | 3 |
| 228 | 6 |
| 232 | 2 |
| 241 | 4 |
| 247 | 4 |
| 250 | 2 |
| 253 | 2 |
| 258 | 4 |
| 261 | 5 |
| 264 | 2 |
| 269 | 3 |
| 273 | 3 |
| 276 | 2 |
| 280 | 4 |
