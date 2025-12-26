# Apple IIe Official Manual - POKE/PEEK/CALL Implementation

## Implementation Summary

The Applesoft BASIC interpreter has been enhanced with comprehensive support for PEEK, POKE, and CALL commands based on the **Official Apple IIe Reference Manual**. This provides authentic compatibility with real Apple II programs.

## Key Features from Official Manual

### PEEK Function
Reads memory locations and special I/O addresses:
- **Cursor position**: PEEK(36) - X position, PEEK(37) - Y position
- **Keyboard input**: PEEK(-16384) with high-order bit indicating new character
- **Joystick buttons**: PEEK(-16287 to -16285) for buttons 0-2
- **Error handling**: PEEK(216), PEEK(218-219), PEEK(222)
- **Generic memory read**: PEEK(addr) reads any 8-bit memory location

### POKE Statement
Writes to memory and triggers softswitches:
- **Text window**: POKE 32-35 for margins and window size
- **Text attributes**: POKE 50 for NORMAL (255), INVERSE (63), FLASH (127)
- **Cursor position**: POKE 36-37 for X, Y positioning
- **Graphics modes**: POKE -16304 to -16297 for all graphics mode combinations
- **HGR pages**: POKE -16300 (page 1), POKE -16299 (page 2)
- **Annunciators**: POKE -16295 to -16290 for hand control outputs
- **Generic memory write**: POKE addr, value for any address

### CALL Command - Monitor Subroutines
Invokes built-in Apple II monitor routines:

**Text Operations:**
- CALL -938 (HOME - clear and top-left cursor)
- CALL -358 (clear cursor to end)
- CALL -858 (clear to end of line)
- CALL -922 (line feed)
- CALL -912 (scroll up one line)

**Graphics Operations:**
- CALL -1998 (clear lo-res page 1)
- CALL -1994 (clear upper lo-res page 1)
- CALL -3086 (clear current hi-res page to black)
- CALL -3082 (fill current hi-res page with last HPLOT color)
- CALL 62454 (fill current hi-res page)

**System Operations:**
- CALL -3288 (clear control stack)
- CALL 54915 (empty control stack)

## Example Programs

### Keyboard Input
```basic
10 POKE -16368, 0    : REM Clear strobe
20 X = PEEK(-16384)  : REM Read keyboard
30 IF X > 127 THEN PRINT "KEY PRESSED"
40 GOTO 20
```

### Graphics Mode Control (Per Manual)
```basic
10 HGR
20 HCOLOR=3
30 HPLOT 0,0 TO 279,191
40 POKE -16299,0    : REM Switch to page 2
50 HCOLOR=2
60 HPLOT 100,100 TO 200,200
70 POKE -16300,0    : REM Switch back to page 1
```

### Text Window Setup
```basic
10 POKE 32, 10      : REM Left margin at column 10
20 POKE 33, 20      : REM Width of 20 characters
30 POKE 34, 5       : REM Top margin at line 5
40 POKE 35, 15      : REM Bottom margin at line 15
50 PRINT "Text in custom window"
```

### Error Handling
```basic
10 ONERR GOTO 100
20 X = 1 / 0        : REM Trigger divide by zero
30 END
100 ERR = PEEK(222) : REM Get error code
110 LINE = PEEK(219)*256 + PEEK(218) : REM Get error line
120 PRINT "Error"; ERR; "at line"; LINE
130 CALL -3288      : REM Clear control stack
140 GOTO 30
```

### Graphics Clearing
```basic
10 HGR
20 HCOLOR=3
30 FOR X = 0 TO 279 STEP 10
40 HPLOT X,0 TO X,191
50 NEXT
60 CALL -3086       : REM Clear page to black
70 HCOLOR=2
80 CALL -3082       : REM Fill with last color (2)
90 END
```

## Memory Map Summary

| Address Range | Purpose | Notes |
|---|---|---|
| 32-35 | Text window control | Margins and window size |
| 36-37 | Cursor position | X and Y coordinates |
| 50 | Text video mode | NORMAL/INVERSE/FLASH |
| 103-104 | LOMEM | Low memory end |
| 115-116 | HIMEM | High memory end |
| 216 | Error handler flag | POKE to restore normal |
| 218-219 | Error line number | 2-byte little-endian |
| 222 | Error code | Error type identifier |
| $C000/-16384 | Keyboard | High-order bit=new char |
| $C010/-16368 | Keyboard strobe | Clear high-order bit |
| $C030/-16336 | Speaker | Click (PEEK/PEEK preferred) |
| $C050/-16304 | TEXT/GRAPHICS | Toggle text mode |
| $C051/-16303 | TEXT/GRAPHICS | Toggle full screen |
| $C052/-16302 | GRAPHICS/MIXED | Full screen graphics |
| $C053/-16301 | MIXED/FULL-SCREEN | Mixed text overlay |
| $C054/-16300 | PAGE 1/PAGE 2 | Select page 1 |
| $C055/-16299 | PAGE 2/PAGE 1 | Select page 2 |
| $C056/-16298 | LO-RES/HI-RES | Low resolution |
| $C057/-16297 | HI-RES/LO-RES | High resolution |
| $C061-63/-16287 to -16285 | Joystick buttons | Buttons 0-2 |

## Official Manual Warnings

Per the Apple IIe manual, observe these critical warnings:

1. **Text Window Width** (POKE 33)
   - Do NOT set to 0 - will crash system
   - Ensure right edge doesn't exceed display boundary

2. **Cursor Position** (POKE 36-37)
   - Don't move past right edge of screen
   - Don't move past bottom (line 23)
   - Only unlimited movement within proper ranges

3. **Text Window Setup**
   - Don't set top edge lower than bottom edge
   - Don't set bottom edge higher than top edge
   - Adjust width before changing left margin

## Special Softswitch Behaviors

Per the official manual, these softswitches have unique properties:

- Any PEEK or POKE to one address in a pair activates the switch
- Example: POKE -16304, 0 and X = PEEK(-16304) both switch to graphics
- Exception: Addresses requiring specific stored values (margins, cursor position)

## Testing

All features have been tested with:
- Comprehensive POKE/PEEK test suite
- Official manual feature test program
- Graphics mode switching tests
- Text attribute tests
- Error handling tests

## Compatibility

This implementation provides compatibility with standard Applesoft BASIC programs that use PEEK, POKE, and CALL statements as documented in the official Apple IIe manual. Most mainstream Apple II programs will run without modification.

Programs using DOS 3.3-specific addresses or advanced machine language routines may require additional implementation.
