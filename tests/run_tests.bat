@echo off
chcp 65001 >nul
title Executar Testes - My Summer Car Mod Installer

set "PYTHON_EXE="

:: 1. Tenta python no PATH
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
    goto :RUN
)

:: 2. Tenta py launcher
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=py"
    goto :RUN
)

:: 3. Locais conhecidos do Windows
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%PROGRAMFILES%\Python313\python.exe"
    "%PROGRAMFILES%\Python312\python.exe"
    "%PROGRAMFILES%\Python311\python.exe"
    "%PROGRAMFILES%\Python310\python.exe"
    "%PROGRAMFILES%\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe"
    "%PROGRAMFILES%\Blender Foundation\Blender 5.1\5.1\python\bin\python.exe"
    "%PROGRAMFILES%\Blender Foundation\Blender 5.0\5.0\python\bin\python.exe"
    "%PROGRAMFILES%\Blender Foundation\Blender 4.2\4.2\python\bin\python.exe"
) do (
    if exist %%P (
        set "PYTHON_EXE=%%P"
        goto :RUN
    )
)

echo [ERRO] Python não foi encontrado no sistema.
pause
exit /b 1

:RUN
"%PYTHON_EXE%" "%~dp0run_all_tests.py"
echo.
pause
