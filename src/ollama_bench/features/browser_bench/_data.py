"""Static ground truth, snapshots, and prompts for browser-model-bench.

Pure data: T1 OCR ground truth, T2 class labels, T3/T4 accessibility-tree
snapshots, T3 expected change words, and the T1-T4 prompt templates. Lives
apart from ``_bench_fixtures`` so the text-only scenarios (T3/T4) can be
exercised without importing Pillow.
"""

from __future__ import annotations

__all__ = [
    "ALL_CLASSES",
    "CLASS_GT",
    "GT",
    "P_T1",
    "P_T2",
    "P_T3_PROMPTS",
    "P_T4_PROMPTS",
    "SNAPSHOT_1",
    "SNAPSHOT_2",
    "SNAPSHOT_BASE",
    "SNAPSHOT_BASE_SEARCH",
    "SNAPSHOT_LIST_VIEW",
    "SNAPSHOT_LOADING",
    "SNAPSHOT_TOP_OF_TABLE",
    "T3_CHANGE_WORDS",
    "T3_MAJOR_AFTER",
    "T3_MEDIUM_AFTER",
]

# =============================================================================
# Fixture ground truth — words that MUST be in the OCR output for recall;
# and forbidden-words list (must NOT appear) for hallucination scoring.
# =============================================================================
GT = {
    "login_microsoft": {
        "must_contain": ["sign in", "email", "password", "next"],
        "must_not": ["github", "facebook", "google"],
    },
    "login_github": {
        "must_contain": ["sign in", "username", "password", "forgot"],
        "must_not": ["microsoft", "contoso"],
    },
    "error_404": {
        "must_contain": ["404", "page", "found", "home"],
        "must_not": ["500", "server error"],
    },
    "error_500": {
        "must_contain": ["500", "server", "error", "retry"],
        "must_not": ["404", "not found"],
    },
    "table_financial": {
        "must_contain": ["q1", "q2", "q3", "q4", "revenue", "23.4", "27.1", "31.0", "35.6"],
        "must_not": ["login", "sign in"],
    },
    "chart_pie": {
        # Pure visual chart, no readable text. Test if model hallucinates.
        "must_contain": [],
        "must_not": ["chart", "graph", "pie", "percentage", "sales", "revenue"],
    },
    "dashboard_complex": {
        "must_contain": ["dashboard", "active users", "12,847", "$48,200", "alerts", "3"],
        "must_not": [],
    },
    "article_long": {
        "must_contain": ["retrieval-augmented", "embedding", "vector", "transformer", "2026"],
        "must_not": [],
    },
}

# T2 expected class per fixture
CLASS_GT = {
    "login_microsoft": "login_form",
    "login_github": "login_form",
    "error_404": "error_404",
    "error_500": "error_500",
    "chart_pie": "chart",
    "dashboard_complex": "dashboard",
    "table_financial": "table",
    "article_long": "article",
}
ALL_CLASSES = [
    "login_form",
    "error_404",
    "error_500",
    "success_page",
    "loading_spinner",
    "chart",
    "dashboard",
    "article",
    "table",
    "blank",
]

# =============================================================================
# Prompts (rigorous versions — cleaner, more strict)
# =============================================================================
P_T1 = (
    "Extract EVERY visible text string in the screenshot in reading order.\n"
    "Rules:\n"
    "  - One text string per line, plain text, no markdown, no commentary\n"
    "  - DO NOT invent text that is not visible\n"
    "  - DO NOT describe layout, colors, or visual style\n"
    "  - If text is partially cut off, write [partial]\n"
    "  - If a region is purely visual with no readable text, OMIT it entirely\n"
    "Begin now:"
)
P_T2 = (
    "Classify this webpage screenshot into EXACTLY one of these labels:\n"
    + "\n".join(f"  - {c}" for c in ALL_CLASSES)
    + "\nReply with ONLY the label, no other text, no punctuation."
)

# Snapshots for T3 medium + major + T4 scenarios
SNAPSHOT_BASE = """- banner "App" [ref=e1]
- navigation:
  - link "Home" [ref=e2]
  - link "Customers" [ref=e3]
  - link "Reports" [ref=e4]
- main:
  - heading "Active customers" [ref=e5]
  - table:
    - row:
      - cell "Acme Corp" [ref=e6]
      - cell "42" [ref=e7]
      - button "View" [ref=e8]
    - row:
      - cell "Beta Ltd" [ref=e9]
      - cell "17" [ref=e10]
      - button "View" [ref=e11]
- contentinfo "© 2026" [ref=e12]"""
SNAPSHOT_1 = SNAPSHOT_BASE
SNAPSHOT_2 = """- banner "App" [ref=e1]
- navigation:
  - link "Home" [ref=e2]
  - link "Customers" [ref=e3]
  - link "Reports" [ref=e4]
- main:
  - heading "Active customers" [ref=e5]
  - alert "Failed to load customers: timeout after 5s" [ref=e6]
  - button "Retry" [ref=e7]
- contentinfo "© 2026" [ref=e8]"""
SNAPSHOT_BASE_SEARCH = """- banner "Shop" [ref=e1]
- main:
  - heading "Search orders" [ref=e2]
  - searchbox "Enter order ID" [ref=e3]
  - button "Search" [ref=e4]
- contentinfo "© 2026" [ref=e5]"""
SNAPSHOT_TOP_OF_TABLE = """- banner "Pricing" [ref=e1]
- main:
  - heading "Plans" [ref=e2]
  - table:
    - row:
      - cell "Starter" [ref=e3]
      - cell "$9/mo" [ref=e4]
    - row:
      - cell "Pro" [ref=e5]
      - cell "$29/mo" [ref=e6]
    - row:
      - cell "Enterprise" [ref=e7]
      - cell "Contact us" [ref=e8]
  - paragraph "Pricing scales with seats and includes..." [ref=e9]
- contentinfo "© 2026" [ref=e10]"""
SNAPSHOT_LOADING = """- banner "App" [ref=e1]
- main:
  - heading "Loading..." [ref=e2]
  - progressbar "indeterminate" [ref=e3]
- status "Fetching data" [ref=e4]"""
SNAPSHOT_LIST_VIEW = """- banner "Library" [ref=e1]
- main:
  - heading "My items" [ref=e2]
  - list:
    - listitem "Item A" [ref=e3]
    - listitem "Item B" [ref=e4]
    - listitem "Item C" [ref=e5]
    - listitem "Item D" [ref=e6]
    - listitem "Item E" [ref=e7]"""

# T3 medium + major scenarios (built from SNAPSHOT_1)
T3_MEDIUM_AFTER = """- banner "App" [ref=e1]
- navigation:
  - link "Home" [ref=e2]
  - link "Customers" [ref=e3]
  - link "Reports" [ref=e4]
  - link "Settings" [ref=e15]
- main:
  - heading "Active customers (filtered)" [ref=e5]
  - searchbox "Filter by name" [ref=e13]
  - table:
    - row:
      - cell "Acme Corp" [ref=e6]
      - cell "42" [ref=e7]
      - button "View" [ref=e8]
  - paragraph "Showing 1 of 2 results" [ref=e14]
- contentinfo "© 2026" [ref=e12]"""
T3_MAJOR_AFTER = """- banner "App v2" [ref=e1]
- navigation:
  - link "Dashboard" [ref=e2]
  - link "Customers" [ref=e3]
  - link "Reports" [ref=e4]
  - link "Settings" [ref=e15]
  - link "Admin" [ref=e16]
- main:
  - heading "Customers (25)" [ref=e5]
  - searchbox "Filter" [ref=e13]
  - button "Export CSV" [ref=e17]
  - table:
    - row:
      - cell "Acme Corp" [ref=e6]
      - cell "42" [ref=e7]
      - cell "Active" [ref=e18]
      - button "View" [ref=e8]
    - row:
      - cell "Beta Ltd" [ref=e9]
      - cell "17" [ref=e10]
      - cell "Trial" [ref=e19]
      - button "View" [ref=e11]
    - row:
      - cell "Gamma Inc" [ref=e20]
      - cell "8" [ref=e21]
      - cell "Churned" [ref=e22]
      - button "View" [ref=e23]
  - paragraph "Last updated 2 minutes ago" [ref=e24]
- contentinfo "© 2026" [ref=e12]"""

T3_CHANGE_WORDS = {
    "minor": {"timeout", "retry", "alert", "failed", "load"},
    "medium": {"filtered", "settings", "filter", "showing", "results"},
    "major": {
        "v2",
        "dashboard",
        "admin",
        "export",
        "active",
        "trial",
        "churned",
        "gamma",
        "8",
        "last updated",
    },
}

# Now fill P_T3_PROMPTS with actual snapshots
P_T3_PROMPTS = {
    "minor": (
        "Two accessibility-tree snapshots, before and after. ONE change occurred.\n"
        "Identify the EXACT change in 1 bullet.\n\n"
        f"BEFORE:\n{SNAPSHOT_1}\n\nAFTER:\n{SNAPSHOT_2}"
    ),
    "medium": (
        "Two accessibility-tree snapshots, before and after. List ALL changes in 4 bullets.\n\n"
        f"BEFORE:\n{SNAPSHOT_1}\n\nAFTER:\n{T3_MEDIUM_AFTER}"
    ),
    "major": (
        "Two accessibility-tree snapshots, before and after. List ALL changes in 8 bullets.\n\n"
        f"BEFORE:\n{SNAPSHOT_1}\n\nAFTER:\n{T3_MAJOR_AFTER}"
    ),
}

# Now fill P_T4_PROMPTS with actual snapshots
P_T4_PROMPTS = {
    "click": (
        "Goal: 'Find and open the customer detail page for Acme Corp.'\n\n"
        f"SNAPSHOT:\n{SNAPSHOT_1}\n\nNext single tool call (JSON only):"
    ),
    "fill": (
        "Goal: 'Search for the order with ID 12345.'\n\n"
        f"SNAPSHOT:\n{SNAPSHOT_BASE_SEARCH}\n\nNext single tool call (JSON only):"
    ),
    "scroll": (
        "Goal: 'Read the full pricing table on this page.'\n\n"
        f"SNAPSHOT:\n{SNAPSHOT_TOP_OF_TABLE}\n\nNext single tool call (JSON only):"
    ),
    "wait": (
        "Goal: 'Continue once the loading indicator is gone.'\n\n"
        f"SNAPSHOT:\n{SNAPSHOT_LOADING}\n\nNext single tool call (JSON only):"
    ),
    "eval": (
        "Goal: 'Get the count of currently visible items.'\n\n"
        f"SNAPSHOT:\n{SNAPSHOT_LIST_VIEW}\n\nNext single tool call (JSON only):"
    ),
    "recovery": (
        "Goal: 'Find and open the customer detail page for Acme Corp.'\n"
        "(Last action returned an error — page now shows a retry prompt.)\n\n"
        f"SNAPSHOT:\n{SNAPSHOT_2}\n\nNext single tool call (JSON only):"
    ),
}
