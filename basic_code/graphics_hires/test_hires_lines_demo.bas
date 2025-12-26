REM HI-RES LINE DRAWING DEMO
REM Demonstrates horizontal, vertical, and diagonal lines with various techniques

10 PRINT "HI-RES LINE DRAWING"
20 PRINT ""
30 HGR
40 PRINT "Drawing lines..."
50 GOSUB 100
60 PRINT "Done!"
70 FOR D = 1 TO 20000000: NEXT D
80 END

REM Draw various line styles and techniques
100 REM Horizontal line test
110 HCOLOR = 3
120 HPLOT 0,96 TO 279,96
130 PRINT "  Horizontal line at Y=96"
140 
REM Vertical line test
150 HCOLOR = 1
160 HPLOT 140,0 TO 140,191
170 PRINT "  Vertical line at X=140"
180 
REM Diagonal circle using math
190 HCOLOR = 2
200 HPLOT 140,96
210 FOR A = 0 TO 6.28 STEP 0.1
220 X = 140 + 100 * COS(A)
230 Y = 96 + 80 * SIN(A)
240 HPLOT TO X,Y
250 NEXT A
260 PRINT "  Ellipse drawn with trigonometry"
270 
REM Cross pattern
280 HCOLOR = 5
290 FOR I = 0 TO 191
300 HPLOT 140,I
310 NEXT I
320 FOR I = 0 TO 279
330 HPLOT I,96
340 NEXT I
350 PRINT "  Cross pattern"
360 
370 RETURN
