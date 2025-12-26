REM PRINT LOOP DEMO
REM Demonstrates output with loops at different scales

10 PRINT "PRINT LOOP DEMO"
20 PRINT ""
30 PRINT "Small loop (100 iterations):"
40 PRINT ""; : GOSUB 100
50 PRINT ""
60 PRINT ""
70 PRINT "Large loop (30000 iterations):"
80 PRINT ""; : GOSUB 200
90 PRINT ""
100 PRINT ""
110 PRINT "Done!"
120 END

REM Small loop - 100 iterations
100 FOR D = 1 TO 100
110 PRINT "X";
120 NEXT D
130 RETURN

REM Large loop - 30000 iterations with minimal output
200 FOR D = 1 TO 30000
210 PRINT ".";
220 NEXT D
230 RETURN
