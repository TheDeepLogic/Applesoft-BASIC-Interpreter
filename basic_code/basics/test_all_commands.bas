10 REM Test all Applesoft BASIC commands
20 PRINT "Testing All Commands"
30 PRINT
40 REM Test TRACE/NOTRACE
50 TRACE
60 PRINT "TRACE is on"
70 NOTRACE
80 PRINT "TRACE is off"
90 PRINT
100 REM Test logical operators
110 PRINT "Testing logical operators:"
120 PRINT "5 > 3 AND 2 < 4: "; 5 > 3 AND 2 < 4
130 PRINT "1 OR 0: "; 1 OR 0
140 PRINT "NOT 0: "; NOT 0
150 PRINT "NOT 1: "; NOT 1
160 PRINT
170 REM Test string concatenation
180 PRINT "Testing string ops:"
190 A$ = "Hello"
200 B$ = " World"
210 C$ = A$ + B$
220 PRINT C$
230 PRINT "Length: "; LEN(C$)
240 PRINT "First 5: "; LEFT$(C$, 5)
250 PRINT
260 REM Test math functions
270 PRINT "Testing math functions:"
280 PRINT "SQR(16) = "; SQR(16)
290 PRINT "ABS(-42) = "; ABS(-42)
300 PRINT "INT(3.7) = "; INT(3.7)
310 PRINT "SGN(-5) = "; SGN(-5)
320 PRINT "SIN(0) = "; SIN(0)
330 PRINT
340 REM Test arrays
350 DIM A(5)
360 FOR I = 0 TO 5
370 A(I) = I * 10
380 NEXT I
390 PRINT "Array test: A(3) = "; A(3)
400 PRINT
410 REM Test FOR loop
420 PRINT "FOR loop (1 to 3):"
430 FOR I = 1 TO 3
440 PRINT "  Value: "; I
450 NEXT I
460 PRINT
470 REM Test IF/THEN
480 X = 5
490 IF X > 3 THEN PRINT "X is greater than 3"
500 IF X < 3 THEN PRINT "X is less than 3" : GOTO 520
510 PRINT "X is not less than 3"
520 PRINT
530 REM Test INPUT
540 PRINT "Input test skipped (would wait for user)"
550 PRINT
560 REM Test memory functions
570 PRINT "Testing memory:"
580 PRINT "FRE = "; FRE(0)
590 POKE 100, 42
600 PRINT "PEEK(100) = "; PEEK(100)
610 PRINT
620 REM Test CALL
630 PRINT "CALL test (HOME):"
640 CALL -938
650 PRINT "HOME called"
660 PRINT
670 REM Test ON/GOTO
680 PRINT "Testing ON/GOTO:"
690 N = 2
700 ON N GOTO 710, 720, 730
710 PRINT "Branch 1" : GOTO 740
720 PRINT "Branch 2" : GOTO 740
730 PRINT "Branch 3"
740 PRINT
750 REM Test RND
760 PRINT "Random number: "; RND(1)
770 PRINT
780 PRINT "All tests completed!"
790 END
