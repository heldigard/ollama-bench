#!/usr/bin/env python3
"""Deep-bench the 4 newly researched candidates vs the known winners.

Reuses bench_deep.TESTS + run/unload + judge_deep.JUDGES so scores are
directly comparable to final_ranking_v2.json history. Sequential + think=False
+ unload after every call (one model resident at a time)."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/eldi/bench/ollama")
import bench_deep as bd          # noqa: E402
import judge_deep as jd          # noqa: E402

OUT = Path("/home/eldi/bench/ollama/results_candidates")
OUT.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    "phi4",                         # Phi-4 14B instruct (vs Mobius for improve)
    "deepseek-coder-v2:16b",        # MoE coder (vs composer for code)
    "qwen2.5-coder:14b",            # dedicated coder (alt to deepseek)
    "granite3.3:8b",                # clean enterprise instruct, 128K ctx
]

WINNERS = {
    "qwen3.5:4b":                                                (2.56, 80.9, 53.02),
    "carstenuhlig/omnicoder-9b:Q4_K_M":                          (2.56, 84.0, 55.17),
    "MobiusDevelopment/gemma-4-12B-it-qat-q4_0-gguf:latest":     (2.61, 43.1, 29.38),
    "xentriom/gemma-4-12B-agentic-fable5-composer2.5-v2:latest": (2.29, 26.8, 14.01),
    "fredrezones55/Qwopus3.5:4b":                                (2.38, 88.8, 50.11),
}
PRACTICAL_BEST = 53.02  # qwen3.5:4b — clean default to beat


def main() -> int:
    results: list[dict] = []
    total = len(CANDIDATES) * len(bd.TESTS)
    done = 0
    for m in CANDIDATES:
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
                                "output_head": r["output"][:220]})
            bd.unload(m)
            with (OUT / "all.jsonl").open("a") as f:
                f.write(json.dumps(results[-1]) + "\n")

    print(f"\n{'='*94}\nCANDIDATES — COMPOSITE vs WINNERS\n{'='*94}", flush=True)
    print(f"{'model':<34}{'Q':>5}{'tok/s':>8}{'vram':>7}{'COMP':>7}  verdict", flush=True)
    rows = []
    for m in CANDIDATES:
        ok = [r for r in results if r["model"] == m and r["status"] == "ok"]
        if not ok:
            print(f"{m[:33]:<34}  (all errored)", flush=True)
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
        print(f"{r['model'][:33]:<34}{r['Q']:>5}{r['tps']:>8}{r['vram']:>7}{r['COMP']:>7}  {v}", flush=True)
    print(f"\n--- known winners (reference) ---", flush=True)
    for m, (q, s, c) in WINNERS.items():
        print(f"{m[:33]:<34}{q:>5}{s:>8}{'':>7}{c:>7}", flush=True)

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
            print(f"  {m[:40]:<40} Q={q:.2f} {s:5.1f}tok/s ({len(rs)})", flush=True)

    (OUT / "all.json").write_text(json.dumps(results, indent=2))
    (OUT / "summary.json").write_text(json.dumps({"rows": rows}, indent=2))
    print(f"\nSaved: {OUT/'all.json'}", flush=True)
    print("BENCH_CANDIDATES_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
