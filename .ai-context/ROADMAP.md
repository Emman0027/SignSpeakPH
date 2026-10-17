# ROADMAP.md

Current, living TODO list. Keep this short and *current* — when
something is done, delete it from here (the historical record lives in
CHANGELOG.md, not here).

## Next steps
- (example) Decide landmark-overlay approach: Option A (return coords,
  draw client-side) vs Option B (return annotated JPEG)
- (example) Run final evaluation (accuracy_score, confusion_matrix) on
  the real X_test/y_test for the reportable accuracy number

## Open decisions
- (example) Option A vs B above — not yet chosen

## Blocked / waiting on
- (example) nothing right now


## Capstone evaluation gates
- Gate 1, Alpha-ready: all 8 Table 2 areas pass with logged evidence; held-out accuracy >=90% with confusion matrix and misclassification list; fps and latency measured on the deployed host; test suite and CI green on improv; no P1 task open.
- Gate 2, Beta-ready: stable public URL; beta test plan; evaluation forms for Table 4 (IT experts) and Table 5 (users); a script that scores responses using Table 6.
- Gate 3, Expert-ready: no known high-severity issue in the 7 Table 4 characteristics; manuscript and code agree; vocabulary listed in the manuscript.