@echo off
REM Comprobamos si la carpeta ya existe
if exist "%PROJECTE_LOCAL_PATH%" (
    echo La carpeta %PROJECTE_LOCAL_PATH% ya existe.
    echo ¿Deseas eliminarla y clonar el repositorio nuevamente? [S/N]
    set /p user_input=Respuesta:   

    REM Habilitar expansión diferida para manejar variables correctamente
    setlocal enabledelayedexpansion
    set "user_input=!user_input!"

    REM Comprobar la respuesta del usuario
    if /i "!user_input!"=="S" (
        echo Eliminando la carpeta %PROJECTE_LOCAL_PATH%...
        rmdir /S /Q "%PROJECTE_LOCAL_PATH%"
        if %ERRORLEVEL% NEQ 0 (
            echo Error: No se pudo eliminar la carpeta %PROJECTE_LOCAL_PATH%.
            endlocal
            exit /b 1
        )
        echo %PROJECTE_LOCAL_PATH% eliminada exitosamente.
    ) else if /i "!user_input!"=="N" (
        echo No se clonara el repositorio.
        endlocal
        pause
        exit /b 1
    ) else (
        echo Respuesta no valida. Por favor, responde con S o N.
        endlocal
        pause
        exit /b 1
    )
)

REM Clonar el repositorio en la carpeta especificada
echo Clonando el repositorio en %PROJECTE_LOCAL_PATH%...
git clone https://github.com/legoteque/projecte_raspberry.git "%PROJECTE_LOCAL_PATH%"

REM Comprobar si el comando git clone tuvo éxito
if %ERRORLEVEL% NEQ 0 (
    echo Error: No se pudo clonar el repositorio.
) else (
    echo Repositorio clonado exitosamente en %PROJECTE_LOCAL_PATH%.
)
exit /b 1