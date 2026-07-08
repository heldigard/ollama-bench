"""Prompt data for canonical tasks.

Separated from canonical_tasks.py to keep files under 500 LOC.
Import PROMPTS and HARD_PROMPTS from here; scoring stays in canonical_tasks.py.
"""

from __future__ import annotations

from typing import Any

# fmt: off

PROMPTS: dict[str, dict[str, Any]] = {
    "improve": {
        "budget_words": 150,
        "items": [
            (
                "improve_auth_flake",
                "Rewrite this vague request into a concrete implementation spec with sections GOAL, ASSUMPTIONS, FILES, STEPS, ACCEPTANCE. Original: users sometimes cannot login after password reset, fix auth.",
                ("password reset", "login", "session", "token", "reproduce", "test", "auth"),
            ),
            (
                "improve_dashboard_perf",
                "Rewrite into an actionable engineering task. Original: haz que el dashboard cargue mas rapido, esta lentisimo cuando hay muchas cuentas.",
                ("dashboard", "many accounts", "profile", "query", "cache", "metric", "acceptance"),
            ),
            (
                "improve_flaky_test",
                "Turn this into a precise debugging spec. Original: el test de checkout falla a veces en CI pero local no.",
                ("checkout", "ci", "flaky", "seed", "timeout", "reproduce", "pytest"),
            ),
            (
                "improve_csv_import",
                "Rewrite into a concise spec. Original: i need the csv thing to import customers but skip bad rows and tell me what failed.",
                ("csv", "customers", "bad rows", "validation", "error report", "acceptance"),
            ),
            (
                "improve_conflicting_req",
                "Rewrite into a spec. Identify conflicts and propose resolution. Original: make the search faster but also return more results, and keep memory usage low.",
                ("search", "fast", "memory", "tradeoff", "benchmark", "conflict", "resolution"),
            ),
            (
                "improve_missing_context",
                "Rewrite into a spec. Flag what's MISSING and make reasonable assumptions. Original: we need the notification system to work better.",
                ("notification", "assumption", "missing", "channels", "throttle", "priority"),
            ),
            (
                "improve_multi_lang",
                "Rewrite into an actionable spec. Original: el API de reports esta lento, users are complaining que tarda mucho cuando seleccionan un date range grande. Also the PDF export crashes sometimes.",
                ("reports", "date range", "pdf export", "performance", "crash", "timeout", "pagination"),
            ),
        ],
    },
    "codeq_sum": {
        "budget_words": 32,
        "items": [
            (
                "sum_send_chat",
                "Summarize this function in ONE sentence, max 30 words. NO preamble, no code blocks.\n\nasync function sendChatMessage(trimmed: string) {\n  if (!trimmed || sending.value) return;\n  draft.value = '';\n  try {\n    await api.post('/chat', { text: trimmed });\n  } catch (e) {\n    error.value = e.message;\n  }\n}",
                ("empty", "sending", "clears", "posts", "error"),
            ),
            (
                "sum_chunk_text",
                "Summarize in ONE sentence, max 30 words. NO preamble.\n\nfunction chunkText(text, maxTokens) {\n  const sentences = text.split(/(?<=[.!?])\\s+/);\n  const out = [];\n  let buf = '';\n  for (const s of sentences) {\n    if ((buf + s).split(/\\s+/).length > maxTokens) { out.push(buf.trim()); buf = s; }\n    else buf += ' ' + s;\n  }\n  if (buf) out.push(buf.trim());\n  return out;\n}",
                ("sentences", "chunks", "max", "tokens", "buffer"),
            ),
            (
                "sum_subscribe",
                "Summarize this function in ONE sentence, max 30 words. Mention the important behavior.\n\nasync function subscribeToTopic(topic, handler) {\n  if (subscriptions.has(topic)) return false;\n  const controller = new AbortController();\n  const conn = await openStream(topic, { signal: controller.signal });\n  subscriptions.set(topic, { controller, handler });\n  conn.on('data', msg => {\n    if (msg.type === 'error') { controller.abort(); unsubscribe(topic); }\n    else handler(msg);\n  });\n  return true;\n}",
                ("topic", "stream", "abort", "unsubscribe", "handler"),
            ),
            (
                "sum_retry",
                "One-sentence summary, max 30 words. NO preamble.\n\nasync function retry(fn, attempts, delayMs) {\n  let lastErr;\n  for (let i = 0; i < attempts; i++) {\n    try { return await fn(); }\n    catch (err) { lastErr = err; await sleep(delayMs * (i + 1)); }\n  }\n  throw lastErr;\n}",
                ("retry", "attempts", "delay", "last", "throws"),
            ),
            (
                "sum_error_handler",
                "Summarize in ONE sentence, max 30 words. Mention if errors are swallowed.\n\nfunction processRecords(records) {\n  let ok = 0, fail = 0;\n  for (const r of records) {\n    try {\n      validate(r);\n      db.insert(r);\n      ok++;\n    } catch (e) {\n      fail++;\n    }\n  }\n  return { ok, fail };\n}",
                ("records", "validate", "insert", "ok", "fail", "swallow"),
            ),
            (
                "sum_stateful_class",
                "Summarize in ONE sentence, max 30 words. NO preamble.\n\nclass RateLimiter {\n  constructor(maxPerWindow, windowMs) {\n    this.max = maxPerWindow;\n    this.window = windowMs;\n    this.timestamps = [];\n  }\n  allow() {\n    const now = Date.now();\n    this.timestamps = this.timestamps.filter(t => now - t < this.window);\n    if (this.timestamps.length >= this.max) return false;\n    this.timestamps.push(now);\n    return true;\n  }\n}",
                ("rate", "limit", "window", "timestamps", "allow", "max"),
            ),
            (
                "sum_recursive",
                "Summarize in ONE sentence, max 30 words. NO preamble.\n\nfunction flatten(arr) {\n  const out = [];\n  for (const item of arr) {\n    if (Array.isArray(item)) out.push(...flatten(item));\n    else out.push(item);\n  }\n  return out;\n}",
                ("flatten", "recursive", "array", "nested", "push"),
            ),
        ],
    },
    "smart_trim": {
        "budget_words": 170,
        "items": [
            (
                "trim_wsgi_pytest",
                "Compress to handoff bullet list. Keep task, current step, decisions, next action, blockers. 4-8 bullets, no preamble.\n\n[Earlier] User asked about Python venv setup on WSL2. Assistant recommended uv and created .venv. [Earlier] Imports broke because PYTHONPATH pointed at global site-packages. Fixed by removing override. [Now] pytest collected 0 items. Investigating tests/ dir and conftest.py placement. [Now] ruff says no module, same environment root cause. [Decision] Stay on uv, no pip. [Next] Add root conftest.py, reinstall dev deps, run pytest and ruff. [Blocked] None.",
                ("uv", "pytest collected 0", "conftest", "ruff", "next", "blocked none", "pythonpath"),
            ),
            (
                "trim_ci_snapshots",
                "Make a handoff summary. Keep decisions and next action.\n\n[Earlier] CI took 27min: install=4, test=8, build=12, deploy=3. Chose nx affected because repo already uses nx. [Earlier] nx reduced CI to 18min, still too slow. [Now] vitest migration done; snapshots still slow. Found 14 nested snapshots taking 2.1s each. happy-dom is 30 percent faster than jsdom. [Decision] Delete non-visual snapshots, keep only SVG/PNG render snapshots. [Next] PR branch drop-snapshots-v1 and target <10min CI. [Blocked] None.",
                ("ci", "27min", "nx", "vitest", "snapshots", "drop-snapshots-v1", "blocked none"),
            ),
            (
                "trim_azure_zip",
                "Condense this session into a handoff. 5-9 bullets.\n\n[Earlier] Azure Function cold start baseline 4s, target <500ms. Decided premium EP1 plus always-on. [Earlier] Local func start was 1.2s without warmup. [Now] User said deploy it. Need zip package and az functionapp deploy. [Risk] local.settings.json has storage connection string and must not be zipped. [Decision] Use --build-native-deps for cryptography wheels. [Next] Build pkg.zip excluding .venv, __pycache__, Tests, .git, local.settings.json; then deploy. [Blocked] az login is already done.",
                ("azure function", "premium ep1", "always-on", "local.settings.json", "build-native-deps", "pkg.zip", "az login"),
            ),
            (
                "trim_contradiction",
                "Compress to handoff. Flag any contradictions.\n\n[Earlier] Decided to use SQLite for the local cache. Performance was fine. [Earlier] User said we need multi-process access. SQLite doesn't handle that well. [Now] Switched decision to PostgreSQL. [Now] Realized the deployment target has no PostgreSQL available. [Decision] Reverted to SQLite with WAL mode. [Next] Test WAL under concurrent writes. [Blocked] Need to verify WAL works on the target OS.",
                ("sqlite", "multi-process", "postgresql", "wal", "contradict", "reverted", "concurrent"),
            ),
            (
                "trim_red_herring",
                "Make a handoff summary. Note dead ends briefly.\n\n[Earlier] API returning 500. Spent 2 hours investigating database connection pool. Pool was fine. [Earlier] Checked nginx config. Also fine. [Now] Found the real issue: the rate limiter middleware was not awaiting an async call, causing unhandled promise rejection. [Decision] Replace rate limiter with p-limit. [Next] PR with the fix + a regression test. [Blocked] None. [Dead end] DB pool investigation was a red herring.",
                ("500", "rate limiter", "async", "p-limit", "red herring", "dead end", "regression"),
            ),
            (
                "trim_multi_blocker",
                "Condense into 6-10 bullets.\n\n[Earlier] Auth flow broken after migration. Blocker: JWT secret rotation not deployed. [Earlier] Deployed secret rotation. New blocker: token refresh endpoint returns 401 for tokens issued before rotation. [Now] Added grace period for old tokens. New blocker: grace period bypasses revocation check. [Decision] Grace period only applies to non-revoked tokens. [Risk] Clock skew between auth servers could allow brief window of invalid tokens. [Next] Add NTP sync check to health endpoint. [Blocked] Waiting on infra team for NTP config.",
                ("jwt", "secret rotation", "401", "grace period", "revocation", "clock skew", "ntp", "infra"),
            ),
        ],
    },
    "web_synth": {
        "budget_words": 210,
        "items": [
            (
                "synth_problem_json",
                "Synthesize a 3-paragraph summary with citations [1], [2], [3]. No preamble.\n\n[1] RFC 9457 defines Problem Details for HTTP APIs with type, title, status, detail, instance fields. [2] Microsoft REST API Guidelines recommend problem+json for 4xx/5xx and correlation id in instance. [3] Spring Boot 3.2+ exposes ProblemDetail through ResponseEntityExceptionHandler and RestControllerAdvice.",
                ("problem details", "type", "title", "status", "correlation", "spring boot", "problemdetail"),
            ),
            (
                "synth_conflict_bench",
                "Synthesize with citations. If sources disagree, state the disagreement.\n\n[1] Vendor announcement says Model A reached 64.3 on SWE-bench Verified in Oct 2024. [2] March 2025 blog says Model B reached 62.3 on the same benchmark. [3] Independent December 2025 report lists Model B at 70.3 on the same benchmark.",
                ("64.3", "62.3", "70.3", "same benchmark", "model b", "independent"),
            ),
            (
                "synth_security_policy",
                "Write a 2-3 paragraph synthesis with citations [1][2][3].\n\n[1] OWASP recommends validating redirect targets against an allow-list. [2] A product incident report says unvalidated next= parameters caused account takeover via phishing. [3] The engineering policy requires rejecting absolute external URLs and logging blocked redirect attempts.",
                ("owasp", "allow-list", "next=", "account takeover", "external urls", "logging"),
            ),
            (
                "synth_4_sources_overlap",
                "Synthesize 4 sources into 3 paragraphs. Handle overlap and contradiction. Cite all sources.\n\n[1] A 2024 study found that connection pooling reduces p99 latency by 40% in PostgreSQL. [2] The pgBouncer docs recommend pool sizes of 2-4 per CPU core. [3] A 2025 blog post says connection pooling caused stale-connection errors under high write load. [4] Another 2024 study confirms pooling benefits but warns about prepared statement cache invalidation.",
                ("connection pooling", "p99", "pgbouncer", "stale", "prepared statement", "cpu core", "latency"),
            ),
            (
                "synth_no_consensus",
                "Synthesize with citations. Sources disagree — present all positions, do NOT force consensus.\n\n[1] Microservices advocate says monoliths are unmaintainable beyond 10 engineers. [2] A case study shows Shopify runs a modular monolith serving 80M+ merchants. [3] A 2025 survey says 60% of teams that adopted microservices regret the complexity. [4] Netflix blog says microservices are essential for their scale.",
                ("microservices", "monolith", "shopify", "netflix", "complexity", "scale", "modular"),
            ),
            (
                "synth_tradeoff",
                "Synthesize a technical tradeoff analysis. Cite sources, state your recommendation.\n\n[1] gRPC benchmarks show 10x throughput over REST for internal services. [2] REST adoption is 85% according to a 2025 developer survey, gRPC at 15%. [3] A migration report says moving from REST to gRPC took 6 months and broke 3rd-party integrations. [4] A polyglot team report says gRPC tooling gaps in Python/JS caused 2-week delays per service.",
                ("grpc", "rest", "throughput", "adoption", "migration", "tooling", "polyglot"),
            ),
        ],
    },
    "code_gen": {
        "budget_words": 120,
        "items": [
            (
                "code_validate_email",
                "Write a Python function `validate_email(s: str) -> bool` using ONLY stdlib re. Handle None, empty, whitespace. Return False on invalid. No docstring, no comments, just the function.",
                ("validate_email", "none", "strip", "re.", "return false", "bool"),
                {"function": "validate_email", "args": ("s",), "allow_imports": True},
            ),
            (
                "code_unique_order",
                "Write Python function `unique_preserve_order(items: list[str | None]) -> list[str]`. Skip None and ''. Keep first-seen order. No imports. Just the function.",
                ("unique_preserve_order", "seen", "none", "append", "return", "items"),
                {"function": "unique_preserve_order", "args": ("items",), "allow_imports": False},
            ),
            (
                "code_chunk_lines",
                "Write Python function `chunk_lines(text: str, max_chars: int) -> list[str]` that returns chunks <= max_chars. Split on newline first, then spaces for long lines. No external deps. Just the function.",
                ("chunk_lines", "max_chars", "split", "append", "return", "line"),
                {"function": "chunk_lines", "args": ("text", "max_chars"), "allow_imports": False},
            ),
            (
                "code_parse_bool",
                "Write Python function `parse_bool(value) -> bool | None`. Return True for yes/true/1/on, False for no/false/0/off, None for unknown or None. No imports. Just the function.",
                ("parse_bool", "true", "false", "none", "lower", "return"),
                {"function": "parse_bool", "args": ("value",), "allow_imports": False},
            ),
            (
                "code_retry_backoff",
                "Write Python function `retry_with_backoff(fn, max_attempts=5, base_delay=0.1) -> Any`. Retry fn() up to max_attempts with exponential backoff (base_delay * 2**attempt). Raise last exception on exhaustion. No external deps. Just the function.",
                ("retry", "backoff", "attempt", "delay", "sleep", "raise", "exception"),
                {"function": "retry_with_backoff", "args": ("fn", "max_attempts", "base_delay"), "allow_imports": False},
            ),
            (
                "code_merge_sorted",
                "Write Python function `merge_sorted(a: list[int], b: list[int]) -> list[int]`. Merge two sorted lists into one sorted list, deduplicating. No imports. Just the function.",
                ("merge", "sorted", "deduplicate", "append", "return", "while"),
                {"function": "merge_sorted", "args": ("a", "b"), "allow_imports": False},
            ),
            (
                "code_flatten_nested",
                "Write Python function `flatten_nested(lst: list) -> list`. Flatten arbitrarily nested lists (e.g. [1,[2,[3]],4] -> [1,2,3,4]). Handle empty lists. No imports. Just the function.",
                ("flatten", "nested", "list", "isinstance", "extend", "recursive"),
                {"function": "flatten_nested", "args": ("lst",), "allow_imports": False},
            ),
        ],
    },
}


# Tie-break hard prompts: genuinely harder scenarios, NOT just concatenation.
# Each task gets 3 unique hard prompts with tighter budgets relative to complexity.
HARD_PROMPTS: dict[str, dict[str, Any]] = {
    "improve": {
        "budget": 200,
        "items": [
            (
                "hard_improve_stakeholder_conflict",
                "Rewrite into a spec with GOAL, CONSTRAINTS, TRADE-OFFS, OPEN QUESTIONS. Two stakeholders disagree: PM wants real-time notifications, architect says polling is sufficient for 100 users. Original: add notifications to the app.",
                ("notification", "real-time", "polling", "tradeoff", "stakeholder", "constraint"),
            ),
            (
                "hard_improve_vague_urgent",
                "Rewrite into a precise spec. The request is vague AND urgent — identify what you'd need to ask vs what you can assume. Original: the whole auth system is broken, users are locked out, fix it NOW.",
                ("auth", "locked out", "assume", "investigate", "rollback", "monitoring"),
            ),
            (
                "hard_improve_scale_migration",
                "Rewrite into a migration spec. Original: we need to move from a single PostgreSQL to a sharded setup because writes are getting slow. Also we need zero downtime.",
                ("shard", "migration", "zero downtime", "write", "routing", "cutover", "rollback"),
            ),
        ],
    },
    "codeq_sum": {
        "budget": 48,
        "items": [
            (
                "hard_sum_complex_class",
                "Summarize in ONE sentence, max 45 words. Mention the key invariant.\n\nclass LRUCache {\n  constructor(capacity) {\n    this.cap = capacity;\n    this.map = new Map();\n  }\n  get(key) {\n    if (!this.map.has(key)) return -1;\n    const val = this.map.get(key);\n    this.map.delete(key);\n    this.map.set(key, val);\n    return val;\n  }\n  put(key, value) {\n    if (this.map.has(key)) this.map.delete(key);\n    this.map.set(key, value);\n    if (this.map.size > this.cap) {\n      const oldest = this.map.keys().next().value;\n      this.map.delete(oldest);\n    }\n  }\n}",
                ("lru", "cache", "capacity", "evict", "oldest", "map", "order"),
            ),
            (
                "hard_sum_error_chain",
                "Summarize in ONE sentence, max 45 words. Mention the error handling strategy.\n\nasync function fetchWithFallback(urls, opts) {\n  const errors = [];\n  for (const url of urls) {\n    try {\n      const res = await fetch(url, opts);\n      if (!res.ok) throw new Error(`HTTP ${res.status}`);\n      return await res.json();\n    } catch (e) {\n      errors.push({ url, error: e.message });\n    }\n  }\n  throw new AggregateError(errors.map(e => new Error(`${e.url}: ${e.error}`)), 'All URLs failed');\n}",
                ("fallback", "urls", "errors", "aggregate", "fetch", "failed"),
            ),
            (
                "hard_sum_middleware",
                "Summarize in ONE sentence, max 45 words. NO preamble.\n\nfunction compose(...middlewares) {\n  return function(context, next) {\n    let index = -1;\n    function dispatch(i) {\n      if (i <= index) return Promise.reject(new Error('next() called multiple times'));\n      index = i;\n      let fn = middlewares[i];\n      if (i === middlewares.length) fn = next;\n      if (!fn) return Promise.resolve();\n      try {\n        return Promise.resolve(fn(context, () => dispatch(i + 1)));\n      } catch (err) {\n        return Promise.reject(err);\n      }\n    }\n    return dispatch(0);\n  };\n}",
                ("compose", "middleware", "dispatch", "next", "promise", "chain"),
            ),
        ],
    },
    "smart_trim": {
        "budget": 230,
        "items": [
            (
                "hard_trim_long_session",
                "Compress to 8-12 bullets. Preserve ALL decisions and blockers.\n\n[Earlier] Started migrating from Express to Fastify. 47 endpoints. [Decision] Migrate incrementally, one route group at a time. [Earlier] First batch (auth routes) went well. 2ms improvement per request. [Earlier] Second batch (user routes) broke because Fastify doesn't support middleware chains the same way. [Decision] Rewrite middleware as Fastify plugins. [Now] Third batch (admin routes) hit a wall: admin routes use session-based auth, Fastify defaults to JWT. [Decision] Add fastify-session plugin. [Risk] fastify-session stores sessions in memory by default, won't survive restarts. [Now] Added Redis session store. [New problem] Redis connection pool exhaustion under load test (500 concurrent). [Decision] Increase pool to 50, add connection timeout. [Next] Load test again with pool=50. [Blocked] DevOps needs to provision Redis cluster for production. [Blocked] Auth team needs to review JWT-to-session migration plan.",
                ("express", "fastify", "middleware", "session", "redis", "pool", "migration"),
            ),
            (
                "hard_trim_multi_decisions",
                "Make a handoff. Highlight decision reversals.\n\n[Earlier] Chose React for the new dashboard. [Earlier] Realized the team knows Vue better. Switched to Vue. [Earlier] Vue 3 composition API was too unfamiliar. Switched back to React with a 2-day training sprint. [Now] React app is built but bundle is 2.3MB. [Decision] Add code splitting with React.lazy. [Now] Lazy loading broke SSR. [Decision] Use dynamic imports with ssr: false flag. [Now] First meaningful paint went from 4.2s to 1.8s. [Next] Add skeleton screens for lazy chunks. [Blocked] Design team hasn't provided skeleton designs.",
                ("react", "vue", "switched", "bundle", "code splitting", "ssr", "skeleton"),
            ),
            (
                "hard_trim_security_incident",
                "Compress to handoff. This is a security incident — preserve ALL technical details.\n\n[Earlier] Found SQL injection in /api/search endpoint. Parameterized queries were bypassed by string concatenation in a dynamic ORDER BY clause. [Now] Patched with allow-list of sortable columns. [Earlier] Audit found 3 more endpoints with similar pattern. [Now] Fixed all 3. [Risk] Old API tokens may have been used to exploit the injection. [Decision] Force-rotate all API tokens issued before the fix. [Now] Token rotation script deployed. [New issue] Some clients store tokens in localStorage, rotation breaks them silently. [Next] Add token-expired middleware that returns 401 with re-auth instructions. [Blocked] Need to notify affected customers before force-rotating.",
                ("sql injection", "parameterized", "order by", "allow-list", "token rotation", "localStorage", "401"),
            ),
        ],
    },
    "web_synth": {
        "budget": 280,
        "items": [
            (
                "hard_synth_5_sources",
                "Synthesize 5 sources into 4 paragraphs. Handle contradictions and gaps. Cite all sources.\n\n[1] Google's 2024 paper says multi-agent systems outperform single agents by 23% on complex tasks. [2] OpenAI's blog warns that multi-agent systems have coordination overhead that doubles token costs. [3] A 2025 benchmark shows single-agent GPT-5 matches multi-agent GPT-4 performance. [4] Microsoft Research reports that agent communication protocols are the bottleneck, not model capability. [5] A practitioner survey says 70% of multi-agent deployments failed to outperform single-agent baselines in production.",
                ("multi-agent", "single agent", "coordination", "token cost", "benchmark", "communication", "production"),
            ),
            (
                "hard_synth_contradictory_data",
                "Synthesize with citations. The sources directly contradict each other — do NOT pick a side, present the evidence.\n\n[1] A 2024 meta-analysis of 50 studies says type systems prevent 15% of bugs. [2] A 2025 study of 200 repos found no significant difference in bug rates between TypeScript and JavaScript. [3] Google's internal data says TypeScript adoption reduced P0 incidents by 22%. [4] A developer survey says 45% of TypeScript users report spending more time fighting the type system than writing business logic.",
                ("type system", "bugs", "typescript", "javascript", "meta-analysis", "p0", "developer survey"),
            ),
            (
                "hard_synth_technical_decision",
                "Synthesize into a decision document. Present options, evidence, and a recommendation.\n\n[1] SQLite benchmarks show 10x faster reads than PostgreSQL for <1GB databases. [2] PostgreSQL supports concurrent writes; SQLite serializes them. [3] Litestream enables SQLite replication with <1s failover. [4] A 2025 case study says a SaaS company saved $40K/year by switching from PostgreSQL to SQLite+Litestream. [5] The PostgreSQL wiki says connection pooling handles 10K+ concurrent connections efficiently.",
                ("sqlite", "postgresql", "concurrent", "litestream", "replication", "failover", "connection pooling"),
            ),
        ],
    },
    "code_gen": {
        "budget": 160,
        "items": [
            (
                "hard_code_rate_limiter",
                "Write Python class `TokenBucketRateLimiter` with methods `allow(key: str) -> bool` and `reset(key: str)`. Token bucket algorithm: capacity tokens, refill_rate tokens/second. Thread-safe using threading.Lock. No external deps. Just the class.",
                ("token", "bucket", "rate", "limit", "lock", "thread", "refill"),
                {"function": "TokenBucketRateLimiter", "args": ("capacity", "refill_rate"), "allow_imports": False},
            ),
            (
                "hard_code_topological_sort",
                "Write Python function `topological_sort(graph: dict[str, list[str]]) -> list[str]`. Returns topologically sorted order. Raise ValueError if cycle detected. No imports. Just the function.",
                ("topological", "sort", "graph", "cycle", "visit", "stack", "raise"),
                {"function": "topological_sort", "args": ("graph",), "allow_imports": False},
            ),
            (
                "hard_code_diff_engine",
                "Write Python function `simple_diff(old: list[str], new: list[str]) -> list[dict]`. Returns a list of operations: {'op': 'keep', 'line': str}, {'op': 'remove', 'line': str}, {'op': 'add', 'line': str}. Use LCS-based diff. No imports. Just the function.",
                ("diff", "lcs", "keep", "remove", "add", "dynamic", "matrix"),
                {"function": "simple_diff", "args": ("old", "new"), "allow_imports": False},
            ),
        ],
    },
}

# fmt: on
