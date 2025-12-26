REM AUDIO BASICS - SOUND AND SPEAKER CONTROL
REM Demonstrates direct speaker access (POKE) and SOUND command

10 PRINT "APPLE II AUDIO BASICS"
20 PRINT ""
30 PRINT "1. Direct speaker control (POKE)"
40 GOSUB 100
50 PRINT ""
60 PRINT "2. SOUND command - tone sequence"
70 GOSUB 200
80 PRINT ""
90 PRINT "All demos complete!"
100 END

REM Direct speaker poke method
100 PRINT "  Creating clicks with direct speaker access..."
110 FOR I = 1 TO 5
120 FOR D = 1 TO 300
130 POKE -16336,0
140 NEXT D
150 PRINT "  Click " ; I
160 NEXT I
170 PRINT "  Done!"
180 RETURN

REM SOUND command demo
200 PRINT "  Playing tone sequence with SOUND..."
210 C4=262:D4=294:E4=330:F4=349:G4=392
220 DUR=250
230 SOUND C4,DUR
240 SOUND D4,DUR
250 SOUND E4,DUR
260 SOUND F4,DUR
270 SOUND G4,DUR*2
280 PRINT "  Tone sequence complete!"
290 RETURN
