"""utilidades.py — Grupo G01 · Proyecto Oráculo.

Funciones sin GPU que usan el notebook de evaluación y las pruebas:

    cargar_entrega(ruta)    -> (grupo, semana, config)   valida entrega.json
    leer_instancias(ruta)   -> lista de instancias        lee JSON o JSONL
"""

import json

RANURAS = ["rol", "estrategia", "formato", "estilo", "cierre"]
OPCIONES = range(8)                      # índices válidos por ranura: 0..7
TEMPERATURAS = (0.0, 0.3, 0.7)           # las que acepta el curso
CAMPOS_INSTANCIA = ("prompt", "ids", "kwargs")


def validar_config(config):
    """Revisa que la config tenga un índice entero 0..7 por ranura y una
    temperatura aceptada. Devuelve una copia limpia (ints y float)."""
    if not isinstance(config, dict):
        raise ValueError("la config debe ser un objeto JSON")
    limpia = {}
    for s in RANURAS:
        v = config.get(s)
        if isinstance(v, bool) or not isinstance(v, int) or v not in OPCIONES:
            raise ValueError(f"'{s}' debe ser un entero entre 0 y 7 (llegó {v!r})")
        limpia[s] = v
    t = config.get("temperatura")
    if isinstance(t, bool) or not isinstance(t, (int, float)) or float(t) not in TEMPERATURAS:
        raise ValueError(f"'temperatura' debe ser una de {TEMPERATURAS} (llegó {t!r})")
    limpia["temperatura"] = float(t)
    sobran = set(config) - set(RANURAS) - {"temperatura"}
    if sobran:
        raise ValueError(f"claves desconocidas en la config: {sorted(sobran)}")
    return limpia


def cargar_entrega(ruta="entrega.json"):
    """Lee entrega.json y valida grupo, semana y config."""
    with open(ruta, encoding="utf-8") as f:
        d = json.load(f)
    grupo = d.get("grupo")
    if not isinstance(grupo, str) or not grupo:
        raise ValueError("'grupo' debe ser un texto, p. ej. 'G01'")
    semana = d.get("semana")
    if isinstance(semana, bool) or not isinstance(semana, int) or semana < 1:
        raise ValueError("'semana' debe ser un entero positivo")
    return grupo, semana, validar_config(d.get("config"))


def leer_instancias(ruta):
    """Lee instancias desde JSON (lista, o objeto con una lista dentro) o JSONL.

    Quita las marcadas split='descartada', exige prompt/ids/kwargs y asigna
    un id a las que no traen uno.
    """
    with open(ruta, encoding="utf-8") as f:
        texto = f.read().strip()
    if not texto:
        raise ValueError(f"{ruta} está vacío")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError:
        datos = [json.loads(linea) for linea in texto.splitlines() if linea.strip()]
    if isinstance(datos, dict):
        listas = [v for v in datos.values() if isinstance(v, list)]
        if len(listas) != 1:
            raise ValueError("el JSON es un objeto sin una única lista de instancias")
        datos = listas[0]
    if not isinstance(datos, list):
        raise ValueError("no se encontró una lista de instancias")

    instancias = []
    for k, x in enumerate(datos):
        if not isinstance(x, dict):
            raise ValueError(f"la instancia {k} no es un objeto JSON")
        if x.get("split") == "descartada":
            continue
        faltan = [c for c in CAMPOS_INSTANCIA if c not in x]
        if faltan:
            raise ValueError(f"a la instancia {k} le faltan los campos {faltan}")
        if len(x["ids"]) != len(x["kwargs"]):
            raise ValueError(f"la instancia {k} trae distinto número de ids y kwargs")
        x = dict(x)
        x.setdefault("id", f"inst-{k}")
        x.setdefault("restriccion", "")
        instancias.append(x)
    if not instancias:
        raise ValueError("el archivo no trae instancias evaluables")
    return instancias
