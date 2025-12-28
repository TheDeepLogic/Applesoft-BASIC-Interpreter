REM PRINT LOOP DEMO
REM Demonstrates output with loops at different scales

10 PRINT "PRINT LOOP DEMO"
20 PRINT ""
30 PRINT "Small loop (100 iterations):"
40 PRINT ""; : GOSUB 200
50 PRINT ""
60 PRINT ""
70 PRINT "Large loop (30000 iterations):"
80 PRINT ""; : GOSUB 300
90 PRINT ""
100 PRINT ""
110 PRINT "Done!"
120 END

REM Small loop - 100 iterations
200 FOR D = 1 TO 100
210 PRINT "X";
220 NEXT D
230 RETURN

REM Large loop - 30000 iterations with minimal output
300 FOR D = 1 TO 30000
310 PRINT ".";
320 NEXT D
330 RETURN
