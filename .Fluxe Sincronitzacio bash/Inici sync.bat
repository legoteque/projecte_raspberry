@echo off
REM Descargar archivo de variables desde Google Drive
echo Descarregant l'arxiu de variables desde Google Drive...
set "VARIABLES_LINK=https://drive.google.com/uc?export=download&id=1rWesXzVDpB-FxOFwIDbV0NKM9A"
REM Crear la carpeta SYNC_TEMP si no existe (ha de coincidir sempre amb EXTRACT_FOLDER de .variables.bat)
set "EXTRACT_FOLDER=%USERPROFILE%\Downloads\SYNC_TEMP"
if not exist "%EXTRACT_FOLDER%" mkdir "%EXTRACT_FOLDER%"
REM Descargar el archivo como ".variables.bat"
curl -L "%VARIABLES_LINK%" -o "%EXTRACT_FOLDER%\variables.txt"
rename "%EXTRACT_FOLDER%\variables.txt" ".variables.bat"

CALL "%EXTRACT_FOLDER%\.variables.bat"

REM Descargar archivo desde Google Drive
echo Descargando el archivo .zip desde Google Drive...
curl -L "%ZIP_LINK%" -o "%ZIP_PATH%"

:: Verificar si la descarga fue exitosa
if exist "%ZIP_PATH%" (
	echo Archivo descargado como %ZIP_PATH%.

	echo Descomprimiendo el archivo ZIP...
	powershell -command "Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%EXTRACT_FOLDER%' -Force"
	echo Archivo ZIP descomprimido en %EXTRACT_FOLDER%.

	del /F /Q "%ZIP_PATH%"
	echo Archivo ZIP eliminado
	
	if "%COMPUTERNAME%"=="LEGOTEQUE-PC" (
		rename "%EXTRACT_FOLDER%\Final sync. Sincronitza compartit, rb a projecte, commit y elimina temps.bat" "RB a projecte y commit.bat"
	)
	
	echo Moviendo los archivos .bat al escritorio...
	REM Recorrer todos los archivos .bat en la carpeta
	REM Habilitar expansión de variables en tiempo de ejecución
	setlocal enabledelayedexpansion
	for %%F in ("%EXTRACT_FOLDER%\*.bat") do (
		REM Obtener el nombre del archivo
		set "filename=%%~nxF"
    	set "firstchar=!filename:~0,1!"
		set "filename_path=%%F"
		if not "!firstchar!"=="." (
			if "%COMPUTERNAME%"=="LEGOTEQUE-PC" (
				if /i not "!filename!"=="Puja canvis a gdrive.bat" (
					move "!filename_path!" "%USERPROFILE%\Desktop" >nul 2>&1
				) else (
					echo Excluyendo archivo: !filename!
				)
			) else (
				REM Mover archivos .bat en otros equipos (que no comiencen por ".")
				move "!filename_path!" "%USERPROFILE%\Desktop" >nul 2>&1
			)
		) else (
			echo Excluyendo !filename! porque comienza con punto
		)
	)
	REM Deshabilitar expansión de variables en tiempo de ejecución
	endlocal

	REM Verificar si no estamos en LEGOTEQUE-PC
	if not "%COMPUTERNAME%"=="LEGOTEQUE-PC" (
		REM Mover el archivo rclone.conf a su carpeta
		move "%EXTRACT_FOLDER%\rclone.conf" "%RCLONE_PATH%"
		echo Archivos .bat y rclone.conf movidos exitosamente.
		
		REM Limpiar zip
		del /F /Q "%ZIP_PATH%"
		echo %ZIP_PATH% eliminado.

		echo -----------------------------------------------------

		REM Sincronizar la carpeta compartida desde Google Drive al escritorio
		echo Volcando la carpeta compartida al escritorio...
		rclone sync "%REMOTE_GD_COMPARTIT%" "%COMPARTIT_PATH%" --progress --create-empty-src-dirs

		if exist "%COMPARTIT_PATH%" (
			echo Carpeta compartida sincronizada exitosamente en el escritorio.
		) else (
			echo Error: No se pudo sincronizar la carpeta compartida.
		)
	) else (
	echo Archivos .bat excepto de sincronizacion gdrive movidos exitosamente.
	echo -----------------------------------------------------
    echo Este es el equipo LEGOTEQUE-PC. No se descargara rclone.conf ni se sincronizara con COMPARTIT puesto que tienes GDrive.
	)
	
	echo -----------------------------------------------------

	echo Clonant repositori
	CALL "%EXTRACT_FOLDER%\.clone from github to projecte.bat"

	echo -----------------------------------------------------

	REM Volcar archivos rb_files del repositorio a la Raspberry
	echo Está conectada i encesa la Raspberry Pi?
	set /p respuesta="Vols sincronizarla amb els arxius rb_files desde projecte? (S/N):"
	REM Habilitar expansión diferida para manejar variables correctamente
    setlocal enabledelayedexpansion

    REM Eliminar espacios y recortar solo el primer carácter
	for /f "tokens=1" %%a in ("!respuesta!") do set "respuesta=%%a"
	set "respuesta=!respuesta:~0,1!"

	REM Mostrar la respuesta capturada para depuración
	echo Respuesta capturada: "!respuesta!"

	REM Validar la respuesta
	if /i "!respuesta!"=="S" (
		CALL "%EXTRACT_FOLDER%\.rb3-local sync.bat" local-to-raspberry
		echo Sincronizacion completada con éxito.
	) else if /i "!respuesta!"=="N" (
		echo Has decidido no sincronizar. No se realizará ninguna accion.
	) else (
		echo Respuesta no valida. Por favor, responde con S o N.
	)

	if not "%COMPUTERNAME%"=="LEGOTEQUE-PC" (
		REM Eliminar este archivo .bat definitivamente
		REM set "THIS_FILE=%~f0"
		REM start /b "" cmd /c del /F /Q "%THIS_FILE%"
	)


) else (
	echo Error: No se pudo descargar el archivo .zip desde Google Drive.
)
pause
exit

