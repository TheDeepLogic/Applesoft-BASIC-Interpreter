REM HI-RES GRAPHICS BASICS
REM Demonstrates HPLOT and HGR commands with coordinate system

10 PRINT "HI-RES GRAPHICS BASICS"
20 PRINT ""
30 PRINT "Initializing 280x192 display..."
40 HGR
50 PRINT ""
60 GOSUB 100
70 PRINT ""
80 PRINT "Display ready. Pause to view..."
90 FOR D = 1 TO 20000000: NEXT D
100 END

REM Draw basic points and reference system
100 PRINT "Drawing coordinate reference..."
110 HCOLOR = 3
120 REM Draw points at different Y coordinates
130 HPLOT 10,10
140 PRINT "  Point at (10,10)"
150 HPLOT 10,50
160 PRINT "  Point at (10,50)"
170 HPLOT 10,100
180 PRINT "  Point at (10,100)"
190 HPLOT 10,150
200 PRINT "  Point at (10,150)"
210 
220 HCOLOR = 1
230 REM Draw a simple line
240 HPLOT 100,100 TO 200,100
250 PRINT "  Horizontal line at Y=100"
260 
270 HCOLOR = 2
280 REM Draw vertical reference
290 HPLOT 50,0 TO 50,191
300 PRINT "  Vertical line at X=50"
310 
320 PRINT ""
330 PRINT "Coordinates drawn:"
340 PRINT "  X: 0-279 (left-right)"
350 PRINT "  Y: 0-191 (top-bottom)"
360 RETURN
