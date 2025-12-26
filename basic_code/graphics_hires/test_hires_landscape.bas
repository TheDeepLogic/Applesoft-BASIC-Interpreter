REM HI-RES LANDSCAPE DEMO
REM Demonstrates drawing a simple ground and sky scene

10 PRINT "HI-RES LANDSCAPE"
20 PRINT ""
30 HGR
40 PRINT "Initializing display..."
50 GOSUB 900
60 GOSUB 700
70 GOSUB 600
80 PRINT ""
90 PRINT "Landscape displayed. Pause to view..."
100 FOR D = 1 TO 20000000: NEXT D
110 END

REM SKY - Fill top portion with color
700 PRINT "Drawing sky..."
710 HCOLOR = 6
720 HPLOT 0,0
730 FOR Y = 0 TO 90
740 HPLOT 0,Y TO 279,Y
750 NEXT Y
760 RETURN

REM GROUND - Draw multiple horizontal lines
600 PRINT "Drawing ground..."
610 HCOLOR = 1
620 FOR I = 0 TO 9
630 HPLOT 0, 181 + 1 + I TO 279, 181 + 1 + I
640 NEXT I
650 PRINT "  Ground: lines 182-191"
660 RETURN

REM INITIALIZE GRAPHICS
900 PRINT "Setting up 280x192 display..."
910 HGR
920 RETURN
