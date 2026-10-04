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
import shutil
import subprocess
from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal

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


# ---------------------------------------------------------------------------
# Portierung von format.ts (RED: noch nicht implementiert)
# ---------------------------------------------------------------------------


def formatiere_port(wert: int | float, kuerzel: str) -> str:
    raise NotImplementedError


_PORT: dict[str, Callable[[int | float], str]] = {}


def _lies_gerendert(text: str, kuerzel: str) -> Decimal:
    raise NotImplementedError


def _verstoesse(schluessel: str, wert: int | float, kuerzel: str) -> list[str]:
    raise NotImplementedError


def _pruefe_absaetze(absaetze: Sequence[str], werte: Mapping[str, int | float]) -> list[str]:
    raise NotImplementedError


_NODE_SKRIPT = ""


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
    for text in texte_json["texte"]:
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
    kanten: list[tuple[int | float, str]] = [
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
    paare: list[tuple[int | float, str]] = [*beispiele, *kanten]
    for text in texte_json["texte"]:
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
