@echo off

:: Crear directorio de respaldo si no existe
if not exist %RB_DEL_BACKUP_PATH% (
    mkdir %RB_DEL_BACKUP_PATH%
)

:: Validar parámetro de dirección
if "%1"=="" (
    echo Error: No se ha especificado la dirección de sincronización.
    echo Uso: script.bat [remote-to-local|local-to-remote]
    exit /b 1
)

if "%1"=="raspberry-to-local" (
    :: Sincronizar del remoto al local
    echo Volcant de la raspberry a local...
    rclone sync "%REMOTE_RB%" "%RB_LOCAL%" --checksum --track-renames --delete-excluded --delete-during --create-empty-src-dirs --backup-dir %BACKUP_DIR% --progress --key-file %USERPROFILE%\.ssh\id_rsa

) else if "%1"=="local-to-raspberry" (
    :: Sincronizar del local al remoto
    echo Volcant de local a la raspberry...
    rclone sync "%RB_LOCAL%" "%REMOTE_RB%" --checksum --track-renames --delete-excluded --delete-during --create-empty-src-dirs --backup-dir %BACKUP_DIR% --progress --key-file %USERPROFILE%\.ssh\id_rsa

) else (
    echo Error: Dirección de sincronización no válida.
    echo Uso: script.bat [remote-to-local|local-to-remote]
    exit /b 1
)

:: Pausa para verificar resultados
pause
