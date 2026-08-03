# Testing Guide

This project is an Applesoft BASIC interpreter. Tests should validate interpreter behavior and program compatibility, not a single story game.

## Quick Start

Manual run (recommended while developing):

```bash
python run_basic_file.py lemon_drop --input-timeout 120 --exec-timeout 600
```

Interactive Applesoft prompt run:

```bash
python applesoft.py
```

Use this mode to compare immediate-mode behavior against AppleWin or real Applesoft, including:
- prompt spacing after `RUN`, `NEW`, numbered lines, and immediate statements
- `LIST` formatting and carriage returns
- BREAK handling during running programs
- interactive `SAVE` / `LOAD` flow
- post-command prompt placement for `PRINT "TEXT"` vs `PRINT "TEXT";`
- terse immediate-mode error output such as `?SYNTAX ERROR`

Direct interpreter run:

```bash
python applesoft.py basic_code/games/lemonade.bas --input-timeout 120 --exec-timeout 600
```

Batch run every `.bas` file in the repository:

```bash
python run_all_bas_tests.py
```

## Test Types

1. Smoke tests
- Confirm program launches and exits cleanly.
- Confirm no `SYNTAX ERROR` appears.

2. Input flow tests
- Verify `INPUT` and `GET` prompts accept keyboard input.
- Verify timeout behavior using `--input-timeout`.

3. Rendering checks
- Use `--autosnap-on-end` or `--autosnap-every N` to capture output.
- Compare screenshots between changes when diagnosing regressions.

4. Timing checks
- Validate loop cadence with `--for-delay` and `--cpu-hz` as needed.
- Validate tone pacing with your audio examples in `basic_code/audio/`.

## Useful Commands

Syntax-like smoke run with automatic close:

```bash
python applesoft.py basic_code/basics/test_basic.bas --input-timeout 5 --exec-timeout 30 --auto-close
```

Run Lemon Drop with screenshots:

```bash
python applesoft.py basic_code/games/lemon_drop.bas --input-timeout 120 --exec-timeout 600 --autosnap-on-end
```

## Troubleshooting

If you see `SYNTAX ERROR IN <line>`:

1. Check the referenced line exists.
2. Check for duplicate line numbers.
3. Check for variable names longer than 2 characters (Applesoft truncation behavior).

If input appears stuck:

1. Increase `--input-timeout`.
2. Confirm the program reached an `INPUT`/`GET` line.
3. Try `run_basic_file.py` for manual keyboard testing.
4. For immediate-mode prompt behavior, start `python applesoft.py` with no filename and test directly in the pygame window.

## Notes

- `test_game_manual.py` remains as a compatibility wrapper and now forwards to `run_basic_file.py`.
- Keep tests program-agnostic where possible so they remain useful across all BASIC files.
- `LOAD` / `SAVE` testing is best done from no-file interactive mode because `SAVE` defaults to the repository `basic_code/` directory.
