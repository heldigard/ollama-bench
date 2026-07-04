#!/usr/bin/env python3
"""Deep-bench the 6 newly downloaded candidates vs the known winners.

Reuses bench_deep.TESTS + run/unload + judge_deep.JUDGES so scores are
directly comparable to final_ranking_v2.json history. Sequential + think=False
+ unload after every call (CPU/GPU-safe, one model resident at a time)."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/eldi/bench/ollama")
import bench_deep as bd          # noqa: E402
import judge_deep as jd          # noqa: E402

OUT = Path("/home/eldi/bench/ollama/results_new")
OUT.mkdir(parents=True, exist_ok=True)

NEW_MODELS = [
    "kwangsuklee/Qwen3.5-9B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest",
    "kwangsuklee/Qwen3.5-4B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest",
    "kwangsuklee/Qwen3.5-2B-Claude-4.6-Opus-Reasoning-Distilled-GGUF:latest",
    "lfm2.5:8b",
    "ornith:latest",
    "izy/North-Mini-Code-1.0:IQ4_XS",   # 15GB — run last (heaviest)
]

# Known winners for reference (Q, tok/s, COMP) from final_ranking_v2.json
WINNERS = {
    "qwen3.5:4b":                                                        (2.56, 80.9, 53.02),
    "carstenuhlig/omnicoder-9b:Q4_K_M":                                  (2.56, 84.0, 55.17),
    "fredrezones55/Qwopus3.5:4b":                                        (2.38, 88.8, 50.11),
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest":             (2.61, 43.1, 29.38),
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest":         (2.29, 26.8, 14.01),
}
BEST_COMP = 55.17   # carstenuhlig overall (note: leaks for hooks — qwen3.5 53.02 is the practical best)
PRACTICAL_BEST = 53.02  # qwen3.5:4b — the clean default to beat


def main() -> int:
    results: list[dict] = []
    total = len(NEW_MODELS) * len(bd.TESTS)
    done = 0
    for m in NEW_MODELS:
        print(f"\n=== {m} ===", flush=True)
        for tid, domain, prompt in bd.TESTS:
            done += 1
            num_ctx = 8192 if tid == "longctx_summary" else 4096
            num_predict = 1024 if tid != "compact_long" else 768
            r = bd.run(m, prompt, num_predict=num_predict, num_ctx=num_ctx)
            if not r["ok"]:
                print(f"[{done}/{total}] {tid:18s} ERR {r['error'][:55]}", flush=True)
                results.append({"model": m, "test_id": tid, "domain": domain,
                                "status": "error", "error": r["error"]})
            else:
                tps = r["eval_tokens"] / r["total_s"] if r["total_s"] > 0 else 0
                vram = bd.gpu_mem()
                q, note = jd.JUDGES[domain](r["output"])
                print(f"[{done}/{total}] {tid:18s} Q={q} {tps:5.1f}tok/s "
                      f"{r['total_s']:4.1f}s vram={vram} done={r['done_reason']}", flush=True)
                results.append({"model": m, "test_id": tid, "domain": domain, "status": "ok",
                                "tps": round(tps, 2), "total_s": round(r["total_s"], 3),
                                "vram": vram, "q": q, "note": note,
                                "out_chars": len(r["output"]), "done_reason": r["done_reason"],
                                "output_head": r["output"][:200]})
            bd.unload(m)
            with (OUT / "all.jsonl").open("a") as f:
                f.write(json.dumps(results[-1]) + "\n")

    # ---- Aggregate composite ----
    print(f"\n{'='*94}\nNEW MODELS — COMPOSITE vs WINNERS\n{'='*94}", flush=True)
    print(f"{'model':<64}{'Q':>5}{'tok/s':>8}{'vram':>7}{'COMP':>7}  verdict", flush=True)
    rows = []
    for m in NEW_MODELS:
        ok = [r for r in results if r["model"] == m and r["status"] == "ok"]
        if not ok:
            print(f"{m[:63]:<64}  (all errored — likely OOM/size)", flush=True)
            continue
        avg_q = sum(r["q"] for r in ok) / len(ok)
        avg_s = sum(r["tps"] for r in ok) / len(ok)
        peak = max(r["vram"] for r in ok)
        comp = round(avg_s * (avg_q ** 2) / 10, 2)
        rows.append({"model": m, "Q": round(avg_q, 2), "tps": round(avg_s, 1),
                     "vram": peak, "COMP": comp})
    for r in sorted(rows, key=lambda x: x["COMP"], reverse=True):
        v = ("★ BEATS practical best (qwen3.5)" if r["COMP"] > PRACTICAL_BEST
             else ("≈ competitive" if r["COMP"] > 30 else "✗ below winners"))
        print(f"{r['model'][:63]:<64}{r['Q']:>5}{r['tps']:>8}{r['vram']:>7}{r['COMP']:>7}  {v}", flush=True)
    print(f"\n--- known winners (reference) ---", flush=True)
    for m, (q, s, c) in WINNERS.items():
        print(f"{m[:63]:<64}{q:>5}{s:>8}{'':>7}{c:>7}", flush=True)

    # ---- Per-domain ----
    print(f"\n{'='*94}\nPER-DOMAIN (avg Q, then tok/s)\n{'='*94}", flush=True)
    for d in sorted({r["domain"] for r in results if r["status"] == "ok"}):
        print(f"\n[{d.upper()}]", flush=True)
        dom = [r for r in results if r["status"] == "ok" and r["domain"] == d]
        by_m: dict[str, list[dict]] = {}
        for r in dom:
            by_m.setdefault(r["model"], []).append(r)
        for m, rs in sorted(by_m.items(),
                            key=lambda kv: (sum(r["q"] for r in kv[1]) / len(kv[1]),
                                            sum(r["tps"] for r in kv[1]) / len(kv[1])), reverse=True):
            q = sum(r["q"] for r in rs) / len(rs)
            s = sum(r["tps"] for r in rs) / len(rs)
            print(f"  {m[:55]:<55} Q={q:.2f} {s:5.1f}tok/s ({len(rs)})", flush=True)

    (OUT / "all.json").write_text(json.dumps(results, indent=2))
    (OUT / "summary.json").write_text(json.dumps({"rows": rows,
                                                   "winners": {k: list(v) for k, v in WINNERS.items()}},
                                                  indent=2))
    print(f"\nSaved: {OUT/'all.json'}  +  {OUT/'summary.json'}", flush=True)
    print("BENCH_NEW_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
