10 REM Apple IIe Official Manual - POKE/PEEK/CALL Tests
20 HOME
30 PRINT "OFFICIAL MANUAL TESTS"
40 PRINT "===================="
50 PRINT ""

100 REM Test 1: Keyboard address
110 PRINT "TEST 1: KEYBOARD ADDRESS"
120 REM PEEK(-16384) for keyboard input
130 X = PEEK(-16384)
140 PRINT "PEEK(-16384)="; X; " (keyboard, should be 0)"
150 PRINT ""

200 REM Test 2: Joystick buttons
210 PRINT "TEST 2: JOYSTICK BUTTONS"
220 REM PEEK(-16287) = button 0, PEEK(-16286) = button 1, PEEK(-16285) = button 2
230 B0 = PEEK(-16287)
240 B1 = PEEK(-16286)
250 B2 = PEEK(-16285)
260 PRINT "Button 0:"; B0; " Button 1:"; B1; " Button 2:"; B2
270 PRINT ""

300 REM Test 3: Graphics mode POKEs per manual
310 PRINT "TEST 3: GRAPHICS MODES"
320 HGR
330 HCOLOR=3
340 HPLOT 50,50 TO 100,100
350 REM Switch to HGR page 2 using POKE -16299
360 POKE -16299, 0
370 PRINT "Switched to HGR page 2"
380 HCOLOR=2
390 HPLOT 150,150 TO 200,200
400 REM Switch back to page 1 using POKE -16300
410 POKE -16300, 0
420 PRINT "Switched back to HGR page 1"
430 PRINT ""

500 REM Test 4: Text window margins
510 PRINT "TEST 4: TEXT WINDOW"
520 POKE 32, 5
530 POKE 33, 30
540 POKE 34, 2
550 POKE 35, 20
560 PRINT "Set text window margins (left=5, width=30, top=2, bottom=20)"
570 PRINT ""

600 REM Test 5: Error handling addresses per manual
610 PRINT "TEST 5: ERROR HANDLING"
620 X = PEEK(216)
630 PRINT "PEEK(216) (error handler flag)="; X
640 REM PEEK(222) would return error code
650 REM PEEK(219)*256+PEEK(218) would return error line
660 PRINT ""

700 REM Test 6: CALL commands per manual
710 PRINT "TEST 6: CALL COMMANDS"
720 HGR
730 HCOLOR=3
740 HPLOT 0,0 TO 279,191
750 PRINT "Drew line in HGR"
760 REM CALL -3086: Clear current hi-res page to black
770 CALL -3086
780 PRINT "Called CALL -3086 to clear HGR page"
790 HCOLOR=1
800 HPLOT 100,100 TO 200,100
810 REM CALL -3082: Clear to last HPLOT color
820 CALL -3082
830 PRINT "Called CALL -3082 to fill with last color"
840 HOME
850 PRINT ""

900 PRINT "MANUAL TESTS COMPLETED"
910 END
