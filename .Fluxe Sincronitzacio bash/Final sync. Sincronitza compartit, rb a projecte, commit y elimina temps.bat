@echo off
CALL "%EXTRACT_FOLDER%\.variables.bat"

echo pujant canvis a google drive
if not "%COMPUTERNAME%"=="LEGOTEQUE-PC" (
    CALL "Puja canvis a gdrive.bat"
)
echo canvis actualitzats a google drive

REM baixar canvis de la Raspberry a local
echo Esta conectada la Raspberry Pi? Vols volcar el seu contingut a la carpeta rb_files de projecte local? (S/N)
set /p respuesta="Escribe S para Sí o N para No: "
REM Validar la respuesta
if /i "%respuesta%"=="S" (
    CALL "%EXTRACT_FOLDER%\.b3-local sync.bat" raspberry-to-local
) else (
    echo No s'ha executat la sincronització desde RB a projecte.
)

REM Ejecutar commit
echo Vols realitzar un commit de projecte a GitHub? (S/N)
set /p respuesta="Escribe S para Si o N para No: "
REM Validar la respuesta
if /i "%respuesta%"=="S" (
    echo Ejecutando commit a github
    CALL "commit to github from projecte.bat"
) else (
    echo No s'ha executat la sincronitzacio desde RB a projecte.
)


REM Verificar si estamos en un equipo público
if not "%COMPUTERNAME%"=="LEGOTEQUE-PC" (
    REM Mover carpeta COMPARTIT a la papelera
    if exist "%COMPARTIT_PATH%" (
        powershell -command "Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory('%COMPARTIT_PATH%', 'OnlyErrorDialogs', 'SendToRecycleBin')"
        echo Carpeta COMPARTIT movida a la papelera.
    ) else (
        echo La carpeta COMPARTIT no se encontro en el escritorio. No se requiere eliminacion.
    )

    REM Eliminar el archivo rclone.conf
    if exist "%RCLONE_PATH%\rclone.conf" (
        del /F /Q "%RCLONE_PATH%\rclone.conf"
        echo Archivo rclone.conf eliminado permanentemente.
    ) else (
        echo Archivo rclone.conf no encontrado. No se requiere eliminacion.
    )

    REM eliminar la carpeta temporal de sincronizacion
    rmdir /S /Q "%EXTRACT_FOLDER%"
    echo %EXTRACT_FOLDER% eliminado

    REM Eliminar todos los archivos .bat del escritorio
    if exist "%DESKTOP_PATH%\*.bat" (
        del /F /Q "%DESKTOP_PATH%\*.bat"
        echo Todos los archivos .bat del escritorio han sido eliminados.
    ) else (
        echo No se encontraron archivos .bat en el escritorio.
    )

) else (
    echo Este es el equipo LEGOTEQUE-PC. No se eliminara el archivo rclone.conf ni los scripts.
)

pause
exit



