REM LOW-RES ANIMATION DEMO
REM Simple moving point animation

10 GR
20 PRINT "MOVING POINT ANIMATION"
30 PRINT "Watch the point move..."
40 PRINT ""
50 
REM Animation loop
60 FOR FRAME = 0 TO 2
70 GOSUB 100
80 NEXT FRAME
90 PRINT "Animation complete!"
100 END

REM Animation subroutine - moving point
100 FOR I = 0 TO 30
110 COLOR = I MOD 7
120 X = (I * 8) MOD 40
130 Y = 5 + (I MOD 10)
140 PLOT X,Y
150 NEXT I
160 RETURN
