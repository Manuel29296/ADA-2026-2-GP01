# Manual técnico · Proyecto Oráculo · Grupo G01

Juan Manuel Carmona Villegas · Análisis y Diseño de Algoritmos · Universidad de Caldas · 2026-2

## 1. Entorno

| Elemento | Valor |
|---|---|
| Plataforma | Google Colab con GPU NVIDIA T4 (16 GB) |
| Lenguaje | Python 3.12 (el de Colab) |
| Modelo | `Qwen/Qwen3-1.7B` en fp16 (alias `qwen17b`), modo pensamiento apagado |
| Dependencias | `requirements.txt`: transformers, accelerate, bitsandbytes, nltk, spacy, emoji, langdetect, immutabledict; verificadores de `allenai/open-instruct` |
| Pruebas | Cualquier sistema con Python ≥ 3.10 y `pytest`, sin GPU |

## 2. Arquitectura

```
ADA-2026-2-GP01/
├── busqueda_G01.ipynb        Búsqueda: produce entrega.json y registro_busqueda.csv
├── evaluacion_G01.ipynb      Evaluación de entrega.json sobre datos de prueba
├── entrega.json              Configuración final
├── registro_busqueda.csv     Bitácora de evaluaciones
├── utilidades.py             Validación de entrega.json y lectura de instancias
├── tests/test_utilidades.py  Pruebas sin GPU
├── oraculo.py                (curso) Caja negra: evaluar / validar
├── ayudas.py                 (curso) Cargar modelo y datos, dividir, curva, entrega
├── datos_visibles.json       (curso) 100 búsqueda + 87 validación + 263 descartadas
└── docs/                     Manual técnico e informe
```

| Módulo | Responsabilidad |
|---|---|
| `oraculo.py` | Arma el prompt, genera con el modelo, verifica restricciones y guarda en caché. Se usa sin modificar y sin leerlo para decidir |
| `ayudas.py` | Carga del modelo, lectura y partición de los datos, curva y escritura de `entrega.json` |
| `utilidades.py` | Funciones propias sin GPU: `validar_config`, `cargar_entrega`, `leer_instancias` |
| Notebook de búsqueda | Funciones `medir` y `guardar_registro`, y las fases del algoritmo |
| Notebook de evaluación | Flujo completo de calificación, sin parámetros que editar |

## 3. Funcionamiento

### 3.1 Estructuras de datos

- **Configuración**: diccionario `{"rol": 0..7, "estrategia": 0..7, "formato": 0..7, "estilo": 0..7, "cierre": 0..7, "temperatura": 0.0}`.
- **Instancia**: diccionario con `prompt`, `ids` (familias de restricción), `kwargs` (parámetros de cada verificador), `restriccion` e `id`.
- **Resultado del oráculo**: `precision` (fracción acertada), `trazas` (lista de fallos: `id`, `violo`, `salida`) y `n`.
- **Registro**: lista de filas (número, fase, índices, temperatura, precisión, segundos, tres familias más violadas, nota), exportada a `registro_busqueda.csv`.
- **Caché**: JSON en Google Drive, clave `modelo|huella_config|id_instancia|semilla`. Repetir una consulta cuesta 0 segundos.

### 3.2 Algoritmo de búsqueda

| Fase | Qué hace | Evaluaciones |
|---|---|---|
| 0 · Línea base | Mide el prompt sin instrucciones | 1 |
| 1 · Cribado | Mide cada opción sola (las demás ranuras vacías) | 5 × 8 = 40 |
| Poda por trazas | Descarta una opción si queda más de 2 puntos debajo de la base o si aumenta en 3 o más los fallos de alguna familia; conserva hasta 3 por ranura | 0 (usa lo medido) |
| 2 · Ascenso sobre sobrevivientes | Parte de la mejor opción de cada ranura y cambia una ranura a la vez entre las sobrevivientes | ≤ 3 pasadas |
| 3 · Ascenso sin poda | Desde el mejor punto, prueba las 8 opciones de cada ranura en contexto | ≤ 2 pasadas de 35 |
| Validación | `oraculo.validar` con las 87 instancias de validación | 1 (87 consultas) |

Resultado de la ejecución entregada: cribado 41 evaluaciones (con la base), fase 2 13, fase 3 70; total 124. Configuración final rol 3, estrategia 2, formato 0, estilo 3, cierre 3: 18 % en búsqueda y 21,8 % en validación.

Todas las evaluaciones usan las mismas 100 instancias de búsqueda y la semilla 1, para que las precisiones sean comparables.

### 3.3 Condiciones de parada

- Fase 2: una pasada completa sin mejora estricta, o 3 pasadas.
- Fase 3: una pasada completa sin mejora estricta, o 2 pasadas.
- El resultado es un óptimo local: ninguna configuración que cambie una sola ranura (entre las evaluadas) lo supera. No es un óptimo global demostrado.

## 4. Uso

### 4.1 Notebook de búsqueda

1. Abrir `busqueda_G01.ipynb` en Colab y elegir GPU T4.
2. Celda 1 (instalación) y luego *Entorno de ejecución ▸ Reiniciar sesión*.
3. Celdas 2 (modelo) y 3 (oráculo; autorizar Google Drive).
4. Celdas A a H en orden. Las celdas F (análisis de fallos), G (validación y `entrega.json`) y H (curva de configuraciones completas y validación de la línea base) usan el caché.

Salida: líneas como `# 12 [1-cribado] rol=- estr=2 form=- esti=- cier=- -> 16.0% (191 s) estrategia=2`, que indican el número de evaluación, la fase, la configuración, la precisión sobre 100 instancias, el tiempo y una nota. Al final se generan `entrega.json` y `registro_busqueda.csv`.

### 4.2 Notebook de evaluación

1. Abrir `evaluacion_G01.ipynb` en Colab con GPU T4.
2. *Ejecutar todo*. La primera vez se reinicia solo; volver a usar *Ejecutar todo*.
3. Dejar el archivo de prueba en `/content` o subirlo cuando se pida.

Formato de entrada: igual que `datos_visibles.json` (lista JSON, objeto con una lista o JSONL), con `prompt`, `ids` y `kwargs` por instancia.

Salida: precisión sobre las instancias calificables y sobre el archivo completo, familias más violadas, y los archivos `resultados_evaluacion_G01.json` y `.csv`.

### 4.3 Pruebas

```bash
python -m pytest -q tests
```

Comprueban que `entrega.json` es válido, que se rechazan configuraciones mal formadas y que se leen correctamente archivos JSON, JSONL y los datos del curso.

## 5. Validación y límites

- **Pruebas disponibles**: `tests/test_utilidades.py` (sin GPU) y la validación con `oraculo.validar` en el notebook de búsqueda.
- **Ruido**: con 100 instancias, el error típico de la precisión es de unos 3,8 puntos; diferencias de 1 o 2 puntos no son concluyentes.
- **Trazas parciales**: cada fallo informa solo la primera restricción violada.
- **Costo**: unos 3,2 minutos por evaluación; la cuota gratuita de GPU de Colab puede agotarse tras varias horas de uso.
- **Dependencia del modelo**: la configuración se buscó con `qwen17b`; con otro modelo puede rendir distinto.
- **Datos privados**: el equipo no tiene acceso al conjunto de prueba de la profesora, que puede contener familias de restricciones nuevas.
- **Pendiente para siguientes entregas**: algoritmo exacto con su T(n) deducido (semanas 5–6), heurísticas adicionales y validación experimental de tiempos.
