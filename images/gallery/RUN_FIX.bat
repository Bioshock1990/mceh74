@echo off
cls
title Instagram Downloader - Fix Version

echo.
echo ========================================
echo    INSTAGRAM DOWNLOADER - FIX
echo ========================================
echo.

:: Пробуем разные способы запуска Python
echo Testing Python commands...

echo Testing: python --version
python --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo Python found: %PYTHON_VERSION%
    set PYTHON_CMD=python
    goto :found_python
)

echo Testing: py --version  
py --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('py --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo Python found: %PYTHON_VERSION%
    set PYTHON_CMD=py
    goto :found_python
)

echo Testing: python3 --version
python3 --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo Python found: %PYTHON_VERSION%
    set PYTHON_CMD=python3
    goto :found_python
)

echo ERROR: Python not found!
echo Install Python from https://python.org
echo.
pause
exit /b 1

:found_python
echo.
echo Using command: %PYTHON_CMD%
echo.

:: Проверяем файлы
if not exist "instagram_downloader.py" (
    echo ERROR: instagram_downloader.py not found!
    pause
    exit /b 1
)

if not exist "links.txt" (
    echo ERROR: links.txt not found!
    pause
    exit /b 1
)

:: Проверяем instaloader
echo Checking instaloader...
%PYTHON_CMD% -c "import instaloader" >nul 2>&1
if errorlevel 1 (
    echo Installing instaloader...
    %PYTHON_CMD% -m pip install instaloader
    if errorlevel 1 (
        echo ERROR: Installation failed!
        pause
        exit /b 1
    )
    echo instaloader installed!
) else (
    echo instaloader already installed!
)
echo.

:: Проверяем ссылки
set /a link_count=0
for /f "usebackq tokens=*" %%a in ("links.txt") do (
    if not "%%a"=="" set /a link_count+=1
)

if %link_count%==0 (
    echo ERROR: No links in links.txt!
    pause
    exit /b 1
)

echo Found links: %link_count%
echo.

:: Очищаем старые папки
echo Cleaning old folders...
for /d %%d in (post_*) do (
    rmdir /s /q "%%d" >nul 2>&1
)
echo.

:: ЗАПУСК
echo ========================================
echo   STARTING DOWNLOAD...
echo ========================================
echo.

%PYTHON_CMD% instagram_simple.py

echo.
echo ========================================
echo   WORK COMPLETED!
echo ========================================
echo.

echo Created folders:
for /d %%d in (post_*) do (
    echo   Folder: %%d
    for %%f in ("%%d\*.jpg") do echo     Image: %%~nxf
    if exist "%%d\description.txt" echo     Description: description.txt
)
echo.

echo DONE!
echo.
pause
