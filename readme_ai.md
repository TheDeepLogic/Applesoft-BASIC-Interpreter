# AI Quickstart: Applesoft BASIC Interpreter

This file is written for automated agents and tools. Keep outputs concise and fail fast. All commands assume repository root.

## Launching programs
- Interpreter entry: `python applesoft.py <program>`
- If caller omits `.bas`, the interpreter will append `.bas` automatically when searching.
- Graphics windows auto-close after 3 seconds by default. Override with:
  - `--no-keep-open` (immediate close), `--auto-close` (close at end), `--close-delay <seconds>` (negative waits indefinitely).
- Recommended test flags for automation: `--input-timeout 5 --exec-timeout 45 --auto-close --close-delay 0`.

## New sample: Blackjack
- Path: `basic_code/games/blackjack.bas`
- Features: title screen (HGR), betting, hit/stand/double, single split, dealer play, chip tracking starting at 100, celebration screen each time chips reach the next 100 milestone.
- Run example: `python applesoft.py basic_code/games/blackjack.bas --input-timeout 5 --exec-timeout 120 --auto-close --close-delay 0`
- Automate input: program uses blocking INPUT/GET. Provide scripted keypresses via tool wrapper if needed.

## Batch test sweep (optional)
- Helper script: `run_all_bas_tests.py`
- Runs every `.bas` with `--input-timeout 5`, `--exec-timeout 45`, subprocess timeout 55s, `--auto-close`.
- Generates `test_run_results.json` and logs; these are gitignored.
- Invoke: `python run_all_bas_tests.py`

## File search hints
- BASIC programs live under `basic_code/` (categorized by topic), plus `test_*.bas` for coverage.
- Interpreter entry and CLI live in `applesoft.py` (bottom of file for argument parsing and path resolution).

## Safety notes for agents
- Do not edit existing BASIC tests unless required; add new programs instead.
- Keep output windows short-lived in automation; prefer `--auto-close` and `--close-delay 0`.
- If a path fails, the interpreter prints all attempted locations; ensure you pass relative paths from repo root.
