"""Versioned bilingual relevance judgments for the reranking benchmark."""

from __future__ import annotations

from typing import TypedDict


class RerankDocument(TypedDict):
    id: str
    text: str
    relevance: int


class RerankCase(TypedDict):
    id: str
    language: str
    difficulty: str
    query: str
    documents: tuple[RerankDocument, ...]


def _documents(*items: tuple[str, int]) -> tuple[RerankDocument, ...]:
    """Assign stable IDs while keeping the annotated corpus readable."""
    return tuple(
        {"id": f"d{index}", "text": text, "relevance": relevance}
        for index, (text, relevance) in enumerate(items, 1)
    )


def _case(
    case_id: str,
    language: str,
    difficulty: str,
    query: str,
    *documents: tuple[str, int],
) -> RerankCase:
    return {
        "id": case_id,
        "language": language,
        "difficulty": difficulty,
        "query": query,
        "documents": _documents(*documents),
    }


CASES: tuple[RerankCase, ...] = (
    _case(
        "codeq-model-env",
        "en",
        "medium",
        "Which environment variable selects the local model for codeq summaries?",
        ("Set CODEQ_SUMMARY_MODEL to select codeq's summary/context/relations model.", 3),
        ("OLLAMA_URL changes the Ollama daemon endpoint used by local tools.", 1),
        ("CODEQ_INDEX_DIR chooses where codeq writes its SQLite index.", 0),
        ("SMART_TRIM_PRIMARY_MODEL controls the PreCompact summarizer.", 0),
        ("CallOpts pins seed=42 for reproducible benchmark generation.", 0),
        ("Embedding models create vectors for semantic retrieval, not summaries.", 0),
        ("The codeq CLI can print a map of indexed files.", 0),
        ("A fallback model is used only when the primary Ollama call fails.", 2),
        ("Ruff checks Python style and lint rules.", 0),
        ("A model tag normally has an owner, repository, and quantization suffix.", 0),
    ),
    _case(
        "negation-cloud",
        "en",
        "hard",
        "I do not want a cloud fallback. Which option keeps the summary fully local?",
        ("Use the local Ollama primary and secondary cascade; do not invoke cheap_llm.", 3),
        ("Cloud fallback runs only after both local summarizers return no result.", 2),
        ("Set an API key so a hosted model can answer faster.", 0),
        ("A local model can be kept resident with Ollama keep_alive.", 1),
        ("Web search may use a hosted provider if its local tier fails.", 0),
        ("Secret scrubbing is required before any optional cloud escalation.", 1),
        ("The benchmark cache lives under the user's cache directory.", 0),
        ("Use an uncensored model for every security-sensitive summary.", 0),
        ("An embedding model cannot generate a text handoff.", 0),
        ("Temperature zero improves repeatability of a local generation call.", 1),
    ),
    _case(
        "jaguar-entity",
        "en",
        "hard",
        "Find material about the Jaguar animal, not the Jaguar car brand.",
        ("The jaguar is a large spotted cat native to the Americas and a strong swimmer.", 3),
        ("Jaguar Land Rover announced a new electric vehicle platform.", 0),
        ("Conservation plans protect jaguar habitat corridors from fragmentation.", 2),
        ("A car's fuel economy depends on engine and driving conditions.", 0),
        ("Panthera onca is the scientific name for the jaguar species.", 3),
        ("A dealership can schedule maintenance for a Jaguar automobile.", 0),
        ("Big cats include lions, tigers, leopards, and jaguars.", 1),
        ("The animal's rosette pattern helps camouflage it in forest habitat.", 2),
        ("Vehicle insurance premiums vary by driver and location.", 0),
        ("A jaguar's diet commonly includes deer, capybara, and caiman.", 2),
    ),
    _case(
        "auth-csrf",
        "en",
        "medium",
        "How should an OAuth callback defend against CSRF?",
        (
            "Generate a high-entropy state value, bind it to the user session, and verify it on callback.",
            3,
        ),
        ("Use PKCE with a verifier and challenge for public OAuth clients.", 2),
        ("Store access tokens permanently in URLs for easier debugging.", 0),
        ("Validate redirect URIs against an allowlist rather than accepting arbitrary URLs.", 2),
        ("CSRF tokens protect browser requests that rely on ambient credentials.", 1),
        ("Disable TLS validation when a callback certificate expires.", 0),
        ("Rotate a leaked client secret and invalidate the old credential.", 1),
        ("SQL parameterization prevents injection in database queries.", 0),
        ("Use SameSite cookies as a defense-in-depth control where applicable.", 1),
        ("An OAuth authorization code should be exchanged server-side.", 2),
    ),
    _case(
        "n8n-patch",
        "en",
        "medium",
        "Why does an n8n Dynamics PATCH request fail with error 0x80072530?",
        (
            "The PATCH request was sent without an entity body; include the payload fields to update.",
            3,
        ),
        ("A 401 usually means the configured service connection credentials expired.", 0),
        ("An inactive workflow will not run on its schedule trigger.", 0),
        ("Confirm the entity identifier and send a JSON body with the PATCH request.", 2),
        ("Timeouts commonly indicate a slow downstream service.", 0),
        ("Use GET when you only need to retrieve an entity.", 1),
        ("Dataverse PATCH updates an existing entity rather than creating one.", 1),
        ("A missing body is distinct from an invalid OAuth audience.", 1),
        ("Retries cannot repair a structurally empty update payload.", 2),
        ("Webhook URLs should be treated as credentials when they are secret.", 0),
    ),
    _case(
        "prompt-mejora",
        "es",
        "medium",
        "Como convierto un prompt vago en una especificacion util para implementar codigo?",
        (
            "El prompt-improver transforma una peticion vaga en objetivo, restricciones, entradas, salida y criterios de aceptacion.",
            3,
        ),
        ("Pide archivos afectados, comportamiento esperado y casos limite verificables.", 2),
        ("Un saludo corto no necesita una especificacion de ingenieria.", 0),
        ("Las pruebas de aceptacion convierten requisitos ambiguos en resultados comprobables.", 2),
        ("smart-trim comprime una conversacion larga en un handoff.", 1),
        ("Una migracion de base de datos exige revisar compatibilidad y rollback.", 0),
        (
            "No inventes requisitos que el usuario no haya dado; formula supuestos explicitamente.",
            2,
        ),
        ("El comando ruff revisa estilo de Python.", 0),
        ("La salida debe separar alcance, decisiones y criterios de exito.", 2),
        ("Un modelo de embeddings no reescribe especificaciones.", 0),
    ),
    _case(
        "pdf-causa",
        "es",
        "hard",
        "Extrae solo la causa de terminacion de un contrato; no quiero la fecha ni la clausula de renovacion.",
        (
            "Causa de terminacion: incumplimiento material no subsanado dentro de treinta dias tras aviso escrito.",
            3,
        ),
        ("Fecha de vigencia: el contrato inicia el 1 de enero de 2026.", 0),
        ("Renovacion: se renueva automaticamente por periodos anuales salvo aviso previo.", 0),
        (
            "La terminacion inmediata procede por fraude, insolvencia o violacion de confidencialidad.",
            3,
        ),
        ("El aviso de terminacion debe enviarse a las direcciones designadas.", 1),
        ("Las facturas vencen a treinta dias de su emision.", 0),
        ("La clausula de fuerza mayor suspende obligaciones durante el evento.", 0),
        ("Una parte puede terminar por conveniencia con noventa dias de preaviso.", 2),
        ("La jurisdiccion aplicable es Bogota, Colombia.", 0),
        ("La subsanacion se mide desde la recepcion del aviso escrito.", 2),
    ),
    _case(
        "browser-ref",
        "es",
        "medium",
        "Que pasos permiten hacer clic de forma segura en el boton Guardar de una pagina con snapshot de accesibilidad?",
        (
            "Busca el elemento por su ref accesible actual, verifica nombre y estado, y ejecuta el click usando ese ref.",
            3,
        ),
        ("Toma un snapshot accesible antes de actuar para obtener referencias estables.", 2),
        ("Haz clic por coordenadas aproximadas sin inspeccionar la pagina.", 0),
        ("Confirma que el boton esta habilitado y que su etiqueta es Guardar antes del click.", 2),
        ("Una captura visual sirve solo para depurar problemas de presentacion.", 1),
        ("Despues del click, valida el cambio esperado o el mensaje de exito.", 2),
        ("Un selector CSS puede quedar obsoleto tras un cambio de layout.", 1),
        ("No inventes un ref que no aparezca en el snapshot actual.", 2),
        ("Un PDF escaneado requiere OCR, no una accion de navegador.", 0),
        ("El modelo debe devolver JSON cuando el contrato de herramienta lo exige.", 1),
    ),
)


def build_prompt(case: RerankCase) -> str:
    """Build the fixed, auditable ranking prompt without exposing gold labels."""
    documents = "\n".join(f"{document['id']}: {document['text']}" for document in case["documents"])
    return (
        "Rank the documents by how directly they answer the QUERY. "
        "Return exactly one JSON object and nothing else: "
        '{"ranking":["d1","d2","d3"]}. The ranking must contain exactly three '
        "different document IDs from the list, ordered best to worst.\n\n"
        f"QUERY:\n{case['query']}\n\nDOCUMENTS:\n{documents}\n\nJSON:"
    )
