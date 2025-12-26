REM FOR LOOP PERFORMANCE TEST
REM Demonstrates tight loop optimization at different scales

10 PRINT "FOR LOOP PERFORMANCE TEST"
20 PRINT ""
30 PRINT "Testing: Small loop (10 iterations)"
40 GOSUB 1000
50 PRINT ""
60 PRINT "Testing: Medium loop (3750 iterations)"
70 GOSUB 2000
80 PRINT ""
90 PRINT "Testing: Large loop (30000 iterations)"
100 GOSUB 3000
110 PRINT ""
120 PRINT "All tests completed!"
130 END

REM Small loop test
1000 FOR I = 1 TO 10
1010 NEXT I
1020 PRINT "  10 iterations done"
1030 RETURN

REM Medium loop test (target: ~5 seconds on Apple II)
2000 FOR I = 1 TO 3750
2010 NEXT I
2020 PRINT "  3750 iterations done"
2030 RETURN

REM Large loop test (target: ~40 seconds on Apple II)
3000 FOR I = 1 TO 30000
3010 NEXT I
3020 PRINT "  30000 iterations done"
3030 RETURN
