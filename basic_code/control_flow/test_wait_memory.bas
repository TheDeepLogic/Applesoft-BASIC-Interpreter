10 REM WAIT should return immediately when condition is met
20 POKE 1000,1
30 WAIT 1000,1,1
40 PRINT "WAIT1 OK"
50 REM WAIT without value returns when masked != 0
60 POKE 1001,1
70 WAIT 1001,1
80 PRINT "WAIT2 OK"
90 END