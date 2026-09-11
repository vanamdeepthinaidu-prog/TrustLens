@echo off
title Push VisionTrust AI to GitHub
echo ===============================================================================
echo Pushing TrustLens repository to https://github.com/vanamdeepthinaidu-prog/TrustLens
echo ===============================================================================
echo.
echo Running: git push -u origin main
echo If a GitHub sign-in browser window opens, please log in as 'vanamdeepthinaidu-prog'.
echo.
cd /d "%~dp0"
git push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Code successfully pushed to GitHub!
    echo You can now go to Render.com and click 'Deploy'! 
) else (
    echo [FAILED] Push failed. Please check your GitHub account permissions.
)
echo.
pause

