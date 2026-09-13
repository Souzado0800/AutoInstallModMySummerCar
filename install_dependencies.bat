@echo off
chcp 65001 >nul
title Instalar Dependências Opcionais - My Summer Car Mod Installer
echo ==============================================================================
echo       INSTALADOR DE DEPENDÊNCIAS OPCIONAIS (RARFILE)
echo ==============================================================================
echo.

set "PYTHON_EXE="

:: 1. Tenta python no PATH
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=python"
    goto :INSTALL
)

:: 2. Tenta py launcher
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_EXE=py"
    goto :INSTALL
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
        goto :INSTALL
    )
)

echo [ERRO] Python não foi encontrado no sistema.
pause
exit /b 1

:INSTALL
echo Utilizando Python: "%PYTHON_EXE%"
echo Instalando dependências de requirements.txt...
echo.
"%PYTHON_EXE%" -m pip install -r "%~dp0requirements.txt"
echo.
echo Concluído!
pause
