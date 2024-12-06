@echo off
CALL "%EXTRACT_FOLDER%\.variables.bat"

REM Configura las variables del repositorio\
SETLOCAL ENABLEDELAYEDEXPANSION

REM Obtiene la fecha en formato d\'eda/mes/a\'f1o
FOR /F "tokens=2 delims==" %%I IN ('"wmic os get localdatetime /value | findstr LocalDateTime"') DO SET DATETIME=%%I

REM Extrae el d\'eda y el mes
SET DIA=!DATETIME:~6,2!
SET MES=!DATETIME:~4,2!

REM Convierte el mes al nombre en catal
FOR %%A IN (01-Gener 02-Febrer 03-Mar\'e7 04-Abril 05-Maig 06-Juny 07-Juliol 08-Agost 09-Setembre 10-Octubre 11-Novembre 12-Desembre) DO (
    FOR /F "tokens=1,2 delims=-" %%B IN ("%%A") DO (
        IF "!MES!"=="%%B" SET MES_TEXT=%%C
    )
)

REM Formatea el mensaje de commit
SET COMMIT_MSG=!DIA! de !MES_TEXT!

REM Rama del repositorio
SET BRANCH=master

REM Cambia al directorio del repositorio
cd %PROJECTE_LOCAL_PATH%
IF ERRORLEVEL 1 (
    echo Error: No se encontr\'f3 el directorio del repositorio.
	pause
    exit
)

REM Realiza un pull para actualizar los cambios desde el repositorio remoto
REM git pull origin %BRANCH%
REM IF ERRORLEVEL 1 (
REM     echo Error al realizar el pull.
REM 	pause
REM     exit
REM )

REM Agrega los cambios manuales al staging
git add .

REM Realiza el commit con un mensaje
git commit -m "%COMMIT_MSG%"
IF ERRORLEVEL 1 (
    echo No hay cambios para hacer commit.
	pause
    exit
)

REM Realiza el push al repositorio remoto
git push origin %BRANCH%
IF ERRORLEVEL 1 (
    echo Error al realizar el push.
	pause
    exit
)

echo Proceso completado correctamente.
pause
exit