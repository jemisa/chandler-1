@ECHO OFF
cd ..\Chandler
set PATHBAK=%PATH%
set PATH=..\release\bin
..\release\bin\python Chandler.py
set PATH=%PATHBAK%
