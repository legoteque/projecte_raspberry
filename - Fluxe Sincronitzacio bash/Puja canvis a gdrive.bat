@echo off
CALL "%EXTRACT_FOLDER%\.variables.bat"

REM Sincronizar cambios locales en la carpeta del equipo hacia Google Drive, incluyendo carpetas vacías
if exist "%RCLONE_PATH%\rclone.conf" (
    if exist "%COMPARTIT_PATH%" (
		rclone sync "%COMPARTIT_PATH%" "%REMOTE_GD_COMPARTIT%" --checksum --track-renames --delete-excluded --delete-during --create-empty-src-dirs --progress
        echo Sincronización a google drive completada.
    ) else (
        echo Error: No se encontró la carpeta compartit en la ruta especificada.
        pause
        exit /b
    )
) else (
    echo Error: No se encontró el archivo de configuración rclone.conf en la carpeta de configuración.
    pause
    exit /b
)

pause
exit /b


