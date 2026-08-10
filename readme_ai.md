# AI Quickstart: Applesoft BASIC Interpreter

Complete reference for automated agents integrating this Applesoft BASIC interpreter. Covers execution, language basics, graphics, and safe development patterns.

---

## Overview
- **Interpreter**: Pure Python implementation of Applesoft BASIC with HGR/GR graphics via pygame.
- **Entry point**: `python applesoft.py <program> [flags]`
- **Designed for**: AI model testing, code generation validation, and BASIC program development.

---

## Running Programs

### Basic Invocation
```bash
python applesoft.py <path.bas>  # Run a BASIC program
```
If the filename omits `.bas`, the interpreter auto-appends it and searches:
1. Current working directory
2. `./basic_code/` subdirectory (organized by topic)
3. Script's `basic_code/` directory

### Essential Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--input-timeout SECS` | 30 | Max wait for INPUT/GET (fail gracefully on timeout) |
| `--exec-timeout SECS` | None | Max total program runtime (useful for infinite loops) |
| `--auto-close` | False | Exit immediately when program ends (no window lingering) |
| `--close-delay SECS` | 3.0 | Seconds to keep graphics window open after program ends; use negative for indefinite wait |
| `--no-keep-open` | False | Close window immediately (overrides delay) |
| `--scale N` | 2 | Display scale factor (1=280x192, 2=560x384 for HGR) |

### Recommended Automation Flags
For headless/CI testing without user interaction:
```bash
python applesoft.py program.bas --input-timeout 5 --exec-timeout 45 --auto-close --close-delay 0
```

### Batch Test Suite
Helper script: `run_all_bas_tests.py`
- Iterates all `.bas` files in repo with uniform timeouts
- Generates `test_run_results.json` (gitignored) with rc, timing, and output per program
- Invocation: `python run_all_bas_tests.py`

---

## Legacy README Notes

These are the kinds of reminders that belong in the AI-focused guide instead of the public README.

### Snake Pattern: A Real AI Game Experiment
`basic_code/examples/snake.bas` is the canonical game-development example. The earlier `TEMPLATE_GAME` experiment was a useful but unsuccessful first pass: it drew effects, but did not become a playable game and was removed. Do not use it as a baseline.

Snake works because the task was anchored in a known ruleset, then tested as a program rather than judged from source alone. Its development exposed several failure modes an agent must actively test for:

- Duplicate line numbers silently replace earlier statements.
- Applesoft recognizes only two significant variable-name characters. Avoid token-adjacent names such as `LE TO`, which real Applesoft can render as `LET O`.
- Read a collision pixel before drawing over it.
- After compacting an array, never erase through the old index; save the removed element's coordinates first.
- `SOUND` is an interpreter extension, not Applesoft. Hardware-targeted programs must load the native `$0300` routine, then use `POKE 0,delay: POKE 1,toggles: CALL 768`.
- Clear GR text rows with `CALL -868` before redrawing a HUD line on real hardware.

Use a two-part test loop:

```bash
# Render and inspect state changes.
python applesoft.py basic_code/examples/snake.bas --auto-close --autosnap-every 180 --blit-per-line --exec-timeout 20

# Supply deterministic Apple II key codes: Enter, Right, Down, then Q.
APPLESOFT_TEST_KEYS=13,21,10,81 python applesoft.py basic_code/examples/snake.bas --auto-close --exec-timeout 20
```

On Windows PowerShell, set the environment value as `$env:APPLESOFT_TEST_KEYS='13,21,10,81'` before running Python. This test-only queue drives the same `PEEK(-16384)` keyboard latch as real input; it exists because Windows key injection did not reliably reach the pygame window.

### Common Applesoft Failure Modes
1. Variable names longer than two characters are silently truncated in Applesoft.
2. Every line number must be unique; duplicates trigger syntax errors.
3. Manual reading is not enough; always verify through the interpreter.
4. Use string input variables when you need automated input tests.
5. Check for suspiciously long variable names with a search like `grep -E '[A-Z]{3,}' yourfile.bas`.

### Recommended Test Assets
- `tests/README_TESTING.md` for interpreter and program testing workflow.
- `run_basic_file.py` for single-program manual runs.
- `run_all_bas_tests.py` for batch validation across the repository.
- `basic_code/examples/snake.bas` as a working game and compatibility reference.

### Practical AI Loop
1. Generate or edit a BASIC program.
2. Run it in the interpreter.
3. Inspect output, screenshots, and errors.
4. Fix the BASIC or interpreter issue.
5. Repeat until the behavior matches the intended Apple II result.

---

## Applesoft BASIC Language Primer

### Syntax & Structure
- **Line numbers required**: Each statement begins with a positive integer (line number).
- **Multiple statements per line**: Separate with `:` (colon).
- **Comments**: `REM <text>` ignores everything after REM on that line.
- **Case-insensitive**: Commands, variables, and functions accept any case (e.g., `PRINT`, `print`, `Print`).

Example:
```basic
100 PRINT "HELLO":REM First statement
110 X = 5:PRINT X:REM Second statement on line 110
```

### Variables
- **Naming**: Letters + digits; `$` suffix denotes string (e.g., `NAME$`, `X`, `VAL2`).
- **Types**: Numeric (float) or string; implicit coercion in expressions.
- **Scope**: Global only; no local variables.
- **Arrays**: `DIM A(10), B$(5)` allocates space; 1-indexed by default.

### Operators & Expressions
- **Arithmetic**: `+`, `-`, `*`, `/`, `MOD` (modulo), `\` (integer division, Python-style).
- **Comparison**: `=`, `<>`, `<`, `>`, `<=`, `>=`.
- **Logical**: `AND`, `OR`, `NOT`.
- **String**: `+` concatenates; `LEFT$`, `RIGHT$`, `MID$` extract substrings.
- **Operator precedence**: Standard (unary, `*`/`/`/`MOD`/`\`, `+`/`-`, comparisons, logical).

### Control Flow

#### IF/THEN/ELSE
```basic
100 IF X > 5 THEN PRINT "BIG" ELSE PRINT "SMALL"
```
- Single-line only in this dialect; no multi-line IF blocks.

#### FOR/NEXT Loops
```basic
100 FOR I = 1 TO 10 STEP 2
110   PRINT I
120 NEXT I
```
- Default `STEP` is 1; can step backward (negative STEP).
- `NEXT` variable name is optional but recommended for clarity.

#### GOTO / GOSUB
```basic
100 GOSUB 500        :REM Call subroutine at line 500
110 END
500 PRINT "SUBROUTINE":REM Subroutine code
510 RETURN            :REM Return to caller
```
- `GOSUB`/`RETURN` pushes/pops return address; nesting allowed.
- `GOTO` jumps unconditionally.

### Built-in Functions

| Category | Functions |
|----------|-----------|
| **Math** | `ABS`, `INT`, `SGN`, `SQR`, `EXP`, `LOG`, `SIN`, `COS`, `TAN`, `ATN`, `RND` |
| **String** | `LEN`, `LEFT$`, `RIGHT$`, `MID$`, `CHR$`, `STR$`, `VAL`, `ASC` |
| **I/O** | `PEEK`, `POKE` (memory access), `SCRN` (read pixel) |
| **Random** | `RND(X)` returns float [0,1); `RND(-1)` reseeds |
| **System** | `USR(N)` returns 0 (stubbed; ML calls unsupported) |

Examples:
```basic
100 X = INT(RND(1) * 100)     :REM Random 0-99
110 Y$ = "HELLO"
120 PRINT LEN(Y$)              :REM Output: 5
130 PRINT MID$(Y$, 2, 3)       :REM Output: ELL
```

### Input & Output

#### PRINT
```basic
100 PRINT "X="; X; " Y="; Y
110 PRINT                       :REM Blank line
```
- Semicolon suppresses newline; comma tabs.

#### INPUT / GET
```basic
100 INPUT "ENTER NAME: "; NAME$
110 GET K$                      :REM Single char, no newline required
```
- `INPUT` waits for a full line + Enter.
- `GET` waits for any single key (or timeout).
- Both can timeout; set `--input-timeout` appropriately.

---

## Graphics Modes

### Mode: TEXT (Default)
- 40 columns × 24 rows of text.
- Use `HOME` to clear and reset cursor.

Example:
```basic
100 TEXT
110 HOME
120 PRINT "TEXT MODE"
```

### Mode: GR (Low-Res Graphics)
- 40 × 48 pixels; 16 colors; 4 rows of text overlay (mixed mode).
- Pixel values: 0–15 (color index).

Key Commands:
- `GR` — Enter GR mode.
- `COLOR=N` — Set color for subsequent PLOT/HLIN/VLIN.
- `PLOT X, Y` — Set pixel (X, Y) to current color.
- `HLIN X1, X2 AT Y` — Horizontal line.
- `VLIN Y1, Y2 AT X` — Vertical line.
- `SCRN(X, Y)` — Read pixel color at (X, Y).

Example:
```basic
100 GR
110 COLOR = 5
120 FOR I = 0 TO 39
130   PLOT I, 20
140 NEXT I
150 TEXT
```

### Mode: HGR / HGR2 (High-Res Graphics)
- 280 × 192 pixels; 6 colors (NTSC artifact mode); dual page support.
- Efficient for game demos and complex graphics.

Key Commands:
- `HGR` — Page 1 (default).
- `HGR2` — Page 2 (optional).
- `HCOLOR=N` — Set color (0–7; actual color depends on artifact mode).
- `HPLOT X, Y` — Plot pixel.
- `HPLOT X1, Y1 TO X2, Y2` — Line draw.

Example:
```basic
100 HGR
110 HCOLOR = 3
120 HPLOT 0, 0 TO 279, 191
130 HTAB 5: VTAB 5: PRINT "HGR DEMO"
140 GET K$
150 HGR: TEXT
```

---


## Sound Emulation and Music

### Overview
This interpreter has three intentionally separate sound paths:
- **Native `$0300` baseline**: `init_sound.bas` loads a deterministic 16-byte speaker routine. `POKE 0` controls delay count; `POKE 1` controls speaker toggles. The interpreter derives its square-wave pitch and duration from exact routine cycle counts at `--cpu-hz`.
- **SOUND freq, duration**: Direct desktop playback extension. It is not valid Applesoft and is exercised only by `*_interpreter_extension.bas` fixtures.
- **Legacy CALL 768**: `*_legacy_call768.bas` preserves the old register-dependent routine. The interpreter uses a best-effort approximation for it, so it is not a native timing reference.

#### Implementation Details
- Sound is generated using Python and pygame (cross-platform). On Windows, winsound is used for short tones if pygame is unavailable.
- Native fixtures are self-contained and load the routine before using it. Use `audio_scale.bas` to check pitch order and `play_charge.bas` to check pitch sweep timing.
- Audio waveform/timbre can differ between the physical Apple II speaker and the host mixer. Treat cycle counts, transition timing, and speaker-toggle count as the parity assertions.

#### Example Usage
```basic
REM Native routine must already be loaded at $0300.
POKE 0,171: POKE 1,132: CALL 768
```

#### Notes
- Native routines are the hardware/AppleWin baseline. `SOUND` and legacy `CALL 768` fixtures remain useful only for their explicitly labeled compatibility paths.


### SOUND Command (Interpreter Extension)
Desktop-only syntax:
```basic
100 SOUND 440, 500      :REM Play 440 Hz for 500 ms
110 SOUND 523, 250      :REM Play 523 Hz (C note) for 250 ms
```

### Native Apple II Speaker Routine (CALL 768)
The native test routine at address 768 is self-loaded by the native audio fixtures:
```basic
100 POKE 0, 171         :REM Delay count (1-255, higher = lower pitch)
110 POKE 1, 132         :REM Speaker toggle count (1-255)
120 CALL 768            :REM Play the tone
```
- **Memory location 0**: Delay count (1-255). Higher values lower the pitch.
- **Memory location 1**: Speaker-toggle count (1-255). Higher values lengthen the note.
- **CALL 768**: Executes the loaded routine. Native programs must load it before calling.

Example tune:
```basic
10 POKE 0,216: POKE 1,131: CALL 768  :REM C4
20 POKE 0,171: POKE 1,165: CALL 768  :REM E4
30 POKE 0,144: POKE 1,196: CALL 768  :REM G4
```

Native fixtures should be the basis for parity testing. The interpreter-only extension is intentionally separate.

---

## Data & Structures

### Arrays
```basic
100 DIM A(100)                 :REM Numeric array, 1-indexed
110 DIM NAME$(50)              :REM String array
120 A(1) = 42
130 PRINT A(1)
```
- Bounds: subscript range [1, size].
- Multi-dimensional: `DIM M(10, 10)` allocates 10×10 grid.

### DATA Statements & READ
```basic
100 DATA 10, 20, 30
110 DATA 40, 50
200 READ X, Y, Z
210 PRINT X, Y, Z              :REM 10 20 30
220 READ A, B
230 PRINT A, B                 :REM 40 50
```
- `DATA` lines accumulate into a global pool.
- `READ` consumes sequentially; `RESTORE` resets pointer to start.

---

## Memory & System

### PEEK/POKE
```basic
100 V = PEEK(16384)            :REM Read from Apple II address space
110 POKE 16384, 0              :REM Write value
```
- 64 KB address space; many locations map to special hardware.

### Common Addresses (Soft-switches)
- `16384` (`$C000`): Keyboard input (7-bit ASCII + 128 if key available).
- Interpreter provides sensible defaults for video memory; direct manipulation not required.

### WAIT
```basic
100 WAIT  -16384, 128          :REM Wait until a key is pressed
110 WAIT  16384, 128, 0        :REM Wait until no key is pending
120 WAIT  $C000, 128, 128      :REM Hex address form; same as -16384
```
- Semantics: `WAIT addr, mask[, value]` blocks until `(PEEK(addr) AND mask)` equals `value`; if `value` is omitted, it blocks until the expression is non-zero.
- Keyboard example: `PEEK(-16384)` has bit 7 set when a key is available; `WAIT -16384,128` waits for a key.
- Behavior respects global `--exec-timeout`: if set and reached, `WAIT` stops waiting and execution continues.

---

## File Organization

### Directory Structure
```
basic_code/
  ├── arrays/           # Tests for array operations
  ├── audio/            # SOUND/SPEAKER commands
  ├── basics/           # Core language features
  ├── control_flow/     # FOR, GOTO, GOSUB, etc.
  ├── games/            # Game examples
  ├── graphics_hires/   # HGR demos
  ├── graphics_lores/   # GR demos
  ├── math_random/      # Math functions, RND
  ├── mixed/            # Combined features
  ├── output/           # PRINT, formatting
  ├── system_memory/    # PEEK, POKE, memory
  └── text_and_io/      # INPUT, GET, text handling
```

### Test Conventions
- `test_*.bas` files verify single features.
- Short-running (<5s) for quick iteration.
- Some long-runners (graphics, audio loops) hit `--exec-timeout` by design.

---

## Development Workflow for AI Agents

### Creating New Programs
1. **Choose location**: `basic_code/<category>/<name>.bas`
2. **Start simple**: Test individual commands before combining.
3. **Use clear logic**: Comments (`REM`) help other agents understand intent.
4. **Test interactively**: Run with `--input-timeout 30 --close-delay -1` for manual testing.
5. **Validate with automation**: Re-run with headless flags for CI.

### Common Pitfalls
- **Infinite loops**: Always set `--exec-timeout` when unsure.
- **Blocking I/O**: `INPUT`/`GET` waits indefinitely unless timeout fires.
- **Graphics initialization**: Call `GR` or `HGR` before graphics commands; call `TEXT` to exit.
- **Variable initialization**: No implicit zero; use `X = 0` explicitly.
- **String concatenation**: Use `+` operator; `PRINT` auto-stringifies numbers.

### Debugging
- **Syntax errors**: Interpreter reports line number; check command spelling and structure.
- **Type mismatches**: Ensure numeric ops use numbers, string ops use strings.
- **Array bounds**: Check DIM size; subscripts are 1-based and bounds-checked.
- **Output inspection**: Capture STDOUT with shell redirect or pipe parser.

---

## Integration with External Tools

### Piping Input
```bash
echo -e "10\nS\nn" | python applesoft.py blackjack.bas --input-timeout 5
```
- Each line becomes one INPUT or GET response.
- Multiple inputs: separate with `\n`.

### Capturing Output
```bash
python applesoft.py prog.bas > output.txt 2>&1
```
- Redirects STDOUT + STDERR for log analysis.

### Structured Metadata
- `test_run_results.json` contains per-file rc, duration, and full output.
- Parse JSON to extract success/failure metrics.

---

## Notes for AI Models
- This interpreter is Applesoft-compatible but not 100% feature-complete; advanced features (machine language, disk I/O) are not supported.
- `USR(N)` is recognized but stubbed to return `0`; programs that probe USR will not error but should not rely on machine-language routines.
- Graphic demos may run at reduced speed in headless mode; use `--delay` to adjust statement execution rate.
- HGR artifact color simulation (NTSC mode) is on by default; disable with `--no-artifact` if needed.
- Always check interpreter output for `SYNTAX ERROR` or `RUNTIME ERROR` messages; they include line number and detail.
- For reproducible testing, seed RND explicitly: `RND(-1)` in line 1 of your program.

---

## File Paths & Quick Reference
| Item | Path |
|------|------|
| Main interpreter | `applesoft.py` |
| Batch test helper | `run_all_bas_tests.py` |
| AI primer (this file) | `readme_ai.md` |
| Example programs | `basic_code/<category>/*.bas` |
| Main README | `README.md` |

---

Use this guide when developing, debugging, or integrating new BASIC programs. When in doubt, run a simpler test first to isolate issues.
