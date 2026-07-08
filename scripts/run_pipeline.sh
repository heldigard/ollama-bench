#!/usr/bin/env bash
# Full bench pipeline: wait for deep -> specialized benches -> tie-break.
#
# GPU-SAFE by construction: every stage runs sequentially with --cooldown 60
# --temp-limit 75 (the specialized benches were converted off the parallel pool
# that overheated the GPU). Idempotent: a stage is skipped if its output MD
# already exists, so re-running after a kill resumes from the next stage.
#
# Usage:  nohup bash scripts/run_pipeline.sh &
# Log:    ~/.cache/ollama-bench/logs/pipeline_<ts>.log
set -u

REPO="$HOME/ollama-bench"
RESULTS="$HOME/.cache/ollama-bench/results"
LOGDIR="$HOME/.cache/ollama-bench/logs"
TS="$(date +%Y%m%d_%H%M%S)"
PIPE_LOG="$LOGDIR/pipeline_${TS}.log"
COOLDOWN=60
TEMPLIMIT=75
DEEP_JSONL="$RESULTS/deep_bench_strip_details.jsonl"

mkdir -p "$LOGDIR" "$RESULTS"
cd "$REPO" || {
    echo "cannot cd $REPO"
    exit 1
}
exec > >(tee -a "$PIPE_LOG") 2>&1

log() { printf '\n=== [%s] %s ===\n' "$(date +%H:%M:%S)" "$*"; }

# smoke-OK LLM models (status ok or strippable), one per line.
smoke_ok_models() {
    python3 - <<'PY'
import csv, sys
from pathlib import Path
p = Path.home() / ".cache/ollama-bench/results/smoke_all.tsv"
if not p.exists():
    sys.exit(1)
for r in csv.DictReader(p.open(), delimiter="\t"):
    if r["status"] == "ok" or r.get("strippable") == "1":
        print(r["name"])
PY
}

# vision/OCR models only (pdf-ocr is meaningless on text LLMs).
ocr_models() {
    python3 - <<'PY'
import csv
from pathlib import Path
p = Path.home() / ".cache/ollama-bench/results/smoke_all.tsv"
if not p.exists():
    raise SystemExit
names = [r["name"] for r in csv.DictReader(p.open(), delimiter="\t")]
keys = ("unlimited-ocr", "/lift-gguf", "ocr-gguf", "sahilchachra", "prithivmlmods/lift")
for n in names:
    if any(k in n.lower() for k in keys):
        print(n)
PY
}

run_bench() { # run_bench <stage_name> <output_md> <cmd...>
    local name="$1"
    shift
    local md="$1"
    shift
    if [ -s "$md" ]; then
        log "SKIP $name (output exists: $md)"
        return 0
    fi
    log "RUN $name -> $md"
    "$@" || log "WARN: $name exited non-zero (continuing)"
}

# ── Stage 0: wait for the deep bench to finish ───────────────────────────────
log "STAGE 0: wait for deep bench"
while pgrep -f "ollama-bench " >/dev/null 2>&1; do
    done_n=$(python3 -c "import json;print(len({json.loads(l).get('model') for l in open('$DEEP_JSONL') if l.strip()}))" 2>/dev/null || echo "?")
    log "  a bench is running (deep $done_n/30); sleeping 120s"
    sleep 120
done
if [ ! -s "$DEEP_JSONL" ]; then
    log "ERROR: deep JSONL missing ($DEEP_JSONL) — run deep first"
    exit 1
fi
log "  deep complete."

# ── Stage 1: specialized benches (sequential, GPU-paced) ─────────────────────
log "STAGE 1: specialized benches"
mapfile -t LLM < <(smoke_ok_models)
log "  ${#LLM[@]} smoke-OK LLM models"

if [ "${#LLM[@]}" -gt 0 ]; then
    run_bench bug-finding "$RESULTS/bug_finding.md" \
        ollama-bench bug-finding -m "${LLM[@]}" --cooldown "$COOLDOWN" --temp-limit "$TEMPLIMIT"
    run_bench tool-call "$RESULTS/tool_call.md" \
        ollama-bench tool-call -m "${LLM[@]}" --cooldown "$COOLDOWN" --temp-limit "$TEMPLIMIT"
    run_bench pdf-extract "$RESULTS/pdf_extract.md" \
        ollama-bench pdf-extract -m "${LLM[@]}" --cooldown "$COOLDOWN" --temp-limit "$TEMPLIMIT"
fi

mapfile -t OCR < <(ocr_models)
log "  ${#OCR[@]} OCR models for pdf-ocr"
if [ "${#OCR[@]}" -gt 0 ]; then
    run_bench pdf-ocr "$RESULTS/pdf_ocr.md" \
        ollama-bench pdf-ocr -m "${OCR[@]}" --cooldown "$COOLDOWN" --temp-limit "$TEMPLIMIT"
fi

# ── Stage 2: tie-break the tied deep winners ─────────────────────────────────
log "STAGE 2: tie-break"
if [ -s "$RESULTS/tiebreak_ranking.md" ]; then
    log "SKIP tie-break (output exists)"
else
    WINNERS="$(python3 scripts/tie_winners.py "$DEEP_JSONL" 0.5)"
    if [ -n "$WINNERS" ]; then
        log "  tied winners ($(echo "$WINNERS" | wc -l)):"$'\n'"$(echo "$WINNERS" | sed 's/^/    /')"
        # shellcheck disable=SC2086  # intentional word-split into -w nargs
        ollama-bench tie-break -w $WINNERS --cooldown "$COOLDOWN" --temp-limit "$TEMPLIMIT" ||
            log "WARN: tie-break exited non-zero"
    else
        log "  no ties detected within margin 0.5; skipping tie-break"
    fi
fi

log "PIPELINE DONE"
echo "Reports:"
ls -1 "$RESULTS"/*.md 2>/dev/null | sed 's/^/  /'
