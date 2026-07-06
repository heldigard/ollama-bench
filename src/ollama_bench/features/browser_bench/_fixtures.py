"""PIL fixture builders for browser-model-bench.

Deterministic synthetic screenshots (login forms, error pages, tables, charts,
dashboards, articles) used as T1/T2 vision ground truth. Pillow is imported
lazily so the text-only ``SNAPSHOT_*`` fixtures (lives in ``_bench_data``) can be
used by lightweight parser tests without the optional visual dependency.
"""

from __future__ import annotations

from collections.abc import Callable
from io import BytesIO
from pathlib import Path

__all__ = [
    "QUICK_FIXTURES",
    "RIGOROUS_FIXTURES",
    "build_fixtures",
    "fx_article_long",
    "fx_chart_pie",
    "fx_dashboard_complex",
    "fx_error_404",
    "fx_error_500",
    "fx_login_github",
    "fx_login_microsoft",
    "fx_table_financial",
]

_PIL_MODULES = None


def _import_pil_modules():
    """Import Pillow or exit with an install hint."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "browser-model-bench requires Pillow. Install it with: python3 -m pip install Pillow"
        ) from exc
    return Image, ImageDraw, ImageFont


def _pil():
    """Import Pillow only when image fixtures are actually built.

    The parser tests import this module only for the text ``SNAPSHOT_*``
    fixtures. Keeping Pillow lazy means those fast tests do not need optional
    visual-benchmark dependencies.
    """
    global _PIL_MODULES
    if _PIL_MODULES is None:
        _PIL_MODULES = _import_pil_modules()
    return _PIL_MODULES


_FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
)


def _load_truetype(font_module, path: str, size: int):
    """Return a TrueType font for ``path`` or ``None`` if unavailable."""
    if not Path(path).exists():
        return None
    try:
        return font_module.truetype(path, size)
    except OSError:
        return None


def _font(size: int = 18):
    _, _, ImageFont = _pil()
    for p in _FONT_PATHS:
        font = _load_truetype(ImageFont, p, size)
        if font is not None:
            return font
    return ImageFont.load_default()


def _save(img) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def fx_login_microsoft() -> bytes:
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "white")
    d = ImageDraw.Draw(img)
    f_h1 = _font(28)
    f = _font(18)
    f_s = _font(14)
    d.rectangle([0, 0, 1024, 48], fill="#0067b8")
    d.text((30, 12), "Microsoft", fill="white", font=f_h1)
    d.rectangle([312, 130, 712, 580], outline="#ccc", width=1)
    d.text((340, 160), "Sign in", fill="#333", font=f_h1)
    d.text((340, 220), "Email", fill="#666", font=f_s)
    d.rectangle([340, 240, 684, 280], outline="#888", width=1)
    d.text((360, 250), "user@contoso.com", fill="#222", font=f)
    d.text((340, 300), "Password", fill="#666", font=f_s)
    d.rectangle([340, 320, 684, 360], outline="#888", width=1)
    d.text((360, 330), "********", fill="#222", font=f)
    d.rectangle([340, 410, 580, 460], fill="#0067b8")
    d.text((430, 425), "Next", fill="white", font=f_h1)
    return _save(img)


def fx_login_github() -> bytes:
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "#f6f8fa")
    d = ImageDraw.Draw(img)
    f_h1 = _font(28)
    f = _font(18)
    f_s = _font(14)
    d.text((30, 30), "GitHub", fill="#24292f", font=f_h1)
    d.rectangle([312, 130, 712, 580], outline="#d0d7de", width=1, fill="white")
    d.text((340, 160), "Sign in to GitHub", fill="#24292f", font=f_h1)
    d.text((340, 220), "Username or email address", fill="#57606a", font=f_s)
    d.rectangle([340, 240, 684, 280], outline="#d0d7de", width=1)
    d.text((360, 250), "octocat", fill="#24292f", font=f)
    d.text((340, 300), "Password", fill="#57606a", font=f_s)
    d.text((620, 300), "Forgot password?", fill="#0969da", font=f_s)
    d.rectangle([340, 320, 684, 360], outline="#d0d7de", width=1)
    d.text((360, 330), "**********", fill="#24292f", font=f)
    d.rectangle([340, 410, 580, 460], fill="#2da44e")
    d.text((430, 425), "Sign in", fill="white", font=f_h1)
    return _save(img)


def fx_error_404() -> bytes:
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "white")
    d = ImageDraw.Draw(img)
    f_h1 = _font(140)
    f_h2 = _font(28)
    f = _font(18)
    d.text((380, 200), "404", fill="#1f2937", font=f_h1)
    d.text((420, 380), "Page not found", fill="#374151", font=f_h2)
    d.text((360, 430), "The page you requested could not be located.", fill="#6b7280", font=f)
    d.rectangle([430, 500, 590, 550], outline="#3b82f6", width=2)
    d.text((480, 510), "Home", fill="#3b82f6", font=f_h2)
    return _save(img)


def fx_error_500() -> bytes:
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "#fafafa")
    d = ImageDraw.Draw(img)
    f_h1 = _font(80)
    f_h2 = _font(24)
    f = _font(16)
    d.text((430, 180), "500", fill="#d83b01", font=f_h1)
    d.text((380, 300), "Server Error", fill="#333", font=f_h2)
    d.text(
        (360, 350), "The server encountered an internal error and was unable", fill="#555", font=f
    )
    d.text((360, 372), "to complete your request. Please try again later.", fill="#555", font=f)
    d.rectangle([440, 440, 580, 480], outline="#0078d4", width=2)
    d.text((470, 448), "Retry", fill="#0078d4", font=f_h2)
    return _save(img)


def fx_table_financial() -> bytes:
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "white")
    d = ImageDraw.Draw(img)
    f_h = _font(20)
    f = _font(16)
    f_s = _font(14)
    d.text((30, 25), "Quarterly Revenue 2026", fill="#1f2937", font=f_h)
    cols = ["", "Q1", "Q2", "Q3", "Q4"]
    rows = [
        ["Revenue", "23.4M", "27.1M", "31.0M", "35.6M"],
        ["Costs", "18.2M", "19.5M", "21.8M", "24.0M"],
        ["Profit", "5.2M", "7.6M", "9.2M", "11.6M"],
    ]
    y = 80
    x = [30, 200, 320, 440, 560]
    for ci, c in enumerate(cols):
        d.text((x[ci], y), c, fill="#374151", font=f_h)
    y += 35
    d.line([30, y, 700, y], fill="#9ca3af", width=2)
    y += 10
    for row in rows:
        for ci, cell in enumerate(row):
            d.text((x[ci], y), cell, fill="#1f2937", font=f)
        y += 30
        d.line([30, y, 700, y], fill="#e5e7eb", width=1)
        y += 10
    d.text((30, 580), "Source: internal finance — confidential", fill="#9ca3af", font=f_s)
    return _save(img)


def fx_chart_pie() -> bytes:
    """Pure visual pie chart, no readable labels — tests hallucination."""
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "white")
    d = ImageDraw.Draw(img)
    cx, cy, r = 512, 320, 180
    # 4 wedges: 40%, 30%, 20%, 10%
    wedges = [
        ("#3b82f6", 0.40),
        ("#ef4444", 0.30),
        ("#22c55e", 0.20),
        ("#f59e0b", 0.10),
    ]
    angle = -90  # start at top
    for color, frac in wedges:
        sweep = int(360 * frac)
        d.pieslice(
            [cx - r, cy - r, cx + r, cy + r],
            start=angle,
            end=angle + sweep,
            fill=color,
            outline="white",
            width=2,
        )
        angle += sweep
    return _save(img)


def fx_dashboard_complex() -> bytes:
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "#f9fafb")
    d = ImageDraw.Draw(img)
    f_h = _font(22)
    f_b = _font(28)
    f = _font(14)
    f_s = _font(12)
    d.text((30, 25), "Dashboard", fill="#111827", font=f_h)
    # KPI cards
    cards = [
        ("Active Users", "12,847", "+5.2%"),
        ("Revenue", "$48,200", "+12.3%"),
        ("Conversion", "3.4%", "-0.1%"),
    ]
    for i, (label, val, delta) in enumerate(cards):
        x = 30 + i * 320
        d.rectangle([x, 80, x + 300, 200], outline="#e5e7eb", width=1, fill="white")
        d.text((x + 16, 95), label, fill="#6b7280", font=f)
        d.text((x + 16, 120), val, fill="#111827", font=f_b)
        d.text((x + 16, 170), delta, fill="#22c55e" if "+" in delta else "#ef4444", font=f)
    # Alerts section
    d.text((30, 230), "Alerts", fill="#111827", font=f_h)
    alerts = [
        ("1", "Spike in 5xx on api-gateway-prod"),
        ("2", "Disk usage > 80% on db-02"),
        ("3", "Deployment failed for checkout-svc"),
    ]
    for i, (n, msg) in enumerate(alerts):
        y = 270 + i * 35
        d.ellipse([40, y + 4, 60, y + 24], fill="#ef4444" if i == 0 else "#f59e0b")
        d.text((50, y + 6), n, fill="white", font=f_s)
        d.text((80, y), msg, fill="#374151", font=f)
    return _save(img)


def fx_article_long() -> bytes:
    Image, ImageDraw, _ = _pil()
    img = Image.new("RGB", (1024, 640), "white")
    d = ImageDraw.Draw(img)
    f_h = _font(24)
    f_h2 = _font(18)
    f = _font(13)
    f_s = _font(11)
    d.text((30, 25), "On Retrieval-Augmented Generation in 2026", fill="#111827", font=f_h)
    d.text((30, 70), "by J. Smith — published March 2026", fill="#9ca3af", font=f_s)
    body = [
        "Retrieval-augmented generation (RAG) has become the dominant",
        "pattern for grounding LLM responses in private knowledge. The core",
        "idea is straightforward: at query time, an embedding model retrieves",
        "the most relevant chunks from a vector index, then a transformer-based",
        "generator conditions on those chunks.",
        "",
        "Three trends shaped 2026: (1) hybrid retrieval mixing BM25 and dense",
        "embedding scores, (2) per-tenant reranking with cross-encoders,",
        "and (3) late chunking via token-level overlap windows.",
    ]
    y = 110
    for line in body:
        if line == "":
            y += 12
            continue
        weight = f_h2 if line.startswith(("Three", "(1)", "(2)", "(3)")) else f
        d.text((30, y), line, fill="#1f2937", font=weight)
        y += 26
    return _save(img)


QUICK_FIXTURES = {
    # Keys MUST match GT dict keys (score_t1 looks up GT[fname]).
    "login_microsoft": (fx_login_microsoft, "login_form"),
    "error_500": (fx_error_500, "error_500"),
}
RIGOROUS_FIXTURES = {
    "login_microsoft": (fx_login_microsoft, "login_form"),
    "login_github": (fx_login_github, "login_form"),
    "error_404": (fx_error_404, "error_404"),
    "error_500": (fx_error_500, "error_500"),
    "table_financial": (fx_table_financial, "table"),
    "chart_pie": (fx_chart_pie, "chart"),
    "dashboard_complex": (fx_dashboard_complex, "dashboard"),
    "article_long": (fx_article_long, "article"),
}


def build_fixtures(
    fixture_builders: dict[str, tuple[Callable[[], bytes], str]],
) -> dict[str, tuple[bytes, str]]:
    return {name: (builder(), cls) for name, (builder, cls) in fixture_builders.items()}
