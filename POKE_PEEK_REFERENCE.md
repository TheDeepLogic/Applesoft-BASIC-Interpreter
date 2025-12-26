# POKE/PEEK/CALL Implementation Documentation

Based on the Official Apple IIe Manual

## Overview
This document describes the comprehensive POKE/PEEK/CALL support based on the official Apple IIe Reference Manual. The implementation provides full compatibility with standard Apple II memory operations and monitor subroutines.

## Architecture

## Architecture

### Memory Array
- **Size**: 64KB (65536 bytes) - standard Apple II address space (0x0000 - 0xFFFF)
- **Storage**: `bytearray` for efficient byte-level access
- **Initialization**: Default values set for common Apple II memory locations

### Address Space Mapping
The interpreter recognizes Apple II memory-mapped I/O addresses, including both positive and negative addressing:
- Positive addresses: 0-65535 (standard)
- Negative addresses: Automatically converted to unsigned (e.g., -16384 becomes 49152)

## Implemented POKE Handlers

### Text Window Control (32-35) - From Official Manual
Settings control the boundaries of the text window:
- **$20 (32)**: Left margin of text window (0-39)
- **$21 (33)**: Width of text window (1-40, must not be 0!)
- **$22 (34)**: Top margin of text window (0-23)
- **$23 (35)**: Bottom margin of text window (0-23)

### Text Attributes (50)
- **50, 255**: NORMAL mode (disable inverse/flash)
- **50, 63**: INVERSE mode (inverse video)
- **50, 127**: FLASH mode (flashing text)
- **50, 128**: Hide listings/catalogs flag

### Cursor Position (36-37)
- **36**: Cursor X position (0-39)
- **37**: Cursor Y position (0-23)
- Values automatically clamped to valid ranges

### Graphics Mode Softswitches ($C0xx)
These are memory-mapped I/O addresses for graphics control:

| Address | Positive | Negative | Function |
|---------|----------|----------|----------|
| $C050 | 49232 | -16304 | TEXT mode (off=graphics) |
| $C051 | 49233 | -16303 | GR mode (off=HGR) |
| $C052 | 49234 | -16302 | Full screen graphics (no text overlay) |
| $C053 | 49235 | -16301 | Mixed mode (text overlay on bottom 4 lines) |
| $C054 | 49236 | -16300 | Select HGR page 1 |
| $C055 | 49237 | -16299 | Select HGR page 2 |
| $C056 | 49238 | -16298 | Lo-res graphics mode |
| $C057 | 49239 | -16297 | Hi-res graphics mode |

### Input/Output Addresses

#### Keyboard ($C000, $C010)
- **49152 / -16384**: Reads keyboard with high-order bit set if new character typed
- **49168 / -16368**: Clears keyboard strobe (read to clear high-order bit of -16384)

#### Joystick/Paddle ($C061-$C064)
- **49249 / -16287**: Joystick button 0
- **49250 / -16286**: Joystick button 1
- **49251 / -16285**: Joystick button 2
- **49252 / -16284**: Joystick button 3
- **49248 / -16288**: Cassette input
- **49200 / -16336**: Speaker (sound output)

### Memory Management Addresses
- **103-104**: LOMEM (low memory end) - default 0x0801 (2049)
- **115-116**: HIMEM (high memory end) - default 0x9600 (38400)
- **232-233**: Shape table address pointer

## Implemented PEEK Functions

### Standard Memory Reads
- Any address can be read with `PEEK(addr)`
- Returns byte value from memory array (0-255)
- Negative addresses supported (automatic conversion)

### Special Addresses
The following addresses return dynamic/special values:

| Address | Function |
|---------|----------|
| 36-37 | Cursor position (synced with interpreter state) |
| 49152 / -16384 | Keyboard input (returns 0) |
| 49168 / -16368 | Keyboard data (returns 0) |
| 49248-49252 / -16288 to -16284 | Joystick inputs (returns 0) |
| 49200 / -16336 | Speaker status (returns 0) |

## Two-Byte Address Reading
Apple II programs commonly read 16-bit values using:
```basic
X = PEEK(B) + PEEK(B+1) * 256
```

This pattern reads a low byte and high byte in little-endian format.

## Two-Byte Address Writing
To write 16-bit values:
```basic
POKE B+1, Q/256 : POKE B, Q - (PEEK(B+1) * 256)
```

Or equivalently:
```basic
POKE B+1, INT(Q/256) : POKE B, Q MOD 256
```

## Example Programs

### Basic POKE/PEEK
```basic
10 POKE 768, 42      : REM Store value
20 X = PEEK(768)     : REM Read value
30 PRINT X           : REM Prints 42
```

### Graphics Mode Control
```basic
10 HGR              : REM Enable hi-res graphics
20 HCOLOR = 3       : REM Set color to white
30 HPLOT 0,0 TO 100,100  : REM Draw line
40 POKE 49237, 0    : REM Switch to page 2
50 HPLOT 100,100 TO 200,200  : REM Draw on page 2
60 POKE 49236, 0    : REM Switch back to page 1
```

### Text Attributes
```basic
10 POKE 50, 255     : REM NORMAL
20 PRINT "NORMAL TEXT"
30 POKE 50, 63      : REM INVERSE
40 PRINT "INVERSE TEXT"
50 POKE 50, 127     : REM FLASH
60 PRINT "FLASHING TEXT"
70 POKE 50, 255     : REM Back to NORMAL
```

### Cursor Control
```basic
10 POKE 36, 10      : REM Move cursor to column 10
20 POKE 37, 5       : REM Move cursor to row 5
30 PRINT "Text at row 5, column 10"
```

## Testing

The implementation has been tested with:
1. **test_poke_simple.bas** - Basic POKE/PEEK functionality
2. **test_poke_comprehensive.bas** - Comprehensive multi-area testing
3. **test_page.bas** - Graphics page selection
4. **test_mixed_toggle.bas** - Mixed mode toggling
5. **test_ground.bas** - Graphics mode POKEs
6. **test_manual_features.bas** - Official manual features

All tests pass successfully.

## CALL Commands - Text and Graphics Operations

The official manual documents these CALL commands:

### Text Operations
- **CALL -938**: Clear text window and move cursor to top-left (equivalent to HOME)
- **CALL -358**: Clear from cursor position to bottom-right of window
- **CALL -858**: Clear from cursor position to end of current line
- **CALL -922**: Line feed (move cursor down one line, scroll if at bottom)
- **CALL -912**: Scroll text up one line within text window

### Graphics Operations
- **CALL -1998**: Clear low-resolution page 1 to black
- **CALL -1994**: Clear upper portion (40 rows) of low-resolution page 1
- **CALL -3086**: Clear current high-resolution page to black
- **CALL -3082**: Clear current high-resolution page to last HPLOT color
- **CALL 62454**: Fill current high-resolution page with last HPLOT color

### Error Handling
- **CALL -3288**: Clear control stack (used in error handlers before GOTO)
- **CALL 54915**: Empty entire control stack

## Error Handling Addresses (Official Manual)

- **216**: Error handler installed flag (> 127 if installed)
  - POKE 216, 0: Restore normal error handling
- **218-219**: Error line number (2-byte little-endian)
  - PEEK(219) * 256 + PEEK(218) yields line number
- **222**: Error code identifying type of error

## Memory Safety

The implementation includes safety features:
- **Byte wrapping**: Values >255 are masked to 0-255 using `val & 0xFF`
- **Address clamping**: Addresses >65535 are masked to valid range `addr & 0xFFFF`
- **Negative address support**: Automatically converted using `(addr + 65536) % 65536`

## Future Enhancements

Possible additions for increased compatibility:
1. Paddle ADC values (addresses $C064-$C067)
2. Game controller support via joystick input
3. Cassette I/O simulation
4. Disk drive controller addresses
5. More ProDOS/DOS 3.3 specific addresses
6. Proper keyboard buffer simulation
7. Sound generation from speaker POKEs

## Compatibility Notes

This implementation focuses on the most commonly used POKEs/PEEKs found in typical Applesoft BASIC programs:
- Graphics mode control (most commonly used)
- Text attributes and cursor positioning
- Memory management references
- Basic memory read/write operations

Programs using advanced DOS 3.3 features, machine language calls, or obscure memory addresses may require additional implementation.
