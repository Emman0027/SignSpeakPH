# Graph Report - SignSpeakPH  (2026-09-24)

## Corpus Check
- 31 files · ~51,188 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 10, .toml 2, .jsonl 2)

## Summary
- 129 nodes · 134 edges · 21 communities (12 shown, 9 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `84f49dbe`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- scan_index.py
- route
- SignSpeakPH Project Structure
- app.py
- $(date '+%Y-%m-%d %H:%M:%S')
- PROJECT_INDEX.md — example (SignSpeakPH)
- file_index.sh
- yuki-dori-ready.sh
- CLAUDE.md
- pull_request_template.md
- yuki_status.sh
- SignSpeakPH - Batch capture version
- ROADMAP.md
- Scripts Directory
- TASKS.md
- CHANGELOG.md

## God Nodes (most connected - your core abstractions)
1. `SignSpeakPH Project Structure` - 8 edges
2. `PROJECT_INDEX.md — example (SignSpeakPH)` - 7 edges
3. `predict_batch()` - 6 edges
4. `$(date '+%Y-%m-%d %H:%M:%S')` - 6 edges
5. `SignSpeakPH - Batch capture version` - 5 edges
6. `Key Improvements` - 5 edges
7. `file_index.sh script` - 4 edges
8. `main()` - 4 edges
9. `mediapipe_detection()` - 4 edges
10. `extract_keypoints()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `predict_batch()` --calls--> `extract_keypoints()`  [EXTRACTED]
  app.py → src/utils/mediapipe_utils.py
- `predict_batch()` --calls--> `mediapipe_detection()`  [EXTRACTED]
  app.py → src/utils/mediapipe_utils.py

## Import Cycles
- None detected.

## Communities (21 total, 9 thin omitted)

### Community 0 - "scan_index.py"
Cohesion: 0.25
Nodes (10): argparse, hashlib, fingerprint(), load_state(), main(), scan_index.py — incremental repo state tracker. Purpose: let an AI agent know…, sha256_of(), walk_repo() (+2 more)

### Community 1 - "route"
Cohesion: 0.25
Nodes (8): delete_feedback(), handle_feedback(), index(), Handle customer satisfaction feedback, Update existing feedback, Delete existing feedback, update_feedback(), route

### Community 2 - "SignSpeakPH Project Structure"
Cohesion: 0.15
Nodes (12): 1. **Separation of Concerns**, 2. **Improved Configuration Management**, 3. **Enhanced ML Workflow**, 4. **Better Development Workflow**, Directory Structure, Feedback Storage, Getting Started, Key Improvements (+4 more)

### Community 3 - "app.py"
Cohesion: 0.10
Nodes (25): decode_base64_image(), predict_batch(), SignSpeakPH - Flask backend (BATCH version) Fixes both the speed problem AND an…, Convert a data:image/jpeg;base64,... string from the browser into an OpenCV…, Receives all SEQUENCE_LENGTH frames at once (captured locally by the browser at…, base64, load_model_config(), Configuration management for SignSpeakPH (+17 more)

### Community 4 - "$(date '+%Y-%m-%d %H:%M:%S')"
Cohesion: 0.18
Nodes (10): $(date '+%Y-%m-%d %H:%M:%S'), PROJECT_INDEX.md — example (SignSpeakPH), 🏗️ Project Overview, 📊 Project Status (Project-Dori), 📚 Quick Reference, 📝 Recent Changes, 🎯 Today's Focus (from TODOs), 🚀 Yuki-Dori Session Briefing (+2 more)

### Community 5 - "PROJECT_INDEX.md — example (SignSpeakPH)"
Cohesion: 0.25
Nodes (7): Decisions log, Key files/folders (what each is for — not what's inside it), Known limitations (don't re-discover these — they're already known), Model architecture (stable — rarely needs re-reading), PROJECT_INDEX.md — example (SignSpeakPH), Tech stack, What this is

### Community 6 - "file_index.sh"
Cohesion: 0.70
Nodes (4): build_index(), search_index(), file_index.sh script, show_help()

### Community 8 - "CLAUDE.md"
Cohesion: 0.33
Nodes (4): 1. Think Before Coding, 2. Simplicity First, 3. Surgical Changes, 4. Goal-Driven Execution

### Community 9 - "pull_request_template.md"
Cohesion: 0.33
Nodes (5): Checklist, Related Issue, Screenshots (if applicable):, Summary, Type of change

### Community 16 - "SignSpeakPH - Batch capture version"
Cohesion: 0.33
Nodes (5): 1. Copy your trained files here, 2. Test locally, 3. Deploy, SignSpeakPH - Batch capture version, What to expect

### Community 17 - "ROADMAP.md"
Cohesion: 0.40
Nodes (3): Blocked / waiting on, Next steps, Open decisions

### Community 18 - "Scripts Directory"
Cohesion: 0.40
Nodes (4): Available Scripts, file_index.sh, Scripts Directory, Usage

## Knowledge Gaps
- **45 isolated node(s):** `yuki_status.sh script`, `YYYY-MM-DD`, `What this is`, `Tech stack`, `Key files/folders (what each is for — not what's inside it)` (+40 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 81 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `predict_batch()` connect `app.py` to `route`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `handle_feedback()` connect `route` to `app.py`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **What connects `yuki_status.sh script`, `YYYY-MM-DD`, `What this is` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._