"""Pruebas sin GPU:  python -m pytest -q tests"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utilidades import RANURAS, cargar_entrega, leer_instancias, validar_config  # noqa: E402

RAIZ = os.path.join(os.path.dirname(__file__), "..")


def test_entrega_del_repositorio_es_valida():
    """El entrega.json real cumple el formato del curso."""
    grupo, semana, config = cargar_entrega(os.path.join(RAIZ, "entrega.json"))
    assert grupo == "G01"
    assert semana >= 1
    assert set(config) == set(RANURAS) | {"temperatura"}
    assert all(0 <= config[s] <= 7 for s in RANURAS)


@pytest.mark.parametrize("malo", [
    {"rol": 8, "estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.0},
    {"rol": -1, "estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.0},
    {"rol": "3", "estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.0},
    {"estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.0},
    {"rol": 0, "estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.5},
    {"rol": 0, "estrategia": 0, "formato": 0, "estilo": 0, "cierre": 0, "temperatura": 0.0, "extra": 1},
])
def test_config_invalida_se_rechaza(malo):
    with pytest.raises(ValueError):
        validar_config(malo)


def test_config_valida_se_normaliza():
    c = validar_config({"rol": 1, "estrategia": 2, "formato": 3, "estilo": 4, "cierre": 5, "temperatura": 0})
    assert c["temperatura"] == 0.0 and isinstance(c["temperatura"], float)


def _inst(i, split=None):
    x = {"prompt": f"p{i}", "ids": ["a:b"], "kwargs": [{}], "id": i}
    if split:
        x["split"] = split
    return x


def test_lee_json_y_quita_descartadas(tmp_path):
    ruta = tmp_path / "d.json"
    ruta.write_text(json.dumps([_inst(1), _inst(2, "descartada"), _inst(3, "validacion")]))
    assert [x["id"] for x in leer_instancias(str(ruta))] == [1, 3]


def test_lee_jsonl(tmp_path):
    ruta = tmp_path / "d.jsonl"
    ruta.write_text("\n".join(json.dumps(_inst(i)) for i in range(3)))
    assert len(leer_instancias(str(ruta))) == 3


def test_lee_objeto_con_lista(tmp_path):
    ruta = tmp_path / "d.json"
    ruta.write_text(json.dumps({"instancias": [_inst(1)]}))
    assert len(leer_instancias(str(ruta))) == 1


def test_rechaza_instancia_incompleta(tmp_path):
    ruta = tmp_path / "d.json"
    ruta.write_text(json.dumps([{"prompt": "x"}]))
    with pytest.raises(ValueError):
        leer_instancias(str(ruta))


def test_datos_visibles_del_curso_se_leen(tmp_path):
    """Los datos del curso pasan la lectura: 187 instancias (100 + 87)."""
    ruta = os.path.join(RAIZ, "datos_visibles.json")
    if not os.path.exists(ruta):
        pytest.skip("datos_visibles.json no está junto a las pruebas")
    assert len(leer_instancias(ruta)) == 187
