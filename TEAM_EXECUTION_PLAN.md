# Project ARES – Member Execution & Responsibility Document

Comprehensive, step-by-step task breakdown for each team member (Abdul Rauf, Asaad Bin Amir, Basim Khurram Gul). Includes phases, dependencies, acceptance criteria, expected outcomes, Copilot prompt templates, quality gates, risk mitigation, and stretch goals.

---
## 0. Purpose of This Document
This document is the single source of truth for "who does what" and "what does done look like" for Project ARES. It answers:
- What EXACTLY each member must deliver (step-by-step)
- The order of operations (dependencies & sequencing)
- The acceptance criteria and testable outcomes
- When to integrate, log, and demo features
- Stretch tasks if time remains after MVP

Use this to coordinate work and author precise Copilot prompts.

---
## 1. Roles (Canonical)
| Member | GitHub Username | Focus | Primary Folders | Secondary Tasks |
|--------|-----------------|-------|-----------------|-----------------|
| Abdul Rauf | @abdulraufdev | Search & Tactical Algorithms | `algorithms/` | Heuristics tuning, performance experiments |
| Asaad Bin Amir | (add username) | Visuals, HUD, Sound | `core/graphics.py`, `core/sound_manager.py`, `assets/` | Readability polish, iconography |
| Basim Khurram Gul | @Basim-Gul | Gameplay integration, Map & Logging, CI/Repo | `core/`, `.github/`, root | Coordination, documentation, branch hygiene |

---
## 2. Phased Plan Overview (Turbo 10–14 Day Path)
Day ranges are flexible; treat as guidance.

| Phase | Days | Focus | Owner Lead | Integration Check |
|-------|------|-------|------------|-------------------|
| P1 | 1–2 | Skeleton runs; algorithms validated; basic HUD live | Basim + Abdul + Asaad | Game window opens; BFS path draws |
| P2 | 3–4 | Advanced search (DLS, IDS, BDS); Map loader & switching; Sound manager stub | Abdul + Basim + Asaad | Key `M` cycles maps; sounds do not crash |
| P3 | 5–7 | Hill Climb implemented; HUD metrics refined; logging operational | Abdul + Basim + Asaad | CSV rows append after path compute |
| P4 | 8–10 | Polish: heuristics cycle, neighbor toggle, minor SFX/UI, stability | All | Demo GIF recorded |
| Buffer | 11–14 | Optional Beam / SA stubs; charts; report; refactors | All | Stretch features isolated |

---
## 3. Detailed Task Breakdown by Member
Each task lists: ID, Description, Steps, Dependencies, Acceptance Criteria (AC), Expected Outcome (EO).

### 3.1 Abdul Rauf – Algorithms Lead

#### A1 – Implement Depth-Limited Search (DLS)
- Steps:
  1. Create `algorithms/dls.py` with `find_path(grid, start, goal, depth_limit: int = 50)`.
  2. Use DFS-style recursion or iterative stack storing (node, depth).
  3. Do NOT expand children when `depth == depth_limit`.
  4. Track `nodes_expanded` only when popping for expansion.
  5. Reconstruct path via `came_from`; if goal not found return `([], Stats)`. 
  6. Add docstring + type hints.
  7. Add unit test in `tests/test_algorithms.py` for case: goal beyond limit returns empty.
- Dependencies: Existing `Stats`, `Grid`.
- AC: Returns valid path when depth sufficient; fails gracefully when limit too low.
- EO: Deterministic path length equals BFS on unweighted grid where reachable within limit.

#### A2 – Implement Iterative Deepening Search (IDS)
- Steps:
  1. Create `algorithms/ids.py` calling `dls.find_path` for limits 0..max_depth.
  2. Accumulate `nodes_expanded` across attempts.
  3. Return first non-empty path.
  4. Docstring & type hints; note performance caveat.
  5. Tests: On simple grid, IDS path == BFS path; nodes_expanded >= BFS.
- Dependencies: A1.
- AC: Stops immediately when path found; Stats reflect aggregated expansions.
- EO: Path identical to BFS for uniform cost grid.

#### A3 – Implement Bidirectional BFS (BDS)
- Steps:
  1. Create `algorithms/bds.py` with symmetric frontiers.
  2. Maintain `came_from_start`, `came_from_goal`.
  3. When intersection occurs, stitch path: start->meet + reversed(goal->meet).
  4. Track combined `nodes_expanded`.
  5. Tests: Path valid (start first, goal last); path_len <= BFS path_len.
- Dependencies: None (after skeleton).
- AC: Handles start==goal trivially; no crashes if frontiers exhaust.
- EO: Typically fewer nodes expanded than BFS on larger grids.

#### A4 – Extend Heuristics (`algorithms/common.py`)
- Steps: Already added `euclidean`, `octile`, `get_heuristic`; verify correctness.
  1. Add tests: small coordinate pairs verifying numeric outputs.
  2. Ensure octile uses factor ≈ 0.414 ( (sqrt(2)-1) ).
- Dependencies: None.
- AC: Tests pass; values precise within 1e-6 tolerance.
- EO: Heuristics selectable for A* when integrated.

#### A5 – Hill Climbing Tactical Planner
- Steps:
  1. Replace stub in `locals_planner.py` implementing `hill_climb(state, action_space, horizon=5)`.
  2. Represent candidate plan as list of actions.
  3. Initialize random (or baseline) plan; evaluate score.
  4. Mutation: swap one action or replace one with random; iterate fixed N (e.g. 100) improvements.
  5. Scoring: distance band (prefer 6–10 cells), flank bonus (difference in x/y alignment), penalty low stamina (<30), small random jitter.
  6. Return best `Plan` (actions, score).
  7. Add docstring detailing scoring function.
  8. Add lightweight test: output horizon length; score is float.
- Dependencies: Basim exposes state dict (positions, stamina) when in melee range.
- AC: Function returns a reproducible (if seeded) or reasonable plan; no crashes.
- EO: When entities close, HUD can show chosen sequence (Basim integration).

#### A6 (Stretch) – Local Beam Search Stub
- Steps: New function `beam_search(state, action_space, beam_width=3, horizon=5)` leaving TODO comments.
- EO: Placeholder for report; not required for MVP.

### 3.2 Asaad Bin Amir – Visuals & Sound

#### V1 – HUD Legend & Metrics Polish
- Steps:
  1. Enhance `draw_labels` with multi-line box: controls + current map name + algorithm + planner (if active).
  2. Add dynamic color highlight for selected algorithm.
  3. Ensure font fallback (if Consolas not found). Use `pygame.font.get_default_font()` fallback.
- Dependencies: Existing renderer.
- AC: Box visible, text readable (contrast > WCAG ~4.5:1 simulated by bright text on dark background).
- EO: Clear, clutter-free HUD.

#### V2 – Sound Manager Implementation
- Steps:
  1. Create `core/sound_manager.py` with class `SoundManager`.
  2. Load `assets/sfx/{move.wav, attack.wav, block.wav}` gracefully (try/except; store `None` if missing).
  3. Methods `play_move`, `play_attack`, `play_block` skip if sound is `None`.
  4. Initialize in `main.py`; pass to `Game` or keep module-level singleton.
- Dependencies: Asset files or dummy placeholders.
- AC: No exception if files absent; stepping triggers move sound.
- EO: Audible feedback enhances interaction.

#### V3 – Algorithm Icon Support (Optional)
- Steps:
  1. Add folder `assets/ui/` with `bfs.png`, `dfs.png`, etc. (16–24 px).
  2. In `draw_labels`, attempt load current icon; fallback to text.
- Dependencies: Basic icon assets.
- AC: No crash if missing icon.
- EO: Visual distinction between algorithms.

#### V4 – Visual Path Differentiation
- Steps:
  1. Use different color or thickness for UCS/A* vs BFS/DFS.
  2. Optional toggle in HUD to show path cost vs length.
- Dependencies: Stats integration.
- AC: Colors consistent and not confusing.
- EO: Users can visually compare strategies.

#### V5 (Stretch) – Minor Animation / Tween
- Steps: Interpolate sprite position between cells if time.
- EO: Smoother movement (non-essential).

### 3.3 Basim Khurram Gul – Gameplay & Integration

#### G1 – Map Loader Module
- Steps:
  1. Create `core/map_loader.py` with `make_random(seed, obstacle_ratio, eight_connected)` returning `Grid`.
  2. Implement `from_text(file_path, eight_connected)` parsing `#` walls and `.` floors.
  3. Add sample maps under `assets/maps/{map1.txt, map2.txt}`.
  4. Modify `main.py` to keep list of maps (random + text). Press `M` cycles, recomputes path.
  5. Show current map name in HUD.
- Dependencies: Existing `Grid`.
- AC: Switching updates grid & path without crash; agents repositioned validly.
- EO: Demonstrable map variety.

#### G2 – CSV Logging
- Steps:
  1. Create `core/logging.py` with `log_run(file_path, algo, stats, map_name, notes="")`.
  2. Append row: `timestamp,algo,nodes,ms,path_len,path_cost,map_name,notes`.
  3. Invoke after each successful `compute_path` call (in `game.compute_path`).
  4. Ensure file created if absent; header optional (include if new file).
- Dependencies: Stats filled by algorithms.
- AC: Rows accumulate; numeric fields correct; no duplicate headers.
- EO: Data ready for later charting.

#### G3 – Neighbor Mode & Heuristic Cycling
- Steps:
  1. Extend `UIState` with `neighbors_mode` & `heuristic`.
  2. Key `N` toggles between 4-way/8-way; reinitialize `Grid` or flag update.
  3. Key `H` cycles heuristics list; pass selected heuristic into A* (and optionally Greedy).
- Dependencies: Abdul’s heuristics tests.
- AC: A* uses appropriate heuristic; path & nodes_expanded changes reflect heuristic choice.
- EO: Comparative demonstration of heuristic effect.

#### G4 – Hill Climb Integration
- Steps:
  1. Detect melee range (`distance <= MELEE_RANGE`).
  2. Build `state` dict (player pos, enemy pos, stamina values).
  3. Call `hill_climb` and store returned `Plan`.
  4. Display plan actions briefly in HUD (e.g., overlay for 2 seconds).
- Dependencies: Abdul completes A5.
- AC: No spam calls every frame; plan updates only when entering range or cooldown elapsed.
- EO: Tactical layer visible; differentiates project.

#### G5 – CI/CD Pipeline
- Steps:
  1. Add `.github/workflows/python.yml` (Python 3.11, cache `pip`, run `pytest`).
  2. Add status badge to `README.md`.
  3. Ensure test suite passes in PR.
- Dependencies: Stable tests.
- AC: Workflow green on `main` & feature branches.
- EO: Professional presentation; early bug catch.

#### G6 – PR Template & CODEOWNERS
- Steps:
  1. Create `.github/PULL_REQUEST_TEMPLATE.md` with checklist (tests pass, GIF demo, README updated).
  2. Create `CODEOWNERS` mapping directories: `algorithms/ @abdulraufdev`, `core/graphics.py core/sound_manager.py assets/ @AsaadUsername`, `core/gameplay.py core/map_loader.py core/logging.py .github/ @Basim-Gul`.
  3. Commit to `main`; verify ownership enforcement.
- Dependencies: None.
- AC: Auto review requests triggered.
- EO: Structured review flow.

#### G7 (Stretch) – Metrics Visualization Prep
- Steps: Add `scripts/plot_metrics.py` to parse CSV & produce PNG charts (nodes vs ms; path length vs algo).
- EO: Visual evidence for write-up.

---
## 4. Cross-Feature Integration Points
| Integration | Trigger | Owner Primary | Owner Secondary | Notes |
|-------------|---------|---------------|-----------------|-------|
| Map Switch recompute | Press `M` | Basim | Abdul | Path recomputed with current algo & heuristic |
| Hill Climb call | Distance <= melee range | Basim | Abdul | Provide state; display plan |
| Sound trigger | Path step / plan action | Asaad | Basim | Non-blocking; try/except |
| Logging append | After `compute_path` success | Basim | Abdul | Stats must have path_len & nodes_expanded |

---
## 5. Acceptance Criteria Summary (Condensed)
| Feature | Acceptance Criteria |
|---------|---------------------|
| DLS | Respects `depth_limit`; returns empty when goal deeper than limit; test passes |
| IDS | Path matches BFS on simple grid; aggregated node expansions >= BFS |
| BDS | Produces valid path; nodes_expanded < BFS (on larger grid) |
| Heuristics | Numeric tests for sample coordinates pass |
| Hill Climb | Returns horizon-length plan; score differentiates better positions |
| Map Loader | Map cycles without crash; agents valid positions; HUD updates |
| Logging | CSV rows appended correctly; numeric fields accurate |
| Sound | Plays without blocking; no crash if file missing |
| Heuristic Cycling | A* output path changes when switching heuristics |
| Neighbor Toggle | 4-way vs 8-way differences visible in path shape |
| CI | Workflow green; failing tests block merge |
| PR Template | Checkbox list appears in PR form |

---
## 6. Copilot Prompt Templates (Use EXACT File Paths & Signatures)
Copy, adapt variable names; keep constraints explicit.

### Algorithm Example (Abdul – DLS)
```
You are assisting with Project ARES.
File: algorithms/dls.py
Create function: find_path(grid, start: tuple[int,int], goal: tuple[int,int], depth_limit: int = 50) -> tuple[list[tuple[int,int]], Stats]
Constraints:
- Use grid.neighbors
- Track nodes_expanded only when expanding
- Do not explore children deeper than depth_limit
- Reconstruct path using came_from
- Return ([], Stats) if goal not found
Add docstring and type hints.
Acceptance: Unit test will verify empty path when limit too low.
```

### Hill Climb Planner (Abdul)
```
File: algorithms/locals_planner.py
Implement hill_climb(state: dict, action_space: list[str], horizon: int=5) -> Plan
Constraints:
- Start with random action sequence (length=horizon)
- Iterate 100 mutations (swap or replace one action)
- Scoring: prefer distance 6-10 cells; flank bonus if x or y offset > 2; penalty if stamina <30; add small random noise
- Keep best plan
Return Plan(actions, score) with docstring and type hints.
```

### Sound Manager (Asaad)
```
File: core/sound_manager.py
Class: SoundManager
Methods: __init__(), play_move(), play_attack(), play_block()
Constraints:
- Load assets/sfx/{move.wav, attack.wav, block.wav} via pygame.mixer.Sound
- Wrap loads in try/except; set attribute to None if missing
- Each play_* checks if sound is not None before playing
No crashes if files absent.
```

### Map Loader (Basim)
```
File: core/map_loader.py
Functions: make_random(seed:int, obstacle_ratio:float, eight_connected:bool) -> Grid; from_text(file_path:str, eight_connected:bool)->Grid
Constraints:
- Random uses seed for reproducibility
- from_text parses lines; '#' blocked, '.' free; ignore other chars
- Ensure start and goal spawn positions are not blocked (adjust if needed)
Add docstrings & type hints.
```

### CSV Logger (Basim)
```
File: core/logging.py
Function: log_run(file_path:str, algo:str, stats:Stats, map_name:str, notes:str="") -> None
Constraints:
- If file does not exist write header
- Append single CSV line; timestamp via datetime.datetime.utcnow().isoformat()
- Ensure path_cost and path_len recorded
No return value.
```

---
## 7. Daily Micro-Goal Template
Each member posts daily (informal):
```
Yesterday: Implemented DLS base; wrote failing test.
Today: Fix path reconstruction; start IDS wrapper.
Blockers: Need map file sample for complexity tests.
```
This keeps momentum without meetings.

---
## 8. Risk Mitigation Mapping
| Risk | Owner Monitoring | Mitigation Action |
|------|------------------|-------------------|
| Copilot drift | Task author | Re-prompt with explicit signature & constraints |
| Merge conflicts | Basim | Encourage small PRs; rebase before push |
| Slow algorithm dev | Abdul | Implement minimal version first; optimize later |
| Asset load failures | Asaad | Graceful fallbacks; log warnings |
| Logging performance | Basim | Write once per compute; avoid per-frame writes |

---
## 9. Quality Gates Before Demo
1. All algorithms produce correct paths on a 10x10 open grid.
2. No crashes when switching algorithms rapidly (spam 1–5 keys).
3. Map switch does not leave agents inside walls.
4. Hill Climb executes only near melee range (distance check verified).
5. CSV contains ≥5 distinct runs with varying algorithms.
6. Sound calls do not raise exceptions if assets missing.
7. README updated with CI badge & instructions.
8. Tests: ≥6 passing (existing + newly added heuristics + DLS/IDS/BDS).

---
## 10. Stretch Feature Acceptance (If Time Allows)
| Feature | Description | Acceptance |
|---------|-------------|------------|
| Local Beam Search | Keep top K sequences each step | Returns Plan list; docstring placeholder |
| Simulated Annealing | Probabilistic acceptance of worse states | Temperature decays; at least one uphill acceptance logged |
| Terrain Costs | Different tile costs (mud, stone) | UCS/A* path_cost differences visible |
| Charts Script | `scripts/plot_metrics.py` producing PNGs | Generates 2+ charts from CSV |
| Profiles | Aggressive vs Defensive scoring weights | CLI arg or key toggles scoring profile |

---
## 11. Final Expected MVP Outcomes
By end of Phase 4:
- Playable window at stable ~60 FPS.
- User can toggle BFS, DFS, UCS, Greedy, A* seamlessly.
- Additional algorithms (DLS, IDS, BDS) operational & test-covered.
- HUD shows algorithm, nodes expanded, compute ms, path length.
- Map cycling functional; at least one random + two text maps.
- Hill Climb triggers within melee range and displays action sequence.
- Sounds play (if assets present) without blocking or crashing.
- CSV logs contain complete metrics dataset for algorithms on multiple maps.
- CI pipeline green; PR template & CODEOWNERS enforcing workflow.
- Demo GIF / video recorded showing algorithm switch + Hill Climb.

---
## 12. Definition of Done (Reaffirmed)
A feature is DONE when:
1. Code implemented with docstrings & type hints.
2. Tests for the feature pass locally.
3. No regressions in existing tests.
4. HUD / UI updates (if user-facing).
5. Logged metrics (if algorithmic).
6. Branch merged via reviewed PR with demo artifact (GIF/screenshot).
7. CI passes.

---
## 13. Ongoing Maintenance Notes
- Keep functions small (<40 lines ideally).
- Prefer pure functions in algorithms; side-effects only in integration code.
- Use descriptive commit messages: `feat(algorithms): add bidirectional bfs`.
- Run `pytest` before pushing every feature branch.

---
## 14. Update Procedure
If scope changes (e.g., add Simulated Annealing early):
1. Add new task (ID with prefix: A#, V#, G#).
2. Specify dependencies & acceptance criteria.
3. Share update in group chat + amend this file in a new PR.
4. Tag affected member for acknowledgment.

---
## 15. Document Ownership
Primary maintainer: Basim (@Basim-Gul). Edits by others require PR review from Basim. Major algorithm spec changes reviewed by Abdul.

---
## 16. Revision History
| Version | Date (UTC) | Author | Summary |
|---------|------------|--------|---------|
| 1.0 | 2025-11-11 | @copilot via Basim request | Initial comprehensive execution plan |
---
End of Document.
