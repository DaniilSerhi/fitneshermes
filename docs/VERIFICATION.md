# Verification record

Preparation checks were performed locally using Python 3.14.6. No private content was submitted to an external scanner. The commands below run from the public repository directory.

## Reproducible checks

| Command | Observed result |
|---|---|
| `python3 scripts/run_demo.py` | Exit 0; synthetic report, structured result and dated journal written |
| `python3 -m unittest discover -s tests -v` | 15 tests passed |
| `python3 scripts/check_public.py` | Publication inventory, local Markdown file links, empty example environment values and focused privacy patterns passed |
| `python3 scripts/run_demo.py --scenario missing --output demo-output-missing` | Exit 0; unavailable activity yields no estimate |
| `python3 scripts/run_demo.py --scenario stale --output demo-output-stale` | Exit 0; stale activity yields no estimate |
| `python3 scripts/run_demo.py --scenario date-mismatch` | Intentional exit 2; date mismatch rejected before output writes |

Tests cover English totals without subtotal double counting, German UTF-16 input with decimal commas, invalid headers, complete arithmetic, synthetic markers, missing nutrition, mismatched/future dates, invalid steps, nonfinite/negative coefficients, missing/stale activity, valid zero steps, journal replay and correction, expected end-to-end artifacts, and rejection without output creation.

The complete report and JSON are compared with committed expected artifacts in the end-to-end test. The readable Markdown report and documentation were inspected as text. There are no screenshots, images, fonts, PDFs or office documents in the publication set. Browser rendering of the README and Mermaid diagram on GitHub was not tested.

## Publication boundary

[PUBLIC_FILES.txt](../PUBLIC_FILES.txt) names the exact 22 files proposed for the first commit, including hidden configuration files. The checker rejects missing or unlisted publication files and symlinks. Generated demo directories, Python caches and Git metadata are outside its publication scope; `.gitignore` alone is not used as evidence of sanitization. Generated outputs and caches from preparation were removed after verification; reference outputs remain under `examples/expected/`.

A separate local comparison checked selected public text against available private credential values. It reported no matches without printing those values. The copied upstream license was compared byte for byte with the working source. The parser differs from its working source only in the documented explanatory comment translation.

No original Git directory was copied and no new Git repository was initialized. There is no new index or commit history to inspect. No repository creation, push, deployment change or credential rotation was performed.

## Not established by these checks

The optional GitHub Actions workflow targets Python 3.11 and 3.12, but those CI jobs have not run. Local execution was verified only on Python 3.14.6. Live API authentication, model behavior, Telegram delivery and concurrent persistence were not exercised. The parser's standalone URL input is outside the offline verification scope.

This preparation does not establish the absence of secrets in previously published repositories or their histories. It checks this newly assembled publication set. Project-specific reuse licensing remains an owner decision; no new license was assigned.
