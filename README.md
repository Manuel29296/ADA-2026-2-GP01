# Proyecto Oráculo · Grupo G01

**Análisis y Diseño de Algoritmos · Ingeniería de Sistemas y Computación · Universidad de Caldas · 2026-2**

| | |
|---|---|
| Integrante | Juan Manuel Carmona Villegas |
| Grupo / subproyecto | G01 · Proyecto Oráculo (búsqueda de configuración de prompt) |
| Entrega | Primera entrega (semanas 1–4): formalización, NP-dureza y solución base |
| Versión entregada | rama `main` |
| Repositorio base | Fork de [JuManoel/ADA-2026-2-GP01](https://github.com/JuManoel/ADA-2026-2-GP01) |

## El problema

Elegir un índice (0–7) para cada una de las cinco ranuras del prompt (`rol`, `estrategia`, `formato`, `estilo`, `cierre`) y una temperatura, para que el modelo Qwen3-1.7B cumpla el mayor número posible de restricciones verificables. Hay 8⁵ = 32 768 configuraciones y evaluar una sobre las 100 instancias de búsqueda tarda unos 3,2 minutos en una GPU T4: probarlas todas tomaría unos 73 días. La solución base encuentra una buena configuración evaluando 124 (0,38 % del espacio).

## Resultado

| | |
|---|---|
| Configuración (`entrega.json`) | `rol 3 · estrategia 2 · formato 0 · estilo 3 · cierre 3 · temperatura 0.0` |
| Precisión en búsqueda (100 instancias) | **18 %** (sin instrucciones: 16 %) |
| Precisión en validación (`oraculo.validar`, 87 instancias) | **21,8 %** (sin instrucciones: 17,2 %) |
| Evaluaciones usadas | 124 de 32 768 posibles (0,38 %) |
| Garantía | Mejor configuración encontrada (óptimo local respecto a cambiar una ranura). **No** es un óptimo global demostrado |

La nota final no sale de estos números: la profesora evalúa `entrega.json` sobre un conjunto de prueba privado con `evaluacion_G01.ipynb`.

## Archivos

| Archivo | Qué es |
|---|---|
| `busqueda_G01.ipynb` | **Notebook de búsqueda**: línea base, cribado, poda por trazas, ascenso por coordenadas, análisis de fallos y validación |
| `evaluacion_G01.ipynb` | **Notebook de evaluación**: carga `entrega.json` y la evalúa sobre los datos de prueba, sin editar nada |
| `entrega.json` | Configuración final (grupo, configuración, semana) |
| `registro_busqueda.csv` | Todas las configuraciones evaluadas con su precisión y las reglas que más fallaron |
| `utilidades.py` | Validación de `entrega.json` y lectura de datos de prueba (sin GPU) |
| `tests/test_utilidades.py` | Pruebas sencillas sin GPU |
| `requirements.txt` | Dependencias |
| `docs/MANUAL_TECNICO.md` | Manual técnico |
| `docs/Informe_Primera_Entrega_G01.pdf` | Informe académico (formalización y NP-dureza) |
| `oraculo.py`, `ayudas.py`, `datos_visibles.json`, `proyecto_oraculo.ipynb` | Archivos del curso, sin modificar |

## Cómo ejecutar

**Notebook de búsqueda** (Google Colab, GPU T4): abrir `busqueda_G01.ipynb` en Colab, elegir *Entorno de ejecución ▸ Cambiar tipo ▸ T4 GPU*, correr la celda 1, reiniciar el entorno y correr las demás en orden. El caché se guarda en Google Drive.

**Notebook de evaluación** (Google Colab, GPU T4): abrir `evaluacion_G01.ipynb` y usar *Ejecutar todo* (dos veces la primera vez, porque se reinicia solo tras instalar). Toma los datos de prueba de `/content` o pide subirlos; sin datos, corre en modo demostración con las 87 instancias de validación.

**Pruebas** (cualquier computador con Python 3.10+, sin GPU):

```bash
pip install pytest
python -m pytest -q tests
```

Resultado esperado: todas las pruebas pasan.

## Versiones

Python 3.12 (Colab) · modelo `Qwen/Qwen3-1.7B` (alias `qwen17b`) · temperatura 0.0 · semilla 1.
