#!/usr/bin/env python3
"""
Applesoft BASIC Interpreter in Python
Implements a full interpreter for Applesoft BASIC with graphics support using pygame.

Features:
- All Applesoft BASIC commands and functions
- Graphics modes: GR (40x48 low-res) and HGR/HGR2 (280x192 high-res)
- Text mode with 40-column display
- Input timeout handling
"""

import re
import sys
import math
import random
import time
import threading
import os
from datetime import datetime
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available. Graphics modes will be disabled.")


class ApplesoftError(Exception):
    """Base exception for Applesoft errors"""
    pass


class ApplesoftInterpreter:
    """Main Applesoft BASIC interpreter"""
    
    # Graphics constants
    GR_WIDTH = 40
    GR_HEIGHT = 48
    HGR_WIDTH = 280
    HGR_HEIGHT = 192
    TEXT_COLS = 40
    TEXT_ROWS = 24
    
    # Color tables
    GR_COLORS = [
        (0, 0, 0),       # 0: Black
        (227, 30, 96),   # 1: Magenta
        (96, 78, 189),   # 2: Dark Blue
        (255, 68, 253),  # 3: Purple
        (0, 163, 96),    # 4: Dark Green
        (156, 156, 156), # 5: Gray
        (20, 207, 253),  # 6: Medium Blue
        (208, 195, 255), # 7: Light Blue
        (96, 114, 3),    # 8: Brown
        (255, 106, 60),  # 9: Orange
        (156, 156, 156), # 10: Gray
        (255, 160, 208), # 11: Pink
        (20, 245, 60),   # 12: Light Green
        (208, 221, 141), # 13: Yellow
        (114, 255, 208), # 14: Aqua
        (255, 255, 255), # 15: White
    ]
    
    HGR_COLORS = [
        (0, 0, 0),       # 0: Black
        (20, 245, 60),   # 1: Green
        (255, 68, 253),  # 2: Purple/Violet
        (255, 255, 255), # 3: White
        (0, 0, 0),       # 4: Black (alt)
        (255, 106, 60),  # 5: Orange
        (20, 207, 253),  # 6: Blue
        (255, 255, 255), # 7: White (alt)
    ]
    
    def __init__(self, input_timeout: float = 30.0, execution_timeout: float = None, keep_window_open: bool = True,
                 autosnap_every: Optional[int] = None, autosnap_on_end: bool = False, artifact_mode: bool = False,
                 composite_blur: bool = False, statement_delay: float = 0.001):
        """Initialize the interpreter
        
        Args:
            input_timeout: Timeout in seconds for INPUT/GET commands (default: 30)
            execution_timeout: Timeout in seconds for program execution (default: None - no limit)
            keep_window_open: Keep pygame window open after program ends (default: True)
            autosnap_every: Automatically save a screenshot every N statements (default: None)
            autosnap_on_end: Save a screenshot when program ends (default: False)
            artifact_mode: Simulate Apple II NTSC artifact color rules (default: True)
            composite_blur: Apply composite horizontal blur effect (default: False)
            statement_delay: Delay in seconds after each statement to simulate Apple II speed (default: 0.001)
        """
        self.input_timeout = input_timeout
        self.execution_timeout = execution_timeout
        self.keep_window_open = keep_window_open
        self.autosnap_every = autosnap_every
        self.autosnap_on_end = autosnap_on_end
        self.artifact_mode = artifact_mode
        self.composite_blur = composite_blur
        self.statement_delay = statement_delay
        self.reset()
        
    def reset(self):
        """Reset the interpreter state"""
        # Program storage
        self.program: OrderedDict[int, str] = OrderedDict()
        
        # Variables
        self.variables: Dict[str, Union[float, str]] = {}
        self.arrays: Dict[str, List] = {}
        
        # Seed random number generator with current time for different results each run
        random.seed()
        
        # Execution state
        self.pc = 0  # Program counter (line number)
        self.running = False
        self.data_pointer = 0
        self.data_items: List[str] = []
        
        # Control flow stacks
        self.for_stack: List[Dict[str, Any]] = []
        self.gosub_stack: List[int] = []
        
        # Graphics state
        self.graphics_mode = 'TEXT'  # TEXT, GR, HGR, HGR2
        self.hgr_color = 3  # White
        self.gr_color = 15  # White
        self.hgr_x = 0
        self.hgr_y = 0
        self.hgr_last_plot_color = 3  # Color of last explicit HPLOT (not HPLOT TO)
        self.text_x = 0
        self.text_y = 0
        self.inverse = False
        self.flash = False
        # Hi-res page/mode state
        self.hgr_page = 1  # 1 or 2
        self.hgr_mixed = True  # mixed text overlay on bottom 4 lines
        
        # Pygame surfaces
        self.screen = None
        self.text_surface = None
        self.gr_surface = None
        self.hgr_surface = None
        self.hgr_page1_surface = None
        self.hgr_page2_surface = None
        # Hi-res backing memory (40 bytes * 192 lines per page)
        self.hgr_memory_page1 = None
        self.hgr_memory_page2 = None
        # Per-pixel white override flags for white colors (HCOLOR 3/7)
        self.hgr_white_page1 = None
        self.hgr_white_page2 = None
        # Per-pixel intended color index (for dense fills where artifact stripes would be unrealistic)
        self.hgr_color_page1 = None
        self.hgr_color_page2 = None
        
        # Input handling
        self.input_result = None
        self.input_thread = None
        self.waiting_for_input = False
        
        # Error handling
        self.error_handler_line = None
        self.last_error = None
        
        # Functions
        self.user_functions: Dict[str, Tuple[str, str]] = {}  # name -> (param, expression)
        # Counters
        self.statement_counter = 0
        self.current_line = 0
        
    def init_graphics(self):
        """Initialize pygame for graphics"""
        if not PYGAME_AVAILABLE:
            return
        
        if pygame.display.get_init():
            return
            
        pygame.init()
        # Create a window that can handle both text and graphics
        window_width = self.TEXT_COLS * 14  # 14 pixels per char width
        window_height = self.TEXT_ROWS * 16  # 16 pixels per char height
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Applesoft BASIC")
        
        # Load authentic Apple II font
        # Try Print Char 21 first (uppercase), then PR Number 3 (mixed case)
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_dir = os.path.join(script_dir, 'fonts')
        
        self.font = None
        for font_file in ['PrintChar21.ttf', 'PRNumber3.ttf']:
            font_path = os.path.join(font_dir, font_file)
            if os.path.exists(font_path):
                try:
                    # Apple II characters are 7x8 pixels, scale up 2x for 14x16
                    self.font = pygame.font.Font(font_path, 16)
                    break
                except:
                    pass
        
        # Fallback to monospace if Apple II fonts not found
        if not self.font:
            for font_name in ['Courier New', 'Consolas', 'Courier', 'monospace']:
                try:
                    self.font = pygame.font.SysFont(font_name, 20, bold=True)
                    if self.font:
                        break
                except:
                    continue
        
        # Last resort fallback
        if not self.font:
            self.font = pygame.font.Font(None, 24)
        
        # Create surfaces for different modes
        self.text_surface = pygame.Surface((window_width, window_height))
        self.text_surface.fill((0, 0, 0))
        
    def load_program(self, filename: str):
        """Load a BASIC program from a file"""
        self.program.clear()
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('//'):
                    self.parse_line(line)
        # Sort program by line numbers after loading
        self.program = OrderedDict(sorted(self.program.items()))
                    
    def parse_line(self, line: str):
        """Parse and store a program line"""
        line = line.strip()
        if not line:
            return
            
        # Check if it starts with a line number
        match = re.match(r'^(\d+)\s*(.*)', line)
        if match:
            line_num = int(match.group(1))
            statement = match.group(2).strip()
            if statement:
                self.program[line_num] = statement
            else:
                # Delete line
                if line_num in self.program:
                    del self.program[line_num]
        else:
            # Immediate mode - execute directly
            self.execute_statement(line, immediate=True)
            
    def run(self, start_line: Optional[int] = None):
        """Run the program from the beginning or a specific line"""
        if not self.program:
            print("No program to run")
            return
        
        # Initialize pygame for text display
        if PYGAME_AVAILABLE and self.graphics_mode == 'TEXT':
            self.init_graphics()
        
        # Track execution start time for timeout
        start_time = time.time()
            
        self.running = True
        self.data_pointer = 0
        self.for_stack.clear()
        self.gosub_stack.clear()
        
        # Collect all DATA items
        self.data_items = []
        for line_num, statement in self.program.items():
            if statement.upper().startswith('DATA '):
                data_str = statement[5:].strip()
                items = [item.strip() for item in data_str.split(',')]
                self.data_items.extend(items)
        
        # Find starting line
        if start_line is None:
            line_nums = list(self.program.keys())
            if not line_nums:
                return
            self.pc = line_nums[0]
        else:
            self.pc = start_line
            
        try:
            while self.running:
                # Check execution timeout
                if self.execution_timeout and (time.time() - start_time) > self.execution_timeout:
                    print(f"\nExecution timeout after {self.execution_timeout} seconds")
                    break
                
                # Handle pygame events
                if PYGAME_AVAILABLE and pygame.display.get_init():
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            return
                
                # Find current line
                if self.pc not in self.program:
                    # Find next line
                    found = False
                    for line_num in self.program.keys():
                        if line_num >= self.pc:
                            self.pc = line_num
                            found = True
                            break
                    if not found:
                        break
                        
                if self.pc in self.program:
                    statement = self.program[self.pc]
                    next_line = self.get_next_line(self.pc)
                    current_pc = self.pc
                    self.current_line = self.pc
                    
                    try:
                        self.execute_statement(statement)
                        # Update display after each statement to show graphics in real-time
                        self.update_display()
                        # Add delay to simulate Apple II speed
                        if self.statement_delay > 0:
                            time.sleep(self.statement_delay)
                        # Auto-screenshot every N statements if enabled
                        self.statement_counter += 1
                        if self.autosnap_every and (self.statement_counter % int(self.autosnap_every) == 0):
                            try:
                                self.save_screenshot('autosnap')
                            except Exception:
                                pass
                    except ApplesoftError as e:
                        if self.error_handler_line:
                            self.pc = self.error_handler_line
                            self.last_error = str(e)
                            continue
                        else:
                            # Apple-like message plus detail
                            if self.current_line:
                                print(f"SYNTAX ERROR IN {self.current_line}")
                            else:
                                print("SYNTAX ERROR")
                            print(f"Detail: {e}")
                            break
                    
                    # Move to next line (unless changed by GOTO, NEXT, etc.)
                    if self.pc == current_pc:
                        if next_line is None:
                            break
                        self.pc = next_line
                else:
                    break
                    
        except KeyboardInterrupt:
            print(f"\nBreak in line {self.pc}")
        finally:
            self.running = False
            
        # Auto-screenshot at end if enabled
        if self.autosnap_on_end and PYGAME_AVAILABLE and pygame.display.get_init():
            try:
                self.save_screenshot('final')
            except Exception:
                pass
        # Keep pygame window open until user closes it (if enabled)
        if self.keep_window_open and PYGAME_AVAILABLE and pygame.display.get_init():
            print("\nProgram ended. Close the window to exit.")
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                time.sleep(0.05)  # Reduce CPU usage while waiting
            
    def get_current_line(self) -> int:
        """Get the current line number"""
        return self.pc
        
    def get_next_line(self, line_num: int) -> Optional[int]:
        """Get the next line number after the given line"""
        line_nums = list(self.program.keys())
        try:
            idx = line_nums.index(line_num)
            if idx + 1 < len(line_nums):
                return line_nums[idx + 1]
        except ValueError:
            pass
        return None
        
    def execute_statement(self, statement: str, immediate: bool = False):
        """Execute a single statement"""
        if not statement:
            return
            
        statement = statement.strip()
        
        # Check if this is a REM statement - if so, don't split on colons
        if statement.upper().startswith('REM '):
            self.execute_single_statement(statement, immediate)
            return
        
        # Handle multiple statements on one line (separated by :)
        if ':' in statement and not self.is_in_string(statement, statement.index(':')):
            parts = self.split_on_colon(statement)
            for part in parts:
                self.execute_single_statement(part.strip(), immediate)
        else:
            self.execute_single_statement(statement, immediate)
            
    def is_in_string(self, text: str, pos: int) -> bool:
        """Check if position is inside a string literal"""
        in_string = False
        for i in range(pos):
            if text[i] == '"':
                in_string = not in_string
        return in_string
        
    def split_on_colon(self, statement: str) -> List[str]:
        """Split statement on colons, but not inside strings"""
        parts = []
        current = []
        in_string = False
        
        for char in statement:
            if char == '"':
                in_string = not in_string
                current.append(char)
            elif char == ':' and not in_string:
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)
                
        if current:
            parts.append(''.join(current))
            
        return parts
        
    def execute_single_statement(self, statement: str, immediate: bool = False):
        """Execute a single statement (no colons)"""
        statement = statement.strip()
        if not statement:
            return
        
        # Handle HCOLOR= and COLOR= specially (they can have = without space)
        if statement.upper().startswith('HCOLOR=') or statement.upper().startswith('HCOLOR ='):
            self.cmd_hcolor(statement[6:].strip())  # Skip "HCOLOR"
            return
        if statement.upper().startswith('COLOR=') or statement.upper().startswith('COLOR ='):
            self.cmd_color(statement[5:].strip())  # Skip "COLOR"
            return
            
        # Get command
        parts = statement.split(None, 1)
        if not parts:
            return
            
        cmd = parts[0].upper()
        args = parts[1] if len(parts) > 1 else ''
        
        # Command dispatch
        if cmd == 'PRINT' or cmd == '?':
            self.cmd_print(args)
        elif cmd == 'LET':
            self.cmd_let(args)
        elif cmd == 'GOTO':
            self.cmd_goto(args)
        elif cmd == 'GOSUB':
            self.cmd_gosub(args)
        elif cmd == 'RETURN':
            self.cmd_return()
        elif cmd == 'IF':
            self.cmd_if(args)
        elif cmd == 'FOR':
            self.cmd_for(args)
        elif cmd == 'NEXT':
            self.cmd_next(args)
        elif cmd == 'INPUT':
            self.cmd_input(args)
        elif cmd == 'GET':
            self.cmd_get(args)
        elif cmd == 'READ':
            self.cmd_read(args)
        elif cmd == 'DATA':
            pass  # DATA is passive
        elif cmd == 'RESTORE':
            self.cmd_restore()
        elif cmd == 'DIM':
            self.cmd_dim(args)
        elif cmd == 'REM':
            pass  # Comment
        elif cmd == 'END' or cmd == 'STOP':
            self.running = False
        elif cmd == 'RUN':
            if not immediate:
                self.run()
        elif cmd == 'LIST':
            self.cmd_list(args)
        elif cmd == 'NEW':
            self.program.clear()
            self.variables.clear()
            self.arrays.clear()
        elif cmd == 'CLEAR':
            self.variables.clear()
            self.arrays.clear()
        elif cmd == 'HOME':
            self.cmd_home()
        elif cmd == 'TEXT':
            self.cmd_text()
        elif cmd == 'GR':
            self.cmd_gr()
        elif cmd == 'HGR':
            self.cmd_hgr()
        elif cmd == 'HGR2':
            self.cmd_hgr2()
        elif cmd == 'COLOR':
            self.cmd_color(args)
        elif cmd == 'PLOT':
            self.cmd_plot(args)
        elif cmd == 'HLIN':
            self.cmd_hlin(args)
        elif cmd == 'VLIN':
            self.cmd_vlin(args)
        elif cmd == 'HCOLOR':
            self.cmd_hcolor(args)
        elif cmd == 'HPLOT':
            self.cmd_hplot(args)
        elif cmd == 'HTAB':
            self.cmd_htab(args)
        elif cmd == 'VTAB':
            self.cmd_vtab(args)
        elif cmd == 'INVERSE':
            self.inverse = True
        elif cmd == 'NORMAL':
            self.inverse = False
        elif cmd == 'FLASH':
            self.flash = True
        elif cmd == 'POKE':
            self.cmd_poke(args)
        elif cmd == 'CALL':
            self.cmd_call(args)
        elif cmd == 'DEF':
            self.cmd_def(args)
        elif cmd == 'ONERR':
            self.cmd_onerr(args)
        elif cmd == 'RESUME':
            self.cmd_resume()
        elif cmd == 'ON':
            self.cmd_on(args)
        elif cmd == 'WAIT':
            self.cmd_wait(args)
        elif '=' in statement and not any(op in statement for op in ['<', '>', '==']):
            # Assignment without LET (must be checked after all commands with =)
            self.cmd_let(statement)
        else:
            # Try as expression/assignment
            if '=' in statement:
                self.cmd_let(statement)
            else:
                raise ApplesoftError(f"Syntax error: Unknown command '{cmd}'")
                
    def cmd_print(self, args: str):
        """PRINT command"""
        if not args:
            self.render_text_to_surface('\n')
            return
            
        output = []
        # Parse print items
        items = self.parse_print_items(args)
        
        for item in items:
            if item == ';':
                continue  # Semicolon suppresses newline/spacing
            elif item == ',':
                # Tab to next column (every 10 chars in Applesoft)
                if output:
                    current_len = len(''.join(str(x) for x in output))
                    spaces = 10 - (current_len % 10)
                    output.append(' ' * spaces)
            elif isinstance(item, str) and item.startswith('TAB('):
                # TAB function
                n = self.evaluate(item[4:-1])
                if output:
                    current_len = len(''.join(str(x) for x in output))
                    if int(n) > current_len:
                        output.append(' ' * (int(n) - current_len))
            elif isinstance(item, str) and item.startswith('SPC('):
                # SPC function
                n = self.evaluate(item[4:-1])
                output.append(' ' * int(n))
            else:
                # Evaluate and print
                value = self.evaluate(item)
                if isinstance(value, float):
                    # Format numbers with space padding
                    if value >= 0:
                        output.append(' ' + self.format_number(value) + ' ')
                    else:
                        output.append(self.format_number(value) + ' ')
                else:
                    output.append(str(value))
                    
        text = ''.join(str(x) for x in output)
        
        # Check if statement ends with semicolon or comma
        ends_with_sep = args.rstrip().endswith(';') or args.rstrip().endswith(',')
        
        # Always print to console for now (can be removed later if desired)
        if ends_with_sep:
            print(text, end='')
        else:
            print(text)
        
        # Also render to pygame if available (supports TEXT and HGR mixed mode)
        if PYGAME_AVAILABLE:
            if ends_with_sep:
                self.render_text_to_surface(text)
            else:
                self.render_text_to_surface(text + '\n')
            
    def parse_print_items(self, args: str) -> List[str]:
        """Parse PRINT statement items"""
        items = []
        current = []
        in_string = False
        paren_depth = 0
        
        for char in args:
            if char == '"':
                in_string = not in_string
                current.append(char)
            elif char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char in [';', ','] and not in_string and paren_depth == 0:
                if current:
                    items.append(''.join(current).strip())
                    current = []
                items.append(char)
            else:
                current.append(char)
                
        if current:
            items.append(''.join(current).strip())
            
        return items
        
    def format_number(self, n: float) -> str:
        """Format a number for output"""
        if n == int(n):
            return str(int(n))
        else:
            # Remove trailing zeros
            s = f"{n:.6f}".rstrip('0').rstrip('.')
            return s
            
    def cmd_let(self, args: str):
        """LET command (assignment)"""
        # Remove LET if present
        if args.upper().startswith('LET '):
            args = args[4:].strip()
            
        # Find the = sign
        eq_pos = args.find('=')
        if eq_pos == -1:
            raise ApplesoftError("Syntax error: Expected '='")
            
        var_part = args[:eq_pos].strip()
        expr_part = args[eq_pos + 1:].strip()
        
        # Check if it's an array element
        if '(' in var_part:
            var_name = var_part[:var_part.index('(')].upper()
            indices_str = var_part[var_part.index('(') + 1:var_part.rindex(')')]
            indices = [int(self.evaluate(idx.strip())) for idx in indices_str.split(',')]
            
            value = self.evaluate(expr_part)
            
            # Set array element
            # Auto-create array with default dimension if not already dimensioned
            # In Applesoft BASIC, arrays default to 0-10 (11 elements) if not explicitly dimensioned
            if var_name not in self.arrays:
                if len(indices) == 1:
                    self.arrays[var_name] = [0] * 11
                elif len(indices) == 2:
                    self.arrays[var_name] = [[0] * 11 for _ in range(11)]
                
            arr = self.arrays[var_name]
            if len(indices) == 1:
                arr[indices[0]] = value
            elif len(indices) == 2:
                arr[indices[0]][indices[1]] = value
        else:
            # Simple variable
            var_name = var_part.upper()
            value = self.evaluate(expr_part)
            self.variables[var_name] = value
            
    def cmd_goto(self, args: str):
        """GOTO command"""
        line_num = int(self.evaluate(args))
        if line_num not in self.program:
            raise ApplesoftError(f"Undefined statement: {line_num}")
        self.pc = line_num
        
    def cmd_gosub(self, args: str):
        """GOSUB command"""
        line_num = int(self.evaluate(args))
        if line_num not in self.program:
            raise ApplesoftError(f"Undefined statement: {line_num}")
        next_line = self.get_next_line(self.pc)
        if next_line:
            self.gosub_stack.append(next_line)
        else:
            self.gosub_stack.append(-1)  # Mark end
        self.pc = line_num
        
    def cmd_return(self):
        """RETURN command"""
        if not self.gosub_stack:
            raise ApplesoftError("Return without gosub")
        return_line = self.gosub_stack.pop()
        if return_line == -1:
            self.running = False
        else:
            self.pc = return_line
            
    def cmd_if(self, args: str):
        """IF command"""
        # Find THEN or GOTO
        then_pos = args.upper().find(' THEN ')
        goto_pos = args.upper().find(' GOTO ')
        
        if then_pos != -1:
            condition = args[:then_pos].strip()
            action = args[then_pos + 6:].strip()
        elif goto_pos != -1:
            condition = args[:goto_pos].strip()
            action = 'GOTO ' + args[goto_pos + 6:].strip()
        else:
            # Direct line number after condition
            parts = args.split()
            condition = ' '.join(parts[:-1])
            action = 'GOTO ' + parts[-1]
            
        # Evaluate condition
        result = self.evaluate(condition)
        
        # In BASIC, non-zero is true
        if result:
            # Check if action is a line number
            if action.isdigit():
                self.cmd_goto(action)
            else:
                self.execute_statement(action)
                
    def cmd_for(self, args: str):
        """FOR command"""
        # Parse: FOR var = start TO end [STEP step]
        match = re.match(r'(\w+)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$', args, re.IGNORECASE)
        if not match:
            raise ApplesoftError("Syntax error in FOR")
            
        var = match.group(1).upper()
        start = self.evaluate(match.group(2))
        end = self.evaluate(match.group(3))
        step = self.evaluate(match.group(4)) if match.group(4) else 1
        
        # Initialize loop variable
        self.variables[var] = start
        
        # Push loop info onto stack
        self.for_stack.append({
            'var': var,
            'end': end,
            'step': step,
            'line': self.pc
        })
        
    def cmd_next(self, args: str):
        """NEXT command"""
        if not self.for_stack:
            raise ApplesoftError("Next without for")
            
        var = args.strip().upper() if args.strip() else None
        
        loop = self.for_stack[-1]
        
        if var and var != loop['var']:
            raise ApplesoftError("Next without for")
            
        # Increment loop variable
        self.variables[loop['var']] += loop['step']
        
        # Check if done
        if loop['step'] > 0:
            done = self.variables[loop['var']] > loop['end']
        else:
            done = self.variables[loop['var']] < loop['end']
            
        if done:
            self.for_stack.pop()
            # Continue to next line after NEXT
        else:
            # Return to the line AFTER the FOR (the first line of the loop body)
            # We need to find the next line after the FOR line
            for_line = loop['line']
            next_after_for = self.get_next_line(for_line)
            if next_after_for:
                self.pc = next_after_for
            else:
                # No line after FOR? Something is wrong
                self.for_stack.pop()
            
    def cmd_input(self, args: str):
        """INPUT command"""
        # Parse prompt if present
        prompt = ''
        vars_str = args
        
        if '"' in args:
            # Extract prompt
            first_quote = args.index('"')
            second_quote = args.index('"', first_quote + 1)
            prompt = args[first_quote + 1:second_quote]
            vars_str = args[second_quote + 1:].strip()
            if vars_str.startswith(';') or vars_str.startswith(','):
                vars_str = vars_str[1:].strip()
                
        # Get variable names
        var_names = [v.strip().upper() for v in vars_str.split(',')]
        
        # Get input with timeout
        if prompt:
            print(prompt, end='')
        print('? ', end='', flush=True)
        
        input_str = self.get_input_with_timeout()
        
        if input_str is None:
            raise ApplesoftError(f"Input timeout after {self.input_timeout} seconds")
            
        # Parse input values
        values = [v.strip() for v in input_str.split(',')]
        
        for i, var in enumerate(var_names):
            if i < len(values):
                # Try to parse as number, else string
                val = values[i]
                if var.endswith('$'):
                    # String variable
                    self.variables[var] = val.strip('"')
                else:
                    # Numeric variable
                    try:
                        self.variables[var] = float(val)
                    except ValueError:
                        raise ApplesoftError("Type mismatch")
            else:
                raise ApplesoftError("Not enough input values")
                
    def cmd_get(self, args: str):
        """GET command - get a single character"""
        var = args.strip().upper()
        
        # Get single character with timeout
        char = self.get_char_with_timeout()
        
        if char is None:
            raise ApplesoftError(f"Input timeout after {self.input_timeout} seconds")
            
        if var.endswith('$'):
            self.variables[var] = char
        else:
            self.variables[var] = ord(char)
            
    def get_input_with_timeout(self) -> Optional[str]:
        """Get input with timeout"""
        self.input_result = None
        self.waiting_for_input = True
        
        def input_thread():
            try:
                self.input_result = input()
            except:
                pass
                
        thread = threading.Thread(target=input_thread, daemon=True)
        thread.start()
        thread.join(timeout=self.input_timeout)
        
        self.waiting_for_input = False
        return self.input_result
        
    def get_char_with_timeout(self) -> Optional[str]:
        """Get single character with timeout"""
        # For simplicity, just get a line and return first char
        result = self.get_input_with_timeout()
        if result:
            return result[0] if result else ''
        return None
        
    def cmd_read(self, args: str):
        """READ command"""
        var_names = [v.strip().upper() for v in args.split(',')]
        
        for var in var_names:
            if self.data_pointer >= len(self.data_items):
                raise ApplesoftError("Out of data")
                
            val = self.data_items[self.data_pointer]
            self.data_pointer += 1
            
            if var.endswith('$'):
                self.variables[var] = val.strip('"')
            else:
                try:
                    self.variables[var] = float(val)
                except ValueError:
                    raise ApplesoftError("Type mismatch")
                    
    def cmd_restore(self):
        """RESTORE command"""
        self.data_pointer = 0
        
    def cmd_dim(self, args: str):
        """DIM command"""
        # Parse array declarations
        arrays = [a.strip() for a in args.split(',')]
        
        for arr_decl in arrays:
            match = re.match(r'(\w+)\s*\((.+)\)', arr_decl)
            if not match:
                raise ApplesoftError("Syntax error in DIM")
                
            name = match.group(1).upper()
            dims_str = match.group(2)
            dims = [int(self.evaluate(d.strip())) + 1 for d in dims_str.split(',')]
            
            # Create array
            if len(dims) == 1:
                self.arrays[name] = [0] * dims[0]
            elif len(dims) == 2:
                self.arrays[name] = [[0] * dims[1] for _ in range(dims[0])]
            else:
                raise ApplesoftError("Too many dimensions")
                
    def cmd_list(self, args: str):
        """LIST command"""
        if not args:
            for line_num, statement in self.program.items():
                print(f"{line_num} {statement}")
        else:
            # Parse range
            if '-' in args:
                parts = args.split('-')
                start = int(parts[0]) if parts[0] else min(self.program.keys())
                end = int(parts[1]) if parts[1] else max(self.program.keys())
            else:
                start = end = int(args)
                
            for line_num, statement in self.program.items():
                if start <= line_num <= end:
                    print(f"{line_num} {statement}")
                    
    def render_char_to_surface(self, char: str):
        """Render a single character to the text surface at the current cursor position"""
        if not PYGAME_AVAILABLE or not self.screen or not self.font:
            return
        
        # In HGR/HGR2 mode, start text at row 20 (bottom 4 lines)
        if self.graphics_mode in ['HGR', 'HGR2']:
            min_text_row = 20
            max_text_row = 23
        else:
            min_text_row = 0
            max_text_row = self.TEXT_ROWS - 1
        
        # Handle special characters
        if char == '\n':
            self.text_y += 1
            self.text_x = 0
            if self.text_y > max_text_row:
                # Scroll up within text area
                self.scroll_text_up()
                self.text_y = max_text_row
        else:
            # Render character at current position
            x_pixel = self.text_x * 14
            y_pixel = self.text_y * 16
            
            # Render character with appropriate colors
            if self.inverse:
                char_surface = self.font.render(char, True, (0, 0, 0), (255, 255, 255))
            else:
                char_surface = self.font.render(char, True, (255, 255, 255), (0, 0, 0))
            
            self.text_surface.blit(char_surface, (x_pixel, y_pixel))
            
            self.text_x += 1
            if self.text_x >= self.TEXT_COLS:
                self.text_x = 0
                self.text_y += 1
                if self.text_y > max_text_row:
                    self.scroll_text_up()
                    self.text_y = max_text_row
    
    def render_text_to_surface(self, text: str):
        """Render text string to the text surface"""
        if not PYGAME_AVAILABLE or not self.screen:
            return
        
        for char in text:
            self.render_char_to_surface(char)
    
    def scroll_text_up(self):
        """Scroll text up by one line"""
        if not PYGAME_AVAILABLE or not self.screen or not self.text_surface:
            return
        
        # Copy everything up by one line height (16 pixels)
        temp_surface = self.text_surface.copy()
        self.text_surface.fill((0, 0, 0))
        self.text_surface.blit(temp_surface, (0, -16))
        
    def cmd_home(self):
        """HOME command - clear screen"""
        if PYGAME_AVAILABLE and self.screen:
            # In TEXT mode, clear entire text surface
            if self.graphics_mode == 'TEXT':
                self.text_surface.fill((0, 0, 0))
                self.text_x = 0
                self.text_y = 0
            else:
                # In graphics modes, clear only the text area and reset cursor
                if not self.text_surface:
                    return
                # Clear bottom 4 text rows (rows 20-23)
                rect = pygame.Rect(0, 320, 560, 64)
                pygame.draw.rect(self.text_surface, (0, 0, 0), rect)
                self.text_x = 0
                self.text_y = 20
        else:
            # Clear console
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
            print('\033[2J\033[H', end='')
            
    def cmd_text(self):
        """TEXT command - switch to text mode"""
        self.graphics_mode = 'TEXT'
        if PYGAME_AVAILABLE:
            self.init_graphics()
            
    def cmd_gr(self):
        """GR command - switch to low-res graphics"""
        self.graphics_mode = 'GR'
        if PYGAME_AVAILABLE:
            self.init_graphics()
            # Create GR surface
            self.gr_surface = pygame.Surface((self.GR_WIDTH * 14, self.GR_HEIGHT * 8))
            self.gr_surface.fill((0, 0, 0))
            
    def cmd_hgr(self):
        """HGR command - switch to hi-res graphics page 1"""
        self.graphics_mode = 'HGR'
        self.hgr_page = 1
        self.hgr_mixed = True  # HGR defaults to mixed mode with text
        if PYGAME_AVAILABLE:
            if not pygame.display.get_init():
                self.init_graphics()
            # Ensure screen is the right size for HGR
            if not self.screen or self.screen.get_size() != (560, 384):
                pygame.init()
                self.screen = pygame.display.set_mode((560, 384))
                pygame.display.set_caption("Applesoft BASIC")
                # Need to reload font after pygame.init()
                import os
                script_dir = os.path.dirname(os.path.abspath(__file__))
                font_dir = os.path.join(script_dir, 'fonts')
                self.font = None
                for font_file in ['PrintChar21.ttf', 'PRNumber3.ttf']:
                    font_path = os.path.join(font_dir, font_file)
                    if os.path.exists(font_path):
                        try:
                            self.font = pygame.font.Font(font_path, 16)
                            break
                        except:
                            pass
                if not self.font:
                    self.font = pygame.font.Font(None, 24)
            # Create/clear HGR page 1 surface and select it
            if not self.hgr_page1_surface:
                self.hgr_page1_surface = pygame.Surface((560, 384))
            self.hgr_page1_surface.fill((0, 0, 0))
            self.hgr_surface = self.hgr_page1_surface
            # Create text surface if needed (don't clear it - preserve existing text)
            if not self.text_surface:
                self.text_surface = pygame.Surface((560, 384))
                self.text_surface.fill((0, 0, 0))
        self._ensure_hgr_memory()
        self._clear_hgr_memory_page(1)
        self._set_active_hgr_memory(1)
        if self.artifact_mode and PYGAME_AVAILABLE and self.hgr_surface:
            self._render_full_hgr_page()
        # Don't reset cursor - leave it where it was so text positioning is preserved
            
    def cmd_hgr2(self):
        """HGR2 command - switch to hi-res graphics page 2"""
        self.graphics_mode = 'HGR2'
        self.hgr_page = 2
        self.hgr_mixed = False  # HGR2 defaults to full screen graphics (no text)
        if PYGAME_AVAILABLE:
            if not pygame.display.get_init():
                self.init_graphics()
            # Ensure screen is the right size for HGR
            if not self.screen or self.screen.get_size() != (560, 384):
                pygame.init()
                self.screen = pygame.display.set_mode((560, 384))
                pygame.display.set_caption("Applesoft BASIC")
            # Create/clear HGR page 2 surface and select it
            if not self.hgr_page2_surface:
                self.hgr_page2_surface = pygame.Surface((560, 384))
            self.hgr_page2_surface.fill((0, 0, 0))
            self.hgr_surface = self.hgr_page2_surface
            # Create text surface if needed (don't clear it - preserve existing text)
            if not self.text_surface:
                self.text_surface = pygame.Surface((560, 384))
                self.text_surface.fill((0, 0, 0))
        self._ensure_hgr_memory()
        self._clear_hgr_memory_page(2)
        self._set_active_hgr_memory(2)
        if self.artifact_mode and PYGAME_AVAILABLE and self.hgr_surface:
            self._render_full_hgr_page()
        # Don't reset cursor - leave it where it was
            
    def cmd_color(self, args: str):
        """COLOR command - set low-res color"""
        if '=' in args:
            args = args.split('=')[1].strip()
        color = int(self.evaluate(args))
        self.gr_color = color % 16
        
    def cmd_plot(self, args: str):
        """PLOT command - plot a point in low-res graphics"""
        parts = [p.strip() for p in args.split(',')]
        x = int(self.evaluate(parts[0]))
        y = int(self.evaluate(parts[1]))
        
        if self.graphics_mode == 'GR' and PYGAME_AVAILABLE and self.gr_surface:
            color = self.GR_COLORS[self.gr_color]
            # Each GR pixel is 14x8 screen pixels (approx)
            rect = pygame.Rect(x * 14, y * 8, 14, 8)
            pygame.draw.rect(self.gr_surface, color, rect)
            
    def cmd_hlin(self, args: str):
        """HLIN command - horizontal line in low-res"""
        # HLIN x1,x2 AT y
        match = re.match(r'(.+?),(.+?)\s+AT\s+(.+)', args, re.IGNORECASE)
        if not match:
            raise ApplesoftError("Syntax error in HLIN")
            
        x1 = int(self.evaluate(match.group(1)))
        x2 = int(self.evaluate(match.group(2)))
        y = int(self.evaluate(match.group(3)))
        
        if self.graphics_mode == 'GR' and PYGAME_AVAILABLE and self.gr_surface:
            color = self.GR_COLORS[self.gr_color]
            for x in range(min(x1, x2), max(x1, x2) + 1):
                rect = pygame.Rect(x * 14, y * 8, 14, 8)
                pygame.draw.rect(self.gr_surface, color, rect)
                
    def cmd_vlin(self, args: str):
        """VLIN command - vertical line in low-res"""
        # VLIN y1,y2 AT x
        match = re.match(r'(.+?),(.+?)\s+AT\s+(.+)', args, re.IGNORECASE)
        if not match:
            raise ApplesoftError("Syntax error in VLIN")
            
        y1 = int(self.evaluate(match.group(1)))
        y2 = int(self.evaluate(match.group(2)))
        x = int(self.evaluate(match.group(3)))
        
        if self.graphics_mode == 'GR' and PYGAME_AVAILABLE and self.gr_surface:
            color = self.GR_COLORS[self.gr_color]
            for y in range(min(y1, y2), max(y1, y2) + 1):
                rect = pygame.Rect(x * 14, y * 8, 14, 8)
                pygame.draw.rect(self.gr_surface, color, rect)

    # ---- HGR artifact helpers -------------------------------------------------

    def _ensure_hgr_memory(self):
        """Allocate hi-res memory pages if needed (40 bytes * 192 rows)."""
        if self.hgr_memory_page1 is None:
            self.hgr_memory_page1 = [[0] * 40 for _ in range(self.HGR_HEIGHT)]
        if self.hgr_memory_page2 is None:
            self.hgr_memory_page2 = [[0] * 40 for _ in range(self.HGR_HEIGHT)]
        if self.hgr_white_page1 is None:
            self.hgr_white_page1 = [[False] * self.HGR_WIDTH for _ in range(self.HGR_HEIGHT)]
        if self.hgr_white_page2 is None:
            self.hgr_white_page2 = [[False] * self.HGR_WIDTH for _ in range(self.HGR_HEIGHT)]
        if self.hgr_color_page1 is None:
            self.hgr_color_page1 = [[-1] * self.HGR_WIDTH for _ in range(self.HGR_HEIGHT)]
        if self.hgr_color_page2 is None:
            self.hgr_color_page2 = [[-1] * self.HGR_WIDTH for _ in range(self.HGR_HEIGHT)]

    def _get_active_hgr_memory(self):
        """Return backing memory for the active HGR page."""
        self._ensure_hgr_memory()
        return self.hgr_memory_page2 if self.hgr_page == 2 else self.hgr_memory_page1

    def _get_active_white_map(self):
        """Return white-override map for the active page."""
        self._ensure_hgr_memory()
        return self.hgr_white_page2 if self.hgr_page == 2 else self.hgr_white_page1

    def _get_active_color_map(self):
        """Return intended color map for the active page."""
        self._ensure_hgr_memory()
        return self.hgr_color_page2 if self.hgr_page == 2 else self.hgr_color_page1

    def _set_active_hgr_memory(self, page: int):
        """Switch the backing memory to the given page."""
        self.hgr_page = page
        self._ensure_hgr_memory()

    def _clear_hgr_memory_page(self, page: int):
        """Clear a page's backing memory to black."""
        self._ensure_hgr_memory()
        target = self.hgr_memory_page2 if page == 2 else self.hgr_memory_page1
        whites = self.hgr_white_page2 if page == 2 else self.hgr_white_page1
        colors = self.hgr_color_page2 if page == 2 else self.hgr_color_page1
        for y in range(self.HGR_HEIGHT):
            target[y] = [0] * 40
            whites[y] = [False] * self.HGR_WIDTH
            colors[y] = [-1] * self.HGR_WIDTH

    def _artifact_color_for_pixel(self, memory, whites, colors, x: int, y: int):
        """Compute NTSC artifact color for a single pixel using hi-res rules."""
        byte_idx = x // 7
        bit_idx = x % 7
        byte_val = memory[y][byte_idx]
        if not (byte_val & (1 << bit_idx)):
            return (0, 0, 0)

        if whites[y][x]:
            return self.HGR_COLORS[3]

        # If we know the intended color for this lit pixel, honor it directly to avoid zebra artifacts
        intended = colors[y][x]
        if intended is not None and intended >= 0:
            return self.HGR_COLORS[intended % len(self.HGR_COLORS)]

        hi = (byte_val & 0x80) != 0
        is_odd = (x % 2 == 1)
        if hi:
            return self.HGR_COLORS[5] if is_odd else self.HGR_COLORS[6]  # orange / blue
        return self.HGR_COLORS[1] if is_odd else self.HGR_COLORS[2]      # green / purple

    def _draw_artifact_pixel(self, x: int, y: int, color: Tuple[int, int, int]):
        """Blit a single 2x2 pixel to the HGR surface."""
        if not (PYGAME_AVAILABLE and self.hgr_surface):
            return
        pygame.draw.rect(self.hgr_surface, color, pygame.Rect(x * 2, y * 2, 2, 2))

    def _refresh_artifact_byte(self, y: int, byte_idx: int):
        """Repaint pixels for a byte and its neighborhood after a change."""
        if byte_idx < 0 or byte_idx >= 40:
            return
        memory = self._get_active_hgr_memory()
        whites = self._get_active_white_map()
        colors = self._get_active_color_map()
        base_x = byte_idx * 7
        for i in range(7):
            x = base_x + i
            if x >= self.HGR_WIDTH:
                break
            color = self._artifact_color_for_pixel(memory, whites, colors, x, y)
            self._draw_artifact_pixel(x, y, color)

    def _render_full_hgr_page(self):
        """Render the entire active HGR page from backing memory."""
        if not (PYGAME_AVAILABLE and self.hgr_surface):
            return
        memory = self._get_active_hgr_memory()
        whites = self._get_active_white_map()
        colors = self._get_active_color_map()
        for y in range(self.HGR_HEIGHT):
            for byte_idx in range(40):
                base_x = byte_idx * 7
                for i in range(7):
                    x = base_x + i
                    if x >= self.HGR_WIDTH:
                        break
                    color = self._artifact_color_for_pixel(memory, whites, colors, x, y)
                    self._draw_artifact_pixel(x, y, color)

    def _plot_artifact_pixel(self, x: int, y: int, color_index: int):
        """Plot a single HGR pixel honoring NTSC artifact rules."""
        if not (0 <= x < self.HGR_WIDTH and 0 <= y < self.HGR_HEIGHT):
            return
        if not (PYGAME_AVAILABLE and self.hgr_surface):
            return

        memory = self._get_active_hgr_memory()
        whites = self._get_active_white_map()
        colors = self._get_active_color_map()
        byte_idx = x // 7
        bit_idx = x % 7

        hi_flag = 1 if color_index >= 4 else 0
        set_on = color_index not in (0, 4)
        force_white = color_index in (3, 7)

        byte_val = memory[y][byte_idx]
        # Update palette bit first so neighbors render correctly
        if hi_flag:
            byte_val |= 0x80
        else:
            byte_val &= 0x7F

        if set_on:
            byte_val |= (1 << bit_idx)
        else:
            byte_val &= ~(1 << bit_idx)
            whites[y][x] = False
        if force_white and set_on:
            whites[y][x] = True
        elif not set_on:
            whites[y][x] = False

        if set_on:
            colors[y][x] = color_index
        else:
            colors[y][x] = -1

        memory[y][byte_idx] = byte_val

        # Repaint this byte and its neighbors so white blooming is correct
        for b in (byte_idx - 1, byte_idx, byte_idx + 1):
            self._refresh_artifact_byte(y, b)

    def _draw_line_artifact(self, x1: int, y1: int, x2: int, y2: int, color_to_use: int):
        """Bresenham line in artifact mode over the 280x192 grid."""
        if not (PYGAME_AVAILABLE and self.hgr_surface):
            return
        dx = abs(x2 - x1)
        sx = 1 if x1 < x2 else -1
        dy = -abs(y2 - y1)
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            self._plot_artifact_pixel(x1, y1, color_to_use)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy
                
    def cmd_hcolor(self, args: str):
        """HCOLOR command - set hi-res color"""
        if '=' in args:
            args = args.split('=')[1].strip()
        color = int(self.evaluate(args))
        self.hgr_color = color % 8
        
    def _draw_line_bresenham(self, x1: int, y1: int, x2: int, y2: int, color: tuple):
        """Draw a line using Bresenham algorithm directly on pygame surface"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            rect = pygame.Rect(x * 2, y * 2, 2, 2)
            self.hgr_surface.fill(color, rect)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    
    def cmd_hplot(self, args: str):
        """HPLOT command - plot in hi-res graphics"""
        # Can be: HPLOT x,y or HPLOT x,y TO x2,y2
        # Also: HPLOT TO x,y (draw line from last position)
        # Important: HPLOT TO uses the color from the last explicit HPLOT, not current HCOLOR

        artifact_active = self.artifact_mode and self.graphics_mode in ['HGR', 'HGR2']

        if args.upper().strip().startswith('TO '):
            # Draw line from last position to x,y using LAST PLOTTED color
            args = args[2:].strip()  # Remove 'TO '
            parts = [p.strip() for p in args.split(',')]
            x2 = int(self.evaluate(parts[0]))
            y2 = int(self.evaluate(parts[1]))
            
            if artifact_active:
                self._draw_line_artifact(self.hgr_x, self.hgr_y, x2, y2, self.hgr_last_plot_color)
            elif self.graphics_mode in ['HGR', 'HGR2'] and PYGAME_AVAILABLE and self.hgr_surface:
                color = self.HGR_COLORS[self.hgr_last_plot_color]
                pygame.draw.line(self.hgr_surface, color, 
                               (self.hgr_x * 2, self.hgr_y * 2), 
                               (x2 * 2, y2 * 2), 2)
            self.hgr_x = x2
            self.hgr_y = y2
        else:
            # Check if there's a TO in the middle (x1,y1 TO x2,y2)
            if ' TO ' in args.upper():
                parts = args.upper().split(' TO ')
                first_part = parts[0].strip()
                second_part = parts[1].strip()
                
                # Parse first coordinate
                coords1 = [p.strip() for p in first_part.split(',')]
                x1 = int(self.evaluate(coords1[0]))
                y1 = int(self.evaluate(coords1[1]))
                
                # Parse second coordinate
                coords2 = [p.strip() for p in second_part.split(',')]
                x2 = int(self.evaluate(coords2[0]))
                y2 = int(self.evaluate(coords2[1]))
                
                # HPLOT x,y TO x2,y2 - first plots at x,y with current HCOLOR, then draws line using that color
                self.hgr_last_plot_color = self.hgr_color
                if artifact_active:
                    self._plot_artifact_pixel(x1, y1, self.hgr_color)
                    self._draw_line_artifact(x1, y1, x2, y2, self.hgr_color)
                else:
                    if self.graphics_mode in ['HGR', 'HGR2'] and PYGAME_AVAILABLE and self.hgr_surface:
                        color = self.HGR_COLORS[self.hgr_color]
                        # Draw line by filling each pixel individually
                        if x1 == x2:
                            # Vertical line
                            for y in range(min(y1, y2), max(y1, y2) + 1):
                                rect = pygame.Rect(x1 * 2, y * 2, 2, 2)
                                self.hgr_surface.fill(color, rect)
                        elif y1 == y2:
                            # Horizontal line
                            for x in range(min(x1, x2), max(x1, x2) + 1):
                                rect = pygame.Rect(x * 2, y1 * 2, 2, 2)
                                self.hgr_surface.fill(color, rect)
                        else:
                            # Diagonal - use Bresenham
                            self._draw_line_bresenham(x1, y1, x2, y2, color)
                self.hgr_x = x2
                self.hgr_y = y2
            else:
                # Just plot a point - this sets the color for future HPLOT TO commands
                parts = [p.strip() for p in args.split(',')]
                x = int(self.evaluate(parts[0]))
                y = int(self.evaluate(parts[1]))
                
                # Remember this color for future HPLOT TO commands
                self.hgr_last_plot_color = self.hgr_color
                
                if artifact_active:
                    self._plot_artifact_pixel(x, y, self.hgr_color)
                elif self.graphics_mode in ['HGR', 'HGR2'] and PYGAME_AVAILABLE and self.hgr_surface:
                    color = self.HGR_COLORS[self.hgr_color]
                    pygame.draw.circle(self.hgr_surface, color, (x * 2, y * 2), 2)
                self.hgr_x = x
                self.hgr_y = y
                
    def cmd_htab(self, args: str):
        """HTAB command - set horizontal cursor position"""
        x = int(self.evaluate(args))
        self.text_x = x - 1  # BASIC uses 1-based
        
    def cmd_vtab(self, args: str):
        """VTAB command - set vertical cursor position"""
        y = int(self.evaluate(args))
        self.text_y = y - 1  # BASIC uses 1-based
        
    def cmd_inverse(self, args: str):
        """INVERSE command - enable inverse video"""
        self.inverse = True
        
    def cmd_normal(self, args: str):
        """NORMAL command - disable inverse video"""
        self.inverse = False
        
    def cmd_poke(self, args: str):
        """POKE command - handle key softswitches for graphics/mixed mode and page selection"""
        # Parse: POKE addr, value
        parts = [p.strip() for p in args.split(',')]
        if len(parts) < 2:
            raise ApplesoftError("Syntax error in POKE")
        addr = int(self.evaluate(parts[0]))
        val = int(self.evaluate(parts[1]))
        # Map negative addresses to unsigned (Apple II two's complement addressing)
        if addr < 0:
            addr = (addr + 65536) % 65536
        # Recognize softswitches described by user
        # 49234 ($C052) and -16302: full-page graphics, no text (disable mixed)
        if addr == 49234:
            self.hgr_mixed = False
            return
        # 49235 ($C053) and -16301: mixed mode text on (enable mixed)
        if addr == 49235 or addr == ((-16301 + 65536) % 65536):
            self.hgr_mixed = True
            return
        # -16299 ($C055): select HGR page 2
        if addr == 49237:
            self.hgr_page = 2
            # Switch current drawing surface
            if PYGAME_AVAILABLE:
                if not self.hgr_page2_surface:
                    self.hgr_page2_surface = pygame.Surface((560, 384))
                    self.hgr_page2_surface.fill((0, 0, 0))
                self.hgr_surface = self.hgr_page2_surface
            self._set_active_hgr_memory(2)
            if self.artifact_mode and PYGAME_AVAILABLE and self.hgr_surface:
                self._render_full_hgr_page()
            return
        # -16300 ($C054): select HGR page 1
        if addr == 49236:
            self.hgr_page = 1
            if PYGAME_AVAILABLE:
                if not self.hgr_page1_surface:
                    self.hgr_page1_surface = pygame.Surface((560, 384))
                    self.hgr_page1_surface.fill((0, 0, 0))
                self.hgr_surface = self.hgr_page1_surface
            self._set_active_hgr_memory(1)
            if self.artifact_mode and PYGAME_AVAILABLE and self.hgr_surface:
                self._render_full_hgr_page()
            return
        # -16302 ($C052): also full screen graphics - no text
        if addr == ((-16302 + 65536) % 65536):
            self.hgr_mixed = False
            return
        # Other POKEs are ignored
        return

    def cmd_call(self, args: str):
        """CALL command - handle selected monitor subroutines used in examples"""
        # For now, implement CALL 62454: fill current HGR page with last HCOLOR
        addr = int(self.evaluate(args.strip()))
        if addr == 62454 and PYGAME_AVAILABLE and self.hgr_surface:
            if self.artifact_mode:
                # Fill backing memory using current palette bit then repaint
                self._ensure_hgr_memory()
                memory = self._get_active_hgr_memory()
                whites = self._get_active_white_map()
                colors = self._get_active_color_map()
                hi_flag = 1 if self.hgr_color >= 4 else 0
                set_on = self.hgr_color not in (0, 4)
                force_white = self.hgr_color in (3, 7)
                fill_byte = (0x80 if hi_flag else 0) | (0x7F if set_on else 0)
                for y in range(self.HGR_HEIGHT):
                    memory[y] = [fill_byte] * 40
                    if force_white and set_on:
                        whites[y] = [True] * self.HGR_WIDTH
                    else:
                        whites[y] = [False] * self.HGR_WIDTH
                    colors[y] = [self.hgr_color if set_on else -1] * self.HGR_WIDTH
                self._render_full_hgr_page()
            else:
                color = self.HGR_COLORS[self.hgr_color]
                self.hgr_surface.fill(color)
        elif addr == 65000 and PYGAME_AVAILABLE and self.screen:
            # Save a screenshot and evaluate mixed overlay presence
            try:
                self.save_screenshot('call65000')
            except Exception as e:
                print(f"Screenshot error: {e}")
        # Otherwise no-op
        return

    def save_screenshot(self, label: str = 'frame'):
        """Save the current pygame window to screenshots/ with timestamp and print a brief evaluation."""
        if not PYGAME_AVAILABLE or not self.screen:
            return
        # Ensure latest frame is drawn
        self.update_display()
        # Prepare directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(script_dir, 'screenshots')
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        path = os.path.join(out_dir, f'{label}_{ts}.png')
        pygame.image.save(self.screen, path)
        # Evaluate presence of mixed text overlay (bottom 4 rows): sample non-black pixels
        non_black = 0
        samples = 0
        for y in range(320, 384, 4):
            for x in range(0, 560, 4):
                c = self.screen.get_at((x, y))
                if (c.r + c.g + c.b) > 5:
                    non_black += 1
                samples += 1
        ratio = non_black / max(samples, 1)
        overlay = ratio > 0.01  # heuristic
        mode_desc = f"mode={self.graphics_mode}, page={self.hgr_page}, mixed={'on' if self.hgr_mixed else 'off'}"
        print(f"Saved screenshot: {path} ({mode_desc}); bottom overlay visible={overlay:.3f}")
        
    def cmd_def(self, args: str):
        """DEF command - define a function"""
        # DEF FN name(param) = expression
        match = re.match(r'FN\s*(\w+)\s*\((\w+)\)\s*=\s*(.+)', args, re.IGNORECASE)
        if not match:
            raise ApplesoftError("Syntax error in DEF")
            
        raw_name = match.group(1).upper()
        # Applesoft requires FN names to be a single letter (optionally followed by a digit)
        if not re.match(r'^[A-Z][0-9]?$', raw_name):
            raise ApplesoftError("Syntax error: DEF FN name must be single letter (optional digit)")
        name = 'FN' + raw_name
        param = match.group(2).upper()
        expr = match.group(3)
        
        self.user_functions[name] = (param, expr)
        
    def cmd_onerr(self, args: str):
        """ONERR command - set error handler"""
        # ONERR GOTO line
        if args.upper().startswith('GOTO '):
            line = int(args[5:].strip())
            self.error_handler_line = line
            
    def cmd_resume(self):
        """RESUME command - resume after error"""
        if self.last_error:
            self.last_error = None
            # Continue from current line
        else:
            raise ApplesoftError("Can't resume")
            
    def cmd_on(self, args: str):
        """ON command - computed GOTO/GOSUB"""
        # ON expr GOTO line1,line2,... or ON expr GOSUB line1,line2,...
        match = re.match(r'(.+?)\s+(GOTO|GOSUB)\s+(.+)', args, re.IGNORECASE)
        if not match:
            raise ApplesoftError("Syntax error in ON")
            
        expr = match.group(1)
        cmd = match.group(2).upper()
        lines_str = match.group(3)
        
        value = int(self.evaluate(expr))
        lines = [int(l.strip()) for l in lines_str.split(',')]
        
        if 1 <= value <= len(lines):
            line = lines[value - 1]
            if cmd == 'GOTO':
                self.cmd_goto(str(line))
            else:
                self.cmd_gosub(str(line))
                
    def cmd_wait(self, args: str):
        """WAIT command - wait for memory condition"""
        # Not fully implemented - just add a small delay
        time.sleep(0.1)
        
    def evaluate(self, expr: str) -> Union[float, str]:
        """Evaluate an expression"""
        expr = expr.strip()
        
        if not expr:
            return 0
            
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
            
        # Variable
        if re.match(r'^[A-Za-z]\w*\$?$', expr):
            var_name = expr.upper()
            if var_name in self.variables:
                return self.variables[var_name]
            else:
                # Uninitialized variables are 0 or ""
                if var_name.endswith('$'):
                    return ""
                else:
                    return 0
                    
        # Array element or function call - only if there's a valid identifier immediately before (
        if '(' in expr and ')' in expr and not expr.startswith('('):
            paren_pos = expr.index('(')
            name_part = expr[:paren_pos]
            
            # Check if name_part is a valid identifier (not an expression like "140 + 100 * COS")
            # Must be letters, digits, underscore, $ (and optionally "FN " prefix)
            if re.match(r'^(FN\s+)?[A-Za-z_]\w*\$?$', name_part.strip()):
                # Check if it's a function call - strip spaces from name_part to handle "RND (1)"
                name_upper = name_part.strip().upper()
                # Normalize FN names to ignore spaces after FN
                if name_upper.startswith('FN '):
                    name_upper = 'FN' + name_upper[3:]
                if name_upper in ['INT', 'ABS', 'SGN', 'SQR', 'SIN', 'COS', 'TAN', 
                                 'ATN', 'LOG', 'EXP', 'RND',
                                 'PEEK', 'PDL', 'SCRN', 'POS', 'FRE']:
                    # Find the matching closing paren for this function
                    depth = 0
                    closing_paren_pos = -1
                    for i in range(paren_pos, len(expr)):
                        if expr[i] == '(':
                            depth += 1
                        elif expr[i] == ')':
                            depth -= 1
                            if depth == 0:
                                closing_paren_pos = i
                                break
                    
                    # Only treat as function call if the closing paren is at the end
                    # Otherwise it's something like RND(1)*279 which needs to be parsed as multiplication
                    if closing_paren_pos > 0 and closing_paren_pos == len(expr) - 1:
                        return self.evaluate_function(expr)
                elif name_upper in ['LEN', 'VAL', 'ASC']:
                    # These can work with strings
                    return self.evaluate_string_or_numeric_function(expr)
                elif name_upper.startswith('FN'):
                    return self.evaluate_user_function(expr)
                elif '$' in name_upper and name_upper.replace('$', '') in ['STR', 'CHR', 'LEFT', 'RIGHT', 'MID']:
                    return self.evaluate_string_function(expr)
                else:
                    # Array access - find the matching closing paren
                    depth = 0
                    closing_paren_pos = -1
                    for i in range(paren_pos, len(expr)):
                        if expr[i] == '(':
                            depth += 1
                        elif expr[i] == ')':
                            depth -= 1
                            if depth == 0:
                                closing_paren_pos = i
                                break
                    
                    # Only treat as array access if the closing paren is at the end (possibly with whitespace)
                    if closing_paren_pos > 0 and closing_paren_pos == len(expr) - 1:
                        var_name = name_part.upper()
                        indices_str = expr[paren_pos + 1:closing_paren_pos]
                        indices = [int(self.evaluate(idx.strip())) for idx in indices_str.split(',')]
                        
                        # Auto-create array with default dimension if not already dimensioned
                        # In Applesoft BASIC, arrays default to 0-10 (11 elements) if not explicitly dimensioned
                        if var_name not in self.arrays:
                            if len(indices) == 1:
                                self.arrays[var_name] = [0] * 11
                            elif len(indices) == 2:
                                self.arrays[var_name] = [[0] * 11 for _ in range(11)]
                            
                        arr = self.arrays[var_name]
                        if len(indices) == 1:
                            return arr[indices[0]]
                        elif len(indices) == 2:
                            return arr[indices[0]][indices[1]]
                    
        # Try to evaluate as arithmetic expression
        return self.evaluate_arithmetic(expr)
        
    def evaluate_arithmetic(self, expr: str) -> float:
        """Evaluate an arithmetic expression"""
        # Normalize comparison operators by removing ALL spaces (e.g., ">  =" or "> =" becomes ">=")
        # Use regex to replace operators with any amount of whitespace
        import re
        expr = re.sub(r'<\s*>', '<>', expr)
        expr = re.sub(r'>\s*=', '>=', expr)
        expr = re.sub(r'<\s*=', '<=', expr)
        
        # Handle operators in order of precedence
        
        # First, handle OR
        if ' OR ' in expr.upper():
            parts = re.split(r'\s+OR\s+', expr, flags=re.IGNORECASE)
            result = 0
            for part in parts:
                val = self.evaluate_arithmetic(part)
                result = result or val
            return float(result != 0)
            
        # Handle AND
        if ' AND ' in expr.upper():
            parts = re.split(r'\s+AND\s+', expr, flags=re.IGNORECASE)
            result = 1
            for part in parts:
                val = self.evaluate_arithmetic(part)
                result = result and val
            return float(result != 0)
            
        # Handle comparisons
        for op in ['<=', '>=', '<>', '=', '<', '>']:
            if op in expr:
                # Find the operator not inside parentheses
                depth = 0
                for i, char in enumerate(expr):
                    if char == '(':
                        depth += 1
                    elif char == ')':
                        depth -= 1
                    elif depth == 0 and expr[i:i+len(op)] == op:
                        left = expr[:i].strip()
                        right = expr[i+len(op):].strip()
                        left_val = self.evaluate(left)
                        right_val = self.evaluate(right)
                        
                        if op == '=':
                            return float(left_val == right_val)
                        elif op == '<>':
                            return float(left_val != right_val)
                        elif op == '<':
                            return float(left_val < right_val)
                        elif op == '>':
                            return float(left_val > right_val)
                        elif op == '<=':
                            return float(left_val <= right_val)
                        elif op == '>=':
                            return float(left_val >= right_val)
                        break
                        
        # Handle addition and subtraction
        # Need to be careful with negative numbers
        depth = 0
        for i in range(len(expr) - 1, -1, -1):
            char = expr[i]
            if char == ')':
                depth += 1
            elif char == '(':
                depth -= 1
            elif depth == 0 and char == '+':
                left = expr[:i].strip()
                right = expr[i+1:].strip()
                if left:  # Not a unary plus
                    left_val = self.evaluate(left)
                    right_val = self.evaluate(right)
                    return float(left_val) + float(right_val)
            elif depth == 0 and char == '-':
                left = expr[:i].strip()
                right = expr[i+1:].strip()
                if left:  # Not a unary minus
                    left_val = self.evaluate(left)
                    right_val = self.evaluate(right)
                    return float(left_val) - float(right_val)
                    
        # Handle multiplication and division
        depth = 0
        for i in range(len(expr) - 1, -1, -1):
            char = expr[i]
            if char == ')':
                depth += 1
            elif char == '(':
                depth -= 1
            elif depth == 0 and char == '*':
                left = expr[:i].strip()
                right = expr[i+1:].strip()
                left_val = self.evaluate(left)
                right_val = self.evaluate(right)
                return float(left_val) * float(right_val)
            elif depth == 0 and char == '/':
                left = expr[:i].strip()
                right = expr[i+1:].strip()
                left_val = self.evaluate(left)
                right_val = self.evaluate(right)
                divisor = float(right_val)
                if divisor == 0:
                    raise ApplesoftError("Division by zero")
                return float(left_val) / divisor
                
        # Handle exponentiation
        if '^' in expr:
            depth = 0
            for i in range(len(expr) - 1, -1, -1):
                char = expr[i]
                if char == ')':
                    depth += 1
                elif char == '(':
                    depth -= 1
                elif depth == 0 and char == '^':
                    left = expr[:i].strip()
                    right = expr[i+1:].strip()
                    left_val = self.evaluate(left)
                    right_val = self.evaluate(right)
                    return float(left_val) ** float(right_val)
                    
        # Handle NOT
        if expr.upper().startswith('NOT '):
            val = self.evaluate(expr[4:])
            return float(not val)
            
        # Handle unary minus
        if expr.startswith('-'):
            val = self.evaluate(expr[1:])
            return -float(val)
            
        # Handle parentheses
        if expr.startswith('(') and expr.endswith(')'):
            return self.evaluate_arithmetic(expr[1:-1])
            
        # Try as number
        try:
            return float(expr)
        except ValueError:
            pass
            
        # Base case - must be variable, function, or array
        var_name = expr.upper()
        
        # Variable lookup
        if var_name in self.variables:
            val = self.variables[var_name]
            if isinstance(val, str):
                raise ApplesoftError("Type mismatch")
            return val
        else:
            # Uninitialized numeric variable
            return 0.0
        
    def evaluate_function(self, expr: str) -> float:
        """Evaluate a built-in function"""
        paren_pos = expr.index('(')
        func_name = expr[:paren_pos].strip().upper()
        args_str = expr[paren_pos + 1:expr.rindex(')')]
        
        if func_name == 'INT':
            return float(int(self.evaluate(args_str)))
        elif func_name == 'ABS':
            return abs(self.evaluate(args_str))
        elif func_name == 'SGN':
            val = self.evaluate(args_str)
            return float(1 if val > 0 else (-1 if val < 0 else 0))
        elif func_name == 'SQR':
            return math.sqrt(self.evaluate(args_str))
        elif func_name == 'SIN':
            return math.sin(self.evaluate(args_str))
        elif func_name == 'COS':
            return math.cos(self.evaluate(args_str))
        elif func_name == 'TAN':
            return math.tan(self.evaluate(args_str))
        elif func_name == 'ATN':
            return math.atan(self.evaluate(args_str))
        elif func_name == 'LOG':
            return math.log(self.evaluate(args_str))
        elif func_name == 'EXP':
            return math.exp(self.evaluate(args_str))
        elif func_name == 'RND':
            arg = self.evaluate(args_str)
            if arg < 0:
                random.seed(int(arg))
            return random.random()
        elif func_name == 'PEEK':
            # Return 0 for PEEK
            return 0
        elif func_name == 'PDL':
            # Return 0 for paddle
            return 0
        elif func_name == 'POS':
            return float(self.text_x)
        elif func_name == 'FRE':
            # Return a fake free memory value
            return 30000
        elif func_name == 'SCRN':
            # SCRN(x,y) - return color at position
            args = [a.strip() for a in args_str.split(',')]
            x = int(self.evaluate(args[0]))
            y = int(self.evaluate(args[1]))
            # Return 0 for now
            return 0
        else:
            raise ApplesoftError(f"Unknown function: {func_name}")
            
    def evaluate_string_or_numeric_function(self, expr: str) -> Union[float, str]:
        """Evaluate functions that can work with both strings and numbers (LEN, VAL, ASC)"""
        paren_pos = expr.index('(')
        func_name = expr[:paren_pos].upper()
        args_str = expr[paren_pos + 1:expr.rindex(')')]
        
        if func_name == 'LEN':
            val = self.evaluate(args_str)
            return float(len(str(val)))
        elif func_name == 'VAL':
            s = str(self.evaluate(args_str))
            try:
                return float(s)
            except ValueError:
                return 0.0
        elif func_name == 'ASC':
            s = str(self.evaluate(args_str))
            return float(ord(s[0])) if s else 0.0
        else:
            raise ApplesoftError(f"Unknown function: {func_name}")
            
    def evaluate_string_function(self, expr: str) -> str:
        """Evaluate a string function"""
        paren_pos = expr.index('(')
        func_name = expr[:paren_pos].upper()
        args_str = expr[paren_pos + 1:expr.rindex(')')]
        
        if func_name == 'CHR$':
            code = int(self.evaluate(args_str))
            return chr(code)
        elif func_name == 'STR$':
            val = self.evaluate(args_str)
            return self.format_number(val)
        elif func_name == 'LEFT$':
            args = [a.strip() for a in args_str.split(',')]
            s = str(self.evaluate(args[0]))
            n = int(self.evaluate(args[1]))
            return s[:n]
        elif func_name == 'RIGHT$':
            args = [a.strip() for a in args_str.split(',')]
            s = str(self.evaluate(args[0]))
            n = int(self.evaluate(args[1]))
            return s[-n:] if n > 0 else ''
        elif func_name == 'MID$':
            args = [a.strip() for a in args_str.split(',')]
            s = str(self.evaluate(args[0]))
            start = int(self.evaluate(args[1])) - 1  # BASIC is 1-based
            if len(args) > 2:
                length = int(self.evaluate(args[2]))
                return s[start:start + length]
            else:
                return s[start:]
        else:
            raise ApplesoftError(f"Unknown function: {func_name}")
            
    def evaluate_user_function(self, expr: str) -> float:
        """Evaluate a user-defined function"""
        paren_pos = expr.index('(')
        func_name = expr[:paren_pos].upper()
        if func_name.startswith('FN '):
            func_name = 'FN' + func_name[3:]
        arg_str = expr[paren_pos + 1:expr.rindex(')')]
        
        if func_name not in self.user_functions:
            raise ApplesoftError(f"Undefined function: {func_name}")
            
        param, func_expr = self.user_functions[func_name]
        arg_val = self.evaluate(arg_str)
        
        # Save old parameter value
        old_val = self.variables.get(param)
        
        # Set parameter
        self.variables[param] = arg_val
        
        # Evaluate function
        result = self.evaluate(func_expr)
        
        # Restore parameter
        if old_val is not None:
            self.variables[param] = old_val
        else:
            del self.variables[param]
            
        return result
        
    def update_display(self):
        """Update the pygame display"""
        if not PYGAME_AVAILABLE or not self.screen:
            return
            
        if self.graphics_mode == 'TEXT':
            self.screen.blit(self.text_surface, (0, 0))
        elif self.graphics_mode == 'GR' and self.gr_surface:
            self.screen.blit(self.gr_surface, (0, 0))
        elif self.graphics_mode in ['HGR', 'HGR2'] and self.hgr_surface:
            # Optionally apply a simple horizontal composite blur to reduce zebra artifacts
            if self.composite_blur:
                try:
                    # Use array3d to avoid locking the surface during blit
                    arr = pygame.surfarray.array3d(self.hgr_surface)
                    # Create a blurred copy: arr_blur[x] = (arr[x-1]+2*arr[x]+arr[x+1])//4
                    arr_blur = arr.copy()
                    # Average horizontally; skip first/last column to avoid bounds checks
                    arr_blur[1:-1, :, :] = (
                        arr[0:-2, :, :] + 2 * arr[1:-1, :, :] + arr[2:, :, :]
                    ) // 4
                    # Replace surface with blurred data
                    pygame.surfarray.blit_array(self.hgr_surface, arr_blur)
                except Exception:
                    # If surfarray fails, fall back to unblurred blit
                    pass
            # Blit graphics first
            self.screen.blit(self.hgr_surface, (0, 0))
            # Then composite text over bottom 4 lines (mixed mode)
            if self.text_surface and self.hgr_mixed:
                # Only blit the bottom 4 text rows (rows 20-23, pixels 320-383)
                text_rect = pygame.Rect(0, 320, 560, 64)  # 4 rows * 16 pixels
                self.screen.blit(self.text_surface, (0, 320), text_rect)
            
        pygame.display.flip()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Applesoft BASIC Interpreter')
    parser.add_argument('filename', nargs='?', help='BASIC program file to load')
    parser.add_argument('--input-timeout', type=float, default=30.0,
                       help='Input timeout in seconds (default: 30)')
    parser.add_argument('--exec-timeout', type=float, default=None,
                       help='Execution timeout in seconds (default: none)')
    parser.add_argument('--no-keep-open', action='store_true',
                       help='Close window immediately after program ends (useful for debugging)')
    parser.add_argument('--autosnap-every', type=int, default=None,
                       help='Automatically save a screenshot every N statements')
    parser.add_argument('--autosnap-on-end', action='store_true',
                       help='Automatically save a screenshot when program ends')
    parser.add_argument('--no-artifact', dest='artifact_mode', action='store_false',
                       help='Disable NTSC artifact color simulation (use direct RGB colors)')
    parser.set_defaults(artifact_mode=False)
    parser.add_argument('--composite-blur', dest='composite_blur', action='store_true',
                       help='Apply horizontal composite blur effect (ghostly afterglow)')
    parser.set_defaults(composite_blur=False)
    parser.add_argument('--delay', type=float, default=0.001,
                       help='Statement execution delay in seconds to simulate Apple II speed (default: 0.001)')
    
    args = parser.parse_args()
    
    interp = ApplesoftInterpreter(
        input_timeout=args.input_timeout,
        execution_timeout=args.exec_timeout,
        keep_window_open=not args.no_keep_open,
        autosnap_every=args.autosnap_every,
        autosnap_on_end=args.autosnap_on_end,
        artifact_mode=args.artifact_mode,
        composite_blur=args.composite_blur,
        statement_delay=args.delay
    )
    
    if args.filename:
        # Load and run program
        try:
            interp.load_program(args.filename)
            interp.run()
        except FileNotFoundError:
            print(f"Error: File not found: {args.filename}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nInterrupted")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        # Interactive mode
        print("Applesoft BASIC Interpreter")
        print("Type NEW to start, LIST to view program, RUN to execute")
        print()
        
        while True:
            try:
                line = input('] ')
                if line.upper() == 'EXIT' or line.upper() == 'QUIT':
                    break
                interp.parse_line(line)
            except KeyboardInterrupt:
                print("\nUse EXIT to quit")
            except Exception as e:
                print(f"Error: {e}")


if __name__ == '__main__':
    main()
