"""Python-Portierung von `app/src/charts/format.ts::formatiere` für CR-01.

Die Pipeline formatiert nie (D-15) — dieser Port lebt ausschließlich hier in den
Tests, damit kein formatierter String nach `daten/` oder `app/src/data/` gelangt.
Er rendert jedes Rohwert/Formatkürzel-Paar aus `erklaerungen.md` und `texte.json`
mechanisch nach, damit eine Regression wie CR-01 (gruppiertes Haushaltsjahr) nicht
unbemerkt bleibt, und wird dort, wo Node und `app/node_modules/typescript`
verfügbar sind, gegen die echte `formatiere()` gegengeprüft.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from collections.abc import Callable, Mapping, Sequence
from decimal import ROUND_HALF_UP, Decimal

import pytest

from ostbevern.konfiguration import PROJEKT_WURZEL
from ostbevern.schema import DATEN_WURZEL, ERKLAERUNGEN_MD
from ostbevern.texte import (
    FORMATKUERZEL,
    PLATZHALTER_MUSTER,
    lies_erklaerungen,
    loese_auf,
    textwerte,
)

APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"

_NBSP = "\u00a0"

# Spiegel von `KEIN_WERT` in format.ts: sichtbarer Ersatz f\u00fcr fehlende Zahlenwerte.
_KEIN_WERT = "\u2013"


# ---------------------------------------------------------------------------
# Portierung von format.ts (GREEN)
# ---------------------------------------------------------------------------

_JAHR_MUSTER = re.compile(r"^(19|20)\d{2}$")


def _zu_decimal(wert: int | float | Decimal) -> Decimal:
    """Wandelt einen Rohwert in ein Decimal, ohne Float-Binärrauschen einzuführen.

    `float -> Decimal(repr(wert))` nutzt die kürzeste rundtrip-fähige Dezimaldarstellung
    (dieselbe, die auch JS' `Number.prototype.toString()` für denselben Double-Wert
    liefert), damit die Portierung dieselbe Dezimalkette rundet wie ICU in format.ts.
    """
    if isinstance(wert, Decimal):
        return wert
    if isinstance(wert, bool):
        raise TypeError(f"bool ist kein gültiger Zahlenwert: {wert!r}")
    if isinstance(wert, int):
        return Decimal(wert)
    if isinstance(wert, float):
        return Decimal(repr(wert))
    raise TypeError(f"Unerwarteter Typ für Zahlenwert: {type(wert)!r}")


def _gruppiere(ziffern: str) -> str:
    """Gruppiert eine Ziffernfolge in Dreiergruppen von rechts, getrennt durch '.'."""
    gruppen: list[str] = []
    rest = ziffern
    while len(rest) > 3:
        gruppen.insert(0, rest[-3:])
        rest = rest[:-3]
    gruppen.insert(0, rest)
    return ".".join(gruppen)


def _dezimal(
    wert: int | float | Decimal,
    *,
    max_nachkommastellen: int | None = None,
    max_signifikante_stellen: int | None = None,
    gruppieren: bool = True,
) -> str:
    """Portiert `new Intl.NumberFormat('de-DE', optionen).format(wert)` für exakt die
    Options-Kombinationen, die format.ts verwendet (maximumFractionDigits XOR
    maximumSignificantDigits, dezimal ',', Tausendertrennzeichen '.', Rundung
    ROUND_HALF_UP wie Intl 'halfExpand')."""
    roh = _zu_decimal(wert)
    negativ = roh.is_signed()  # erfasst auch "-0" (Intl zeigt "-0", nie "0")
    betrag = roh.copy_abs()

    if max_signifikante_stellen is not None:
        if betrag != 0:
            exponent = betrag.adjusted() - max_signifikante_stellen + 1
            quantum = Decimal(1).scaleb(exponent)
            betrag = betrag.quantize(quantum, rounding=ROUND_HALF_UP)
    elif max_nachkommastellen is not None:
        quantum = Decimal(1).scaleb(-max_nachkommastellen)
        betrag = betrag.quantize(quantum, rounding=ROUND_HALF_UP)

    text = format(betrag, "f")
    if "." in text:
        ganzzahl, nachkomma = text.split(".", 1)
        nachkomma = nachkomma.rstrip("0")
    else:
        ganzzahl, nachkomma = text, ""

    if gruppieren:
        ganzzahl = _gruppiere(ganzzahl)

    ergebnis = ganzzahl + ("," + nachkomma if nachkomma else "")
    return ("-" if negativ else "") + ergebnis


def _euro(wert: int | float) -> str:
    return _dezimal(wert, max_nachkommastellen=0) + _NBSP + "€"


def _euro_kurz(wert: int | float) -> str:
    if abs(_zu_decimal(wert)) >= 1_000_000:
        skaliert = wert / 1_000_000
        return _dezimal(skaliert, max_signifikante_stellen=3) + " Mio. €"
    return _euro(wert)


def _zahl(wert: int | float) -> str:
    return _dezimal(wert, max_nachkommastellen=0, gruppieren=True)


def _jahr(wert: int | float) -> str:
    return _dezimal(wert, max_nachkommastellen=0, gruppieren=False)


def _vzae(wert: int | float) -> str:
    return _dezimal(wert, max_nachkommastellen=2, gruppieren=True)


def _prozent(anteil: int | float) -> str:
    wert = Decimal(repr(float(anteil))) * 100
    return _dezimal(wert, max_nachkommastellen=1, gruppieren=True) + _NBSP + "%"


# In FORMATKUERZEL-Reihenfolge (test_port_deckt_alle_formatkuerzel_ab).
_PORT: dict[str, Callable[[int | float], str]] = {
    "euro": _euro,
    "mio": _euro_kurz,
    "zahl": _zahl,
    "jahr": _jahr,
    "prozent": lambda w: _prozent(w / 100),
    "promille": lambda w: _prozent(w / 1000),
    "vzae": _vzae,
}


def formatiere_port(wert: int | float | None, kuerzel: str) -> str:
    """Portierte Entsprechung von `app/src/charts/format.ts::formatiere` (CR-01).

    Wie die App: fehlende oder nicht endliche Werte (None, NaN, ±inf) ergeben den
    sichtbaren Fallback `KEIN_WERT`, ein unbekanntes Formatkürzel einen Fehler (WR-06).
    """
    if wert is None or (isinstance(wert, float) and not math.isfinite(wert)):
        return _KEIN_WERT
    if kuerzel not in _PORT:
        raise ValueError(f"Unbekanntes Formatkürzel: {kuerzel}")
    return _PORT[kuerzel](wert)


def _lies_gerendert(text: str, kuerzel: str) -> Decimal:
    """Parst einen gerenderten String zurück in ein Decimal für den Rundtrip-Vergleich.

    Für `mio` ist der Maßstab 1_000_000, wenn die " Mio. €"-Form gewählt wurde (sonst
    fällt euroKurz() auf euro() zurück und es gilt derselbe Maßstab 1 wie bei `euro`).
    """
    rest = text
    skala = Decimal(1)
    if rest.endswith(" Mio. €"):
        rest = rest[: -len(" Mio. €")]
        skala = Decimal(1_000_000)
    elif rest.endswith(_NBSP + "€"):
        rest = rest[: -len(_NBSP + "€")]
    elif rest.endswith(_NBSP + "%"):
        rest = rest[: -len(_NBSP + "%")]
    rest = rest.replace(".", "").replace(",", ".")
    return Decimal(rest) * skala


def _rundung_halb_aufwaerts(wert: int | float) -> Decimal:
    """Rundet `wert` kaufmännisch (ROUND_HALF_UP) auf eine Ganzzahl, Vorzeichen erhalten."""
    roh = _zu_decimal(wert)
    negativ = roh.is_signed()
    betrag = roh.copy_abs().quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return -betrag if negativ else betrag


# Abgeleitete Formeln, deren Ergebnis ein Kalenderjahr ist (Plan 06-04, D-14). Sie liegen im
# Namensraum "abgeleitet." und gehören trotzdem mit dem Kürzel "jahr" formatiert, sonst
# erschiene "2.026". Andere Formeln mit der Endung "_jahr" (..._letztes_jahr) liefern Beträge.
_JAHRWERTIGE_ABGELEITETE = frozenset({"abgeleitet.ausgleichsruecklage_aufgebraucht_jahr"})


def _verstoesse(schluessel: str, wert: int | float | None, kuerzel: str) -> list[str]:
    """Prüft ein (Rohwert, Formatkürzel)-Paar gegen die CR-01-/Rundtrip-Regeln (D-15).

    (a) ein Schlüssel im Namensraum "jahr." mit einem anderen Kürzel als "jahr" (CR-01);
    (b) Kürzel "jahr", dessen Rendering keine vierstellige Jahreszahl ist oder vom
        Rohwert abweicht; dasselbe Kürzel außerhalb des "jahr."-Namensraums (Ausnahme: abgeleitete
        Formeln, die ein Jahr liefern, siehe _JAHRWERTIGE_ABGELEITETE);
    (c) kein Rundtrip auf den Rohwert innerhalb der kürzel-eigenen Genauigkeit;
    (d) eine leere Darstellung oder eine, die "undefined", "NaN" oder "Infinity" enthält.
    """
    verstoesse: list[str] = []
    gerendert = formatiere_port(wert, kuerzel)

    if gerendert == _KEIN_WERT:
        # Ein Rohwert aus den echten Daten darf nie auf den Fallback laufen, sonst
        # zeigte ein Text statt einer Zahl einen Gedankenstrich (UI-05).
        verstoesse.append(
            f"{schluessel}|{kuerzel}: fehlender oder nicht endlicher Rohwert {wert!r}"
        )
        return verstoesse

    if gerendert == "" or "undefined" in gerendert or "NaN" in gerendert or "Infinity" in gerendert:
        verstoesse.append(
            f"{schluessel}|{kuerzel}: ungültige Darstellung {gerendert!r} für Rohwert {wert!r}"
        )
        return verstoesse

    ist_jahresnamensraum = (
        schluessel == "jahr"
        or schluessel.startswith("jahr.")
        or schluessel in _JAHRWERTIGE_ABGELEITETE
    )
    if ist_jahresnamensraum and kuerzel != "jahr":
        verstoesse.append(
            f"{schluessel}|{kuerzel}: Jahresschlüssel ohne Formatkürzel 'jahr' "
            f"(gerendert {gerendert!r})"
        )
    if kuerzel == "jahr" and not ist_jahresnamensraum:
        verstoesse.append(
            f"{schluessel}|{kuerzel}: Formatkürzel 'jahr' außerhalb des 'jahr.'-Namensraums "
            f"(gerendert {gerendert!r})"
        )

    if kuerzel == "jahr":
        if not _JAHR_MUSTER.fullmatch(gerendert) or Decimal(gerendert) != _zu_decimal(wert):
            verstoesse.append(
                f"{schluessel}|{kuerzel}: {gerendert!r} ist keine vierstellige Jahreszahl "
                f"oder weicht vom Rohwert {wert!r} ab"
            )
        return verstoesse

    geparst = _lies_gerendert(gerendert, kuerzel)
    if kuerzel in ("euro", "zahl"):
        erwartet = _rundung_halb_aufwaerts(wert)
        if geparst != erwartet:
            verstoesse.append(
                f"{schluessel}|{kuerzel}: {gerendert!r} rundet nicht auf den Rohwert {wert!r} "
                f"(erwartet {erwartet})"
            )
    elif kuerzel == "mio":
        roh_abs = abs(_zu_decimal(wert))
        if roh_abs >= 1_000_000:
            toleranz = roh_abs * Decimal("0.005")
            if abs(geparst - _zu_decimal(wert)) > toleranz:
                verstoesse.append(
                    f"{schluessel}|{kuerzel}: {gerendert!r} weicht mehr als 0,5% von {wert!r} ab"
                )
        else:
            erwartet = _rundung_halb_aufwaerts(wert)
            if geparst != erwartet:
                verstoesse.append(
                    f"{schluessel}|{kuerzel}: {gerendert!r} rundet nicht auf den Rohwert "
                    f"{wert!r} (erwartet {erwartet})"
                )
    elif kuerzel == "prozent":
        if abs(geparst - _zu_decimal(wert)) > Decimal("0.05"):
            verstoesse.append(
                f"{schluessel}|{kuerzel}: {gerendert!r} weicht mehr als 0,05 von {wert!r} ab"
            )
    elif kuerzel == "promille":
        if abs(geparst * 10 - _zu_decimal(wert)) > Decimal("0.5"):
            verstoesse.append(
                f"{schluessel}|{kuerzel}: {gerendert!r} (×10) weicht mehr als 0,5 von {wert!r} ab"
            )
    elif kuerzel == "vzae":
        if abs(geparst - _zu_decimal(wert)) > Decimal("0.005"):
            verstoesse.append(
                f"{schluessel}|{kuerzel}: {gerendert!r} weicht mehr als 0,005 von {wert!r} ab"
            )

    return verstoesse


def _pruefe_absaetze(absaetze: Sequence[str], werte: Mapping[str, int | float]) -> list[str]:
    """Rendert jeden Platzhalter jedes Absatzes über `formatiere_port` und sammelt
    `_verstoesse` je Vorkommen; meldet zusätzlich einen Absatz, dessen Rendering noch
    "{{" oder "}}" enthält (unaufgelöster Platzhalter)."""
    verstoesse: list[str] = []

    def _ersetze(treffer: re.Match[str]) -> str:
        schluessel, format_kuerzel = treffer.groups()
        wert = werte[schluessel]
        for eintrag in _verstoesse(schluessel, wert, format_kuerzel):
            verstoesse.append(f"{treffer.group(0)}: {eintrag}")
        return formatiere_port(wert, format_kuerzel)

    for absatz in absaetze:
        gerendert = PLATZHALTER_MUSTER.sub(_ersetze, absatz)
        if "{{" in gerendert or "}}" in gerendert:
            verstoesse.append(f"Unaufgelöster Platzhalter im gerenderten Absatz: {absatz!r}")

    return verstoesse


# Node-Teilskript (D-15, test_port_wie_format_ts): transpiliert format.ts mit dem
# App-eigenen typescript-devDependency (keine neue Abhängigkeit), importiert das
# Ergebnis über eine base64-data:-URL und rendert die über stdin übergebenen Paare
# mit der echten formatiere(). Kein Shell-Aufruf (Argumentliste), keine Netzwerknutzung.
_NODE_SKRIPT = (
    'import {createRequire} from "node:module";'
    'import {readFileSync} from "node:fs";'
    "const wurzel=process.argv[1];"
    'const ts=createRequire(wurzel+"/package.json")("typescript");'
    "const quelle=readFileSync(wurzel+\"/src/charts/format.ts\",'utf8');"
    "const js=ts.transpileModule(quelle,"
    "{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;"
    'const modul=await import("data:text/javascript;base64,"+Buffer.from(js).toString("base64"));'
    'const paare=JSON.parse(readFileSync(0,"utf8"));'
    "const ergebnisse=paare.map(([w,k])=>modul.formatiere(w,k));"
    "console.log(JSON.stringify(ergebnisse));"
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app_daten() -> tuple[dict, dict, list[dict]]:
    haushalt = json.loads((APP_DATEN_WURZEL / "haushalt.json").read_text(encoding="utf-8"))
    investitionen = json.loads(
        (APP_DATEN_WURZEL / "investitionen.json").read_text(encoding="utf-8")
    )
    produkte = json.loads((APP_DATEN_WURZEL / "produkte.json").read_text(encoding="utf-8"))
    return haushalt, investitionen, produkte


@pytest.fixture(scope="module")
def werte(app_daten: tuple[dict, dict, list[dict]]) -> dict[str, int | float]:
    haushalt, investitionen, produkte = app_daten
    return textwerte(haushalt, investitionen, produkte)


@pytest.fixture(scope="module")
def echte_erklaerungen() -> list:
    return lies_erklaerungen(DATEN_WURZEL / ERKLAERUNGEN_MD)


@pytest.fixture(scope="module")
def texte_json() -> dict:
    return json.loads((APP_DATEN_WURZEL / "texte.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_port_deckt_alle_formatkuerzel_ab() -> None:
    assert tuple(_PORT) == FORMATKUERZEL


@pytest.mark.parametrize(
    ("wert", "kuerzel", "erwartet"),
    [
        (1999, "jahr", "1999"),
        (1999, "zahl", "1.999"),
        (12345, "zahl", "12.345"),
        (1234567, "euro", "1.234.567" + _NBSP + "€"),
        (-1234567, "euro", "-1.234.567" + _NBSP + "€"),
        (1234567, "mio", "1,23 Mio. €"),
        (1995000, "mio", "2 Mio. €"),
        (987654, "mio", "987.654" + _NBSP + "€"),
        (450, "prozent", "450" + _NBSP + "%"),
        (125, "promille", "12,5" + _NBSP + "%"),
        (12.75, "vzae", "12,75"),
    ],
)
def test_port_beispiele(wert: int | float, kuerzel: str, erwartet: str) -> None:
    assert formatiere_port(wert, kuerzel) == erwartet


@pytest.mark.parametrize(
    ("wert", "kuerzel"),
    [
        (None, "euro"),
        (None, "mio"),
        (float("nan"), "zahl"),
        (float("inf"), "jahr"),
        (float("-inf"), "prozent"),
    ],
)
def test_port_fallback_fuer_fehlende_werte(wert: float | None, kuerzel: str) -> None:
    assert formatiere_port(wert, kuerzel) == "–"


def test_port_unbekanntes_kuerzel_wirft_value_error() -> None:
    with pytest.raises(ValueError, match="unbekannt"):
        formatiere_port(1, "unbekannt")


def test_verstoesse_meldet_fehlenden_rohwert() -> None:
    assert _verstoesse("meta.einwohner", None, "zahl")
    assert _verstoesse("meta.einwohner", float("nan"), "zahl")


def test_erklaerungen_rendern_korrekt(
    echte_erklaerungen: list, werte: dict[str, int | float]
) -> None:
    verstoesse: list[str] = []
    aufgeloest = loese_auf(echte_erklaerungen, werte)
    for schluessel, (wert, kuerzel) in aufgeloest.items():
        verstoesse.extend(_verstoesse(schluessel, wert, kuerzel))
    for text in echte_erklaerungen:
        verstoesse.extend(_pruefe_absaetze(text.absaetze, werte))
    assert not verstoesse, "\n".join(verstoesse)


def test_texte_json_rendert_korrekt(texte_json: dict) -> None:
    verstoesse: list[str] = []
    texte_werte = texte_json["werte"]
    for text in [*texte_json["texte"], *texte_json["glossar"]]:
        verstoesse.extend(_pruefe_absaetze(text["absaetze"], texte_werte))
    assert not verstoesse, "\n".join(verstoesse)


def test_cr01_gruppiertes_haushaltsjahr_wird_erkannt(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    haushalt, _investitionen, _produkte = app_daten
    haushaltsjahr = haushalt["haushaltsjahr"]
    assert _verstoesse("jahr.haushaltsjahr", haushaltsjahr, "zahl")
    assert not _verstoesse("jahr.haushaltsjahr", haushaltsjahr, "jahr")
    einwohner = werte["meta.einwohner"]
    assert _verstoesse("meta.einwohner", einwohner, "jahr")
    verstoesse = _pruefe_absaetze(
        ("Im Jahr {{jahr.haushaltsjahr|zahl}}.",), {"jahr.haushaltsjahr": haushaltsjahr}
    )
    assert verstoesse


def test_port_wie_format_ts(werte: dict[str, int | float], texte_json: dict) -> None:
    node = shutil.which("node")
    app_wurzel = PROJEKT_WURZEL / "app"
    typescript_paket = app_wurzel / "node_modules" / "typescript" / "package.json"
    if node is None:
        pytest.skip("node ist nicht im PATH verfügbar")
    if not typescript_paket.is_file():
        pytest.skip(f"{typescript_paket} fehlt (app/node_modules/typescript)")

    beispiele: list[tuple[int | float, str]] = [
        (1999, "jahr"),
        (1999, "zahl"),
        (12345, "zahl"),
        (1234567, "euro"),
        (-1234567, "euro"),
        (1234567, "mio"),
        (1995000, "mio"),
        (987654, "mio"),
        (450, "prozent"),
        (125, "promille"),
        (12.75, "vzae"),
    ]
    kanten: list[tuple[int | float | None, str]] = [
        (None, "euro"),
        (None, "mio"),
        (1005000, "mio"),
        (9995000, "mio"),
        (999500, "mio"),
        (-1500000, "mio"),
        (-0.4, "zahl"),
        (-0.4, "euro"),
        (12.345, "vzae"),
        (1554, "prozent"),
        (-3, "promille"),
    ]
    paare: list[tuple[int | float | None, str]] = [*beispiele, *kanten]
    for text in [*texte_json["texte"], *texte_json["glossar"]]:
        for absatz in text["absaetze"]:
            for schluessel, format_kuerzel in PLATZHALTER_MUSTER.findall(absatz):
                paare.append((texte_json["werte"][schluessel], format_kuerzel))

    ergebnis = subprocess.run(
        ["node", "--input-type=module", "-e", _NODE_SKRIPT, str(app_wurzel)],
        input=json.dumps(paare),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=120,
    )
    if ergebnis.returncode != 0:
        pytest.fail(f"node-Teilprozess fehlgeschlagen: {ergebnis.stderr}")

    echte = json.loads(ergebnis.stdout)
    abweichungen: list[str] = []
    for (wert, kuerzel), echter_wert in zip(paare, echte, strict=True):
        port_wert = formatiere_port(wert, kuerzel)
        if port_wert != echter_wert:
            abweichungen.append(f"{wert!r}|{kuerzel}: port={port_wert!r} real={echter_wert!r}")
    assert not abweichungen, "\n".join(abweichungen)
