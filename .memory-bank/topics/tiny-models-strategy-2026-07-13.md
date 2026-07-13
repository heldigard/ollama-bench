# Tiny Models Strategy (0.3B–2B) — análisis + instrucciones de ejecución
> 2026-07-13. Pregunta del usuario: ¿modelos diminutos (gemma-4 ~2B, LFM ~1B)
> pueden complementar a los campeones actuales y ahorrar más tokens de los CLI
> sin sacrificar calidad/precisión/razonamiento?
> Documento escrito para que OTRO modelo lo ejecute. Autocontenido.

## TL;DR (respuesta corta)

**Estado 2026-07-13 - cerrado por evidencia:** el slice `classification` se
implementó y se ejecutó con 48 casos bilingües. LFM2.5-1.2B, qwen3:0.6b y
gemma3:1b obtuvieron `REJECT`; LFM fue 4.14x más rápido pero macro-F1 0.3527
frente a baseline 0.9185. No se cableó ningún tiny. Resultado y screen de E2B:
`topics/candidates-round-15-2026-07-13.md`.

**Corrección E2B:** `batiai/gemma4-e2b:q4` se anuncia como E2B, pero Ollama lo
reporta como 4.6B. No es evidencia para la hipótesis tiny de classification.
En cambio, obtuvo una señal inicial en `smart_trim` (11.67), pero una única
ronda no basta para validar fidelidad. Permanece candidato sin rewire; el
throughput no es un criterio de promoción.

**Sí, pero NO en los roles actuales.** Los 9 roles PRIMARY cableados (improve,
smart_trim, web_synth, codeq_sum, bug_finding, tool_call, pdf_extract, ocr,
browser) son roles de CALIDAD: un 1–2B pierde contra los campeones 4–12B y el
lineup está en TERMINAL STABILITY (round-11/12 = zero rewires). No re-benchear
esos roles con tinys — pérdida de tiempo garantizada.

El valor real de un tiny está en una **capa nueva que hoy no existe**: roles de
ALTA FRECUENCIA y BAJA COMPLEJIDAD donde hoy se dispara cryptidbleh (3.4GB) o
ni siquiera hay modelo (heurísticas/regex). Ahí un 1–2B residente en VRAM
(keep-alive permanente, sin latencia de carga) puede responder en <1s y
**escalar solo cuando falla** — patrón cascada. Eso ahorra: (a) tokens CLI que
hoy se gastan porque el paso local es lento y se omite, (b) segundos de carga
de modelo en cada hook de alta frecuencia.

## Contexto verificado (no re-derivar)

- Lineup: 19 LLM + 3 embeddings = 22 modelos, RTX 5080 16GB, Ollama 0.31.2.
  Fuente: `topics/local-ollama-lineup.md` (round-12 terminal).
- `batiai/gemma4-e2b:q4` YA está en el lineup (fallback codeq_sum). "e2b" =
  effective-2B. O sea: la clase ~2B ya compite y quedó como fallback, no
  primary. Lo NUEVO sería la clase sub-2GB (gemma-4 1B/2B-it QAT, LFM 1B,
  qwen tiny 0.6B) como capa residente, no como reemplazo de campeones.
- LFM: familia con think-leak conocido (hard-DQ histórico). El modo
  `deep --strip` + tag `strippable=1` en smoke lo desbloquea — obligatorio
  benchear LFM con `--strip`. Fuente: `topics/bench-methodology.md`.
- Roadmap P0 pendiente: `classification` y `rerank` NO están implementados
  (tool_call y embedding_retrieval sí aterrizaron). Fuente:
  `topics/new-benchmarks-roadmap-2026-07-04.md`.
- prompt-router corre clasificación en CADA prompt (41 rutas) y hoy no tiene
  bench coverage. Es el rol local que más se dispara en todo el harness.

## Dónde SÍ encaja un tiny (roles candidatos, en orden de valor)

| # | Rol nuevo | Consumidor real | Por qué tiny | Scoring |
|---|---|---|---|---|
| 1 | `classification` | task routing; caveman outcome compatibility | Tarea corta, cerrada y multi-clase. El rendimiento y la velocidad de un tiny son hipótesis que debe probar el bench, no hechos asumidos. | macro-F1 + exact-match, 48 casos bilingües (determinista, sin LLM-judge) |
| 2 | `rerank` | web-research `--smart`, search-swarm, memory semsearch | Listwise top-3 de 10 candidatos: input corto, output corto. | nDCG@3 vs gold |
| 3 | `focused_extract` | extract-tool-output.py (logs >25K), web-research per-page extract | Extracción query-scoped de líneas relevantes. Hoy lo hace cryptidbleh 3.4GB. | precision/recall a nivel línea vs gold |
| 4 | `escalation_gate` (nuevo concepto) | cascada tiny→campeón→CLI | El tiny decide "¿puedo yo o escalo?". Ahorro de tokens compuesto: cada acierto del tiny evita cargar un 12B o gastar tokens cloud. | calibración: accuracy de la decisión escalar/no-escalar vs gold |
| 5 | `draft_gen` (solo subject) | commit-draft.py subject line | Marginal; probar solo si 1–3 ganan. | Conventional-Commits compliance |

**Anti-roles (NO delegar a un tiny real, nunca):** smart_trim (pérdida de
contexto = daño compuesto), web_synth, bug_finding, codeq_sum, judge/scorer,
cualquier
decisión de seguridad, JSON tool_call complejo (los <2B rompen JSON con
frecuencia; si se prueba tool_call, gate determinista de validación + retry
una vez + escalar).

## Arquitectura cascada (el potenciador real)

```
prompt/tarea trivial
  └─ tiny residente (1–2GB, keep_alive=-1, siempre en VRAM)
       ├─ confianza alta + validación determinista pasa → respuesta (0 tokens CLI)
       └─ falla validación o baja confianza → campeón local 4–12B
            └─ falla → CLI cloud (comportamiento actual)
```

- VRAM: 16GB totales. Tiny residente de ≤2GB convive con un campeón de 12GB
  cargado. Q8 xentriom (12GB) + tiny 2GB + KV = justo pero viable; verificar
  con `ollama ps` bajo carga real.
- La validación determinista solo bloquea formato inválido. Una etiqueta válida
  pero semánticamente equivocada atraviesa el gate; macro-F1 offline protege la
  promoción, pero no convierte el clasificador en un detector infalible en vivo.

## Instrucciones de ejecución (para el siguiente modelo)

1. **Candidatos a pull** (verificar nombres exactos en HF/Ollama antes de pull;
   revisar RANKING_HISTORY.md para no re-pullear eliminados):
   - gemma-4 clase 1B/2B instruction-tuned, preferir QAT oficial (la familia
     gemma-4-12B-it-qat ya demostró que QAT rinde).
   - LFM 1B (y 700M si existe) — **benchear con `--strip` obligatorio**.
   - qwen tiny (0.6B) como baseline de suelo.
2. **Smoke primero**: `ollama-bench smoke -m <modelo>` — leak gate. LFM saldrá
   `strippable=1`; eso es aceptable, hard-DQ solo si leak persiste tras strip.
3. **Slice `classification` — IMPLEMENTADO**: `features/classification/` +
   registro en `cli.py::_SLICES` + `tests/test_classification.py`. El dataset
   separa task routing de la taxonomía real de caveman. No inventa clases para
   `error-classify`, cuyo contrato real devuelve sistema/causa/fix. Registra
   macro-F1, accuracy, invalid rate, latencia mediana y TPS.
4. **Regla de aceptación por rol** (implementada y no negociable): tiny gana un
   rol solo si **(a)** macro-F1 no cae más de 0.02 absoluto frente al baseline,
   **(b)** ≥3x en latencia mediana end-to-end, **(c)** ≤2 GiB y **(d)** salida
   inválida ≤40%. TPS se reporta, pero no gobierna: con una etiqueta de salida
   es demasiado ruidoso y no representa el tiempo que percibe el consumidor.
5. **Después de classification**: repetir con `rerank` (nDCG@3) y
   `focused_extract` si el paso 4 dio al menos un ganador. **Cerrado:** ningún
   tiny pasó classification; se registró el dead-end y no se fuerzan roles 3–5.
6. **Wiring si hay ganador**: env override + cadena de fallback (patrón
   existente, ej. `OLLAMA_IMPROVE_MODELS`). Nuevo env sugerido:
   `OLLAMA_CLASSIFY_MODEL` con fallback a cryptidbleh. Actualizar
   `topics/harness-wiring-2026-07-04.md` y RANKING.md.
7. **Validación**: `pytest tests/ -q` + `ruff check .` tras cada slice nuevo.
   Verificar residencia real con `ollama ps` (keep_alive) antes de declarar
   la latencia ganada.
8. **Memoria**: resultados en `topics/candidates-round-15-…` (seguir numeración),
   decisión durable en `systemPatterns.md`, fracasos en `dead-ends.md`.

## Riesgos / trampas conocidas

- **Saturación de score**: los deep tasks actuales saturan; para tinys usar
  slices deterministas nuevos, no el rubric cap-7.0 (trampa documentada en
  bench-methodology).
- **JSON frágil <2B**: no prometer tool_call; gate + escalada.
- **Ollama 0.23.2-style incompats**: en 0.31.2 no hay incompat conocida con
  gemma-4 QAT, pero smoke primero siempre.
- **No tocar el lineup terminal**: los tinys entran como CAPA ADICIONAL
  (roles nuevos), no desplazan campeones existentes salvo que la regla del
  paso 4 se cumpla contra el titular del rol.
- **Ahorro real a medir, no asumir**: caveman ya usa regex determinista y no
  ahorra tokens sustituyéndolo por un LLM. Para cualquier router que sí use un
  modelo, instrumentar cuántas invocaciones
  prompt-router/día resuelve el tiny sin escalar. Si la tasa de escalada
  supera ~40%, la cascada añade latencia neta — revertir.
