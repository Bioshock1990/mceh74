@echo off
echo Starting local server...
start http://localhost:8000
cd /d "%~dp0"
C:\xampp\php\php.exe -S localhost:8000
pause
