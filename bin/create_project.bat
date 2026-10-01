@echo off
setlocal DisableDelayedExpansion
rem Keep project generation in one implementation shared with PowerShell users.
where powershell.exe >nul 2>&1
if not errorlevel 1 (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_project.ps1" %*
    goto :finished
)
where pwsh.exe >nul 2>&1
if not errorlevel 1 (
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_project.ps1" %*
    goto :finished
)
echo This script requires Windows PowerShell or PowerShell 7 on PATH. >&2
exit /b 1

:finished
exit /b %errorlevel%
