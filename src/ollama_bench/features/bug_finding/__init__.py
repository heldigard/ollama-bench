"""bug_finding — diff-review / bug-finding task (6th canonical task).

Why a separate slice: bug-finding needs a DIFF with known bugs + a recall
scorer (count of bugs found), which doesn't fit the prose-output pattern of
the other 5 tasks. composer Q8_0 historically won this (recall 0.97).
"""