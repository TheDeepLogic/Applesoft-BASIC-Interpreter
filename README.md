# Applesoft BASIC Interpreter

A comprehensive Python implementation of the Applesoft BASIC interpreter with full graphics support using pygame.

This project is a Python-based Applesoft BASIC interpreter and renderer built to run and visualize Apple II BASIC programs on modern systems with faithful high‑resolution graphics. It was created to streamline AI‑assisted generation and debugging of Applesoft code without constantly round‑tripping through external emulators, while documenting and reproducing subtle hardware behaviors like NTSC color artifacting, mixed HGR/text overlays, and authentic `HPLOT`/`HCOLOR` semantics. With pragmatic CLI controls (timeouts, autosnap, optional artifact simulation and composite blur), it provides a fast, repeatable way to validate program output, compare rendering against emulators, and explore graphics logic. It’s useful for learning Applesoft, prototyping and testing graphics routines, and capturing reproducible screenshots for documentation and regression tests—without setting up a full vintage environment.

> **AI-Assisted Development Notice**
> 
> Hello, fellow human! My name is Aaron Smith. I've been in the IT field for nearly three decades and have extensive experience as both an engineer and architect. While I've had various projects in the past that have made their way into the public domain, I've always wanted to release more than I could. I write useful utilities all the time that aid me with my vintage computing and hobbyist electronic projects, but rarely publish them. I've had experience in both the public and private sectors and can unfortunately slip into treating each one of these as a fully polished cannonball ready for market. It leads to scope creep and never-ending updates to documentation.
> 
> With that in-mind, I've leveraged GitHub Copilot to create or enhance the code within this repository and, outside of this notice, all related documentation. While I'd love to tell you that I pore over it all and make revisions, that just isn't the case. To prevent my behavior from keeping these tools from seeing the light of day, I've decided to do as little of that as possible! My workflow involves simply stating the need to GitHub Copilot, providing reference material where helpful, running the resulting code, and, if there is an actionable output, validating that it's correct. If I find a change I'd like to make, I describe it to Copilot. I've been leveraging the Agent CLI and it takes care of the core debugging.
>
> With all that being said, please keep in-mind that what you read and execute was created by Claude Sonnet 4.5. There may be mistakes. If you find an error, please feel free to submit a pull request with a correction!
>
> Thanks: [Joshua Bell](https://www.calormen.com/jsbasic/) for writing [JSBASIC](https://github.com/inexorabletash/jsbasic/), which was almost enough for me to not consider this project. Unfortunately, I needed graphics capabilities locally and a way for the model to evaluate those so had to go this route. If you are looking for something that processes text based Applesoft programs from a command line, and don't want to fiddle with all this, that project is an excellent candidate. And, while I can't seem to find any information on the original author of these fonts, or any license information, I'd like to thank whoever created PrintChar21.ttf and PRNumber3.ttf. If anyone knows, please reach out to me and I'll include their information. These seem to have been available on the internet for quite a long while and are hosted by multiple sources. They were used in this and saved some implementation time.
## Features

- **Complete Applesoft BASIC implementation** - All major commands and functions
- **Graphics modes**:
  - `GR` - Low-resolution graphics (40x48)
  - `HGR`/`HGR2` - High-resolution graphics (280x192) with proper pixel erasing
  - `TEXT` - 40-column text mode
- **Full language support**:
  - Variables (numeric and string)
  - Arrays with `DIM`
  - Control flow: `FOR`/`NEXT`, `IF`/`THEN`, `GOTO`, `GOSUB`/`RETURN`
  - Data handling: `READ`, `DATA`, `RESTORE`
  - User-defined functions with `DEF FN`
  - Error handling with `ONERR` and `RESUME`
- **Input handling with timeout** - Prevents hanging on `INPUT` or `GET` statements
- **Math functions**: `SIN`, `COS`, `TAN`, `ATN`, `LOG`, `EXP`, `SQR`, `ABS`, `INT`, `SGN`, `RND`
- **String functions**: `LEFT$`, `RIGHT$`, `MID$`, `LEN`, `VAL`, `ASC`, `CHR$`, `STR$`
- **Graphics commands**: `PLOT`, `HPLOT`, `HLIN`, `VLIN`, `COLOR`, `HCOLOR`

## Requirements

- Python 3.8+
- pygame (optional, for graphics modes)

```bash
pip install pygame
```

## Usage

### Run a BASIC program:

```bash
python applesoft.py program.bas
```

### Interactive mode:

```bash
python applesoft.py
```

Then type BASIC commands directly:
```basic
] 10 PRINT "HELLO"
] 20 GOTO 10
] RUN
```

### Command-line options:

```bash
python applesoft.py [filename] [--input-timeout SECONDS] [--exec-timeout SECONDS] [--no-keep-open] \
                    [--autosnap-every N] [--autosnap-on-end] [--no-artifact] [--composite-blur] \
                    [--delay SECONDS]
```

- `--input-timeout`: Set input timeout in seconds (default: 30)
- `--exec-timeout`: Stop execution after N seconds (optional)
- `--no-keep-open`: Close the pygame window when program ends
- `--autosnap-every N`: Save a screenshot every N statements (helpful for tests)
- `--autosnap-on-end`: Save a screenshot when the program ends
- `--no-artifact`: Use artifact-free rendering (disables NTSC artifact simulation for HGR mode)
- `--composite-blur`: Apply a horizontal blur effect to approximate composite smoothing
- `--delay`: Statement execution delay in seconds to simulate Apple II speed (default: 0.001)

## Example Programs

### Simple Loop (test_basic.bas)

```basic
10 PRINT "TESTING BASIC INTERPRETER"
20 PRINT "========================="
30 PRINT
40 PRINT "TEST 1: SIMPLE LOOP"
50 FOR I = 1 TO 5
60 PRINT "ITERATION "; I
70 NEXT I
80 PRINT
90 PRINT "TEST 2: VARIABLES"
100 LET A = 10
110 LET B = 20
120 LET C = A + B
130 PRINT "A = "; A
140 PRINT "B = "; B
150 PRINT "C = A + B = "; C
```

### Low-Resolution Graphics (test_graphics.bas)

```basic
10 REM LOW-RES GRAPHICS TEST
20 GR
30 COLOR= 3
40 PLOT 20,20
50 HLIN 10,30 AT 15
60 VLIN 10,30 AT 20
70 FOR I = 0 TO 15
80 COLOR= I
90 PLOT I * 2, 10
100 NEXT I
```

### High-Resolution Graphics (test_hires.bas)

```basic
10 REM HI-RES GRAPHICS TEST
20 HGR
30 HCOLOR= 3
40 HPLOT 140,96
50 FOR I = 0 TO 279
60 HPLOT TO I,96
70 NEXT I
80 HCOLOR= 1
90 FOR I = 0 TO 191
100 HPLOT 140,0 TO 140,I
110 NEXT I
120 HCOLOR= 2
125 HPLOT 140,96
130 FOR A = 0 TO 6.28 STEP 0.1
140 X = 140 + 100 * COS(A)
150 Y = 96 + 80 * SIN(A)
160 HPLOT TO X,Y
170 NEXT A
```

### Math Functions (test_math.bas)

```basic
10 REM MATH FUNCTIONS TEST
20 PRINT "SQUARE ROOT OF 16: "; SQR(16)
30 PRINT "INT(3.7): "; INT(3.7)
40 PRINT "ABS(-5): "; ABS(-5)
50 PRINT "SIN(0): "; SIN(0)
60 PRINT "COS(0): "; COS(0)
70 PRINT
80 PRINT "STRING FUNCTIONS:"
90 A$ = "HELLO WORLD"
100 PRINT "STRING: "; A$
110 PRINT "LEN: "; LEN(A$)
120 PRINT "LEFT$(5): "; LEFT$(A$,5)
130 PRINT "RIGHT$(5): "; RIGHT$(A$,5)
140 PRINT "MID$(7,5): "; MID$(A$,7,5)
```

## Supported Commands

### Control Flow
- `GOTO` - Jump to line number
- `GOSUB` / `RETURN` - Subroutine calls
- `IF` ... `THEN` - Conditional execution
- `FOR` ... `TO` ... `STEP` ... `NEXT` - Loops
- `ON` ... `GOTO` / `GOSUB` - Computed branching
- `END` / `STOP` - Stop program execution

### Variables & Data
- `LET` - Variable assignment (LET is optional)
- `DIM` - Dimension arrays
- `READ` / `DATA` / `RESTORE` - Data statements
- `INPUT` - Get user input
- `GET` - Get single character

### Output
- `PRINT` / `?` - Print to screen
- `TAB()` / `SPC()` - Formatting functions

### Graphics
- `TEXT` - Switch to text mode
- `GR` - Low-res graphics mode
- `HGR` / `HGR2` - High-res graphics mode
- `COLOR=` - Set low-res color (0-15)
- `HCOLOR=` - Set high-res color (0-7)
- `PLOT` - Plot point in low-res
- `HPLOT` - Plot point/line in high-res
- `HLIN` / `VLIN` - Draw lines in low-res
- `HTAB` / `VTAB` - Position cursor
- `HOME` - Clear screen
- `INVERSE` / `NORMAL` / `FLASH` - Text modes

HGR mixed-mode display:

- `HGR` (page 1) shows text overlay on the bottom 4 rows (rows 21–24). The pygame interpreter composites only those rows over graphics, matching emulator behavior.
- `HGR2` (page 2) defaults to full-screen graphics with no text overlay.

Softswitch compatibility via `POKE`:

- `POKE 49234,0` or `POKE -16302,0`: Disable mixed overlay (full-page graphics)
- `POKE 49235,0` or `POKE -16301,0`: Enable mixed overlay (bottom text)
- `POKE -16299,0`: Switch to hi-res page 2
- `POKE -16300,0`: Switch to hi-res page 1

Negative addresses are handled with 16-bit wrap, so both positive and negative forms work.

### Compatibility Notes (HCOLOR and HPLOT)

- `HPLOT TO x,y` uses the color of the last explicitly plotted point (`HPLOT x,y`). This matches Applesoft: changing `HCOLOR` alone does not affect a subsequent `HPLOT TO` until a point is plotted.
- `HPLOT x,y TO x2,y2` first plots at `x,y` using current `HCOLOR`, then draws the line using that same color.
- Practical tip: after changing `HCOLOR`, issue a single `HPLOT` to set the active color before `HPLOT TO` sequences.

### Functions
- `DEF FN` - Define user functions
- `POKE` - Softswitch support for HGR mixed/page toggles as listed above
- `PEEK` - Read from memory (returns 0)
- `CALL` - Selected helpers:
  - `CALL 62454`: Fill current HGR page with the last `HCOLOR`
  - `CALL 65000`: Capture a screenshot to `screenshots/` and report overlay presence

### Program Management
- `NEW` - Clear program
- `RUN` - Run program
- `LIST` - List program
- `CLEAR` - Clear variables

### Error Handling
- `ONERR GOTO` - Set error handler
- `RESUME` - Resume after error

## Input Timeout

To prevent programs from hanging on `INPUT` or `GET` statements, the interpreter includes a configurable timeout:

```bash
# Set 60-second input timeout
python applesoft.py myprogram.bas --input-timeout 60
```

When a timeout occurs, the program will display an error message and halt execution.

## Testing Your Code

Test programs are included in the `basic_code/` folder for reference and experimentation. The interpreter makes it easy to test BASIC programs:

1. **Create a simple test program**:
   ```basic
   10 PRINT "Testing"
   20 GOTO 10
   ```

2. **Run it**:
   ```bash
   python applesoft.py basic_code/test.bas
   ```

3. **Use Ctrl+C to break** if the program runs indefinitely

4. **Check graphics** - If using `GR` or `HGR`, a pygame window will open showing the graphics output
5. **Capture screenshots** - Use `CALL 65000` anywhere in your program, or enable `--autosnap-*` flags.

## Limitations

- `CALL` and `POKE`/`PEEK` are not fully implemented (hardware-specific)
- `SHLOAD`, `DRAW`, `XDRAW` shape tables are not implemented
- `TRACE`/`NOTRACE` debugging commands are no-ops
- `LOAD`/`SAVE` file operations are not implemented
- Cassette tape operations (`IN#`, `PR#`) are not implemented
- `WAIT` command only adds a small delay

## Architecture

The interpreter consists of:

1. **Parser** - Tokenizes and parses BASIC statements
2. **Executor** - Executes parsed statements
3. **Expression Evaluator** - Handles arithmetic and logic
4. **Graphics Engine** - pygame-based rendering for GR/HGR modes
5. **Runtime** - Variable storage, control flow stacks, error handling

## Contributing

Feel free to extend the interpreter with additional Applesoft features or improvements!

## License

This implementation is provided for educational and compatibility purposes.

## Credits

Based on the original Applesoft BASIC written by Marc McDonald and Randy Wigginton for Apple Computer, 1976-1978.
