@echo off
setlocal
title AutoInstallModMySummerCar
chcp 65001 >nul 2>&1

cd /d "%~dp0"

echo ========================================
echo  AutoInstallModMySummerCar
echo ========================================
echo.

if not exist "%~dp0AutoInstallModMySummerCar.exe" (
    echo [ERRO] O executavel AutoInstallModMySummerCar.exe nao foi encontrado!
    echo Certifique-se de que o arquivo AutoInstallModMySummerCar.exe esta na mesma pasta.
    echo.
    pause
    exit /b 1
)

echo Iniciando o instalador...
echo.

"%~dp0AutoInstallModMySummerCar.exe" %*

if errorlevel 1 (
    echo.
    echo O programa finalizou com avisos ou foi interrompido.
)

echo.
pause
exit /b 0