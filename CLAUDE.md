# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make it pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## Project Goal: pass the capstone evaluation
SignSpeakPH must be ready for the three evaluations defined in the capstone manuscript:
1. Alpha testing (internal, Table 2), 8 areas: environment setup, camera input, landmark detection, gesture classification, text generation, voice output, real-time pipeline, UI. Each area needs a pass/fail entry with evidence.
2. Beta testing (Table 3): IT professionals and real users (including Deaf/hard-of-hearing users) test end-to-end, camera, performance, functionality, and acceptance.
3. ISO/IEC 25010:2023 evaluation: IT experts rate 7 characteristics (Functional Suitability, Performance Efficiency, Usability, Reliability, Security, Maintainability, Portability); users rate 4 (Functional Suitability, Performance Efficiency, Usability, Reliability). 5-point Likert; target mean 4.51+ (Excellent), minimum 3.51 (Very Good).
Manuscript targets: >=90% classification accuracy, >=15 fps, Filipino text and voice output, standard webcam only.
Rules: prefer work that moves one of these gates (see .ai-context/ROADMAP.md and TASKS.md). Never claim something works without evidence (a test, a measurement, or a log). If the code and the manuscript disagree, report it and ask which should change; never edit the manuscript text itself.

## Already fixed: do not redo or duplicate (as of 2026-10-10)
- Before adding any route, search app.py for it. Existing routes: /, /health, /config, /signs, /predict_batch, /feedback (POST, PUT and DELETE by id), /metrics. A duplicate /signs once crashed startup.
- src/config/settings.py BASE_DIR points to the repo root. Model files live in data/models/production; action_v1.0.0.tflite is tracked and is regenerated with scripts/export_tflite.py.
- requirements.txt: keep mediapipe==0.10.21 (later releases removed mp.solutions) and numpy<2. Windows uses tensorflow, Linux uses tflite-runtime. render.yaml swaps OpenCV for the headless build.
- SIGN_INFO in src/constants.py feeds /signs; its labels must match labels_v1.0.0.json (tests/unit/test_signs.py checks this).
- Do not run the full pytest suite yet: tests/unit/test_endpoints.py writes to the real data/feedback/feedback.json. Running tests/unit/test_signs.py and tests/unit/test_config_and_feedback_id.py is safe.
- Keep each file's existing line endings (CRLF).
- Not yet verified: Docker build, Render deploy, browser flow. Never mark these done without evidence.