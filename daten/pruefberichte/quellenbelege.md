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
| inv (Investitionsmaßnahmen) | 137 | 0 |
| ve (VE-Fälligkeiten) | 6 | 0 |
| sd (Schuldenstand) | 3 | 1 |
| sp (Stellenplan) | 123 | 4 |

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
