@echo off
title Push WhatsApp Business Agent to GitHub
echo ========================================================
echo   Pushing WhatsApp Business Agent to GitHub
echo   Remote: https://github.com/Ahmad-Haassan/WhatsApp-Business-Agent.git
echo   Branch: main
echo ========================================================
echo.

git push -u origin main

echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo   [SUCCESS] Code successfully pushed to GitHub!
    echo ========================================================
) else (
    echo ========================================================
    echo   [ERROR] Push failed. If prompted, please complete
    echo   the GitHub browser login popup.
    echo ========================================================
)
echo.
pause
