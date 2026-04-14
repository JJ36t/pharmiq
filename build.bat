@echo off
title PharmIQ Builder
color 0A

echo.
echo ============================================================
echo   PharmIQ -- Smart Pharmacy Management System Builder
echo   Dept. of Intelligent Medical Systems -- Al-Diwaniyah
echo ============================================================
echo.

echo [1/4] Cleaning old build files...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist PharmIQ.spec  del /q PharmIQ.spec
echo       Done.

echo [2/4] Building EXE with PyInstaller...
pyinstaller --onefile --windowed --name "PharmIQ" ^
    --add-data "database;database" ^
    --add-data "ui;ui" ^
    --add-data "logic;logic" ^
    --add-data "reports;reports" ^
    main.py

echo [3/4] Copying database to dist...
if exist pharmiq.db (
    copy pharmiq.db dist\pharmiq.db
    echo       pharmiq.db copied.
) else (
    echo       No existing database -- will be created on first run.
)

echo [4/4] Opening output folder...
explorer dist

echo.
echo ============================================================
echo   Build complete!  Find PharmIQ.exe in the dist/ folder.
echo ============================================================
echo.
pause
