@echo off
echo Installing test dependencies...
pip install -r tests\requirements.txt

echo.
echo Running tests...
pytest tests\ -v

echo.
echo Test run completed!
pause
