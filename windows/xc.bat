@echo off
IF "%1"=="" GOTO :EOF
SET DIR=%~dp0..
where /q cl || CALL "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat" || GOTO :EOF
python "%DIR%"\process.py "%1" > "%DIR%"\a.cc && ^
cl "%DIR%"\a.cc /Fe"%DIR%"\a.out && ^
"%DIR%"\a.out
