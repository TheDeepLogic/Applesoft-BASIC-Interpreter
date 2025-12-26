10 REM Test advanced features
20 PRINT "Applesoft Advanced Features Test"
30 PRINT
40 REM Test string operations  
50 A$ = "Apple"
60 B$ = " II"
70 C$ = A$ + B$
80 PRINT "String concat: "; C$
90 PRINT "Length: "; LEN(C$)
100 PRINT
110 REM Test HIMEM/LOMEM (memory management)
120 HIMEM: 40000
130 LOMEM: 2048
140 PRINT "Memory configured"
150 PRINT
160 REM Test user functions
170 DEF FN F(X) = X * X + 2 * X + 1
180 PRINT "FN F(5) = "; FN F(5)
190 PRINT
200 REM Test ON GOSUB
210 N = 2
220 ON N GOSUB 250, 260, 270
230 PRINT "Back from GOSUB"
240 GOTO 280
250 PRINT "GOSUB 1"
260 RETURN
260 PRINT "GOSUB 2"
270 RETURN
270 PRINT "GOSUB 3"
280 PRINT
290 REM Test complex expressions
300 X = 10
310 IF X > 5 AND X < 15 THEN PRINT "X is between 5 and 15"
320 IF NOT (X < 0) THEN PRINT "X is not negative"
330 PRINT
340 PRINT "Advanced tests completed!"
350 END
