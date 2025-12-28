10 REM Test MID$ length handling
20 S$ = "HELLO WORLD"
30 PRINT MID$(S$,2,3)
40 PRINT MID$(S$,7)
50 REM Expected: ELL / WORLD
60 END