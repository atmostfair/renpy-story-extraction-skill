@echo off
py -3 "%~dp0unrpyc.py" %*
exit /b %errorlevel%