import RPi.GPIO as GPIO
import time
import os
import sys
from subprocess import call

# Configuración del pin del botón
BUTTON_PIN = 3
PRESS_DURATION = 2  # Duración mínima (en segundos) para ejecutar el apagado

# Configuración del GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Usamos pull-up interno

# Ruta absoluta de la librería adicional
sys.path.append('/home/admin/Documents/llibreria_dispositius')

from buzzer_library import Buzzer

# Configuración del buzzer
PIN_BUZZER = 18
buzzer = Buzzer(PIN_BUZZER)

def play_welcome_melody():
    """Reproduce una melodía de bienvenida al iniciar el script"""
    print("Reproduciendo melodía de bienvenida...")
    buzzer.defined_melodies("welcome")

def play_shutdown_melody():
    """Reproduce una melodía antes de apagar el sistema"""
    print("Reproduciendo melodía de apagado...")
    buzzer.defined_melodies("shutdown")

def shutdown_system():
    """Apaga el sistema de forma segura"""
    print("Duración suficiente. Apagando el sistema...")
    play_shutdown_melody()  # Reproduce la melodía de apagado
    GPIO.cleanup()
    os.system("sudo shutdown -h now")

def shutdown_pressed(channel):
    """Verifica la duración del botón presionado y apaga el sistema si corresponde"""
    print("Botón presionado. Verificando duración...")
    start_time = time.time()
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Mientras el botón esté presionado
        time.sleep(0.1)
        press_duration = time.time() - start_time
        if press_duration >= PRESS_DURATION:
            shutdown_system()
            return
    print("Pulsación demasiado breve. Ignorando...")

def start_pigpiod():
    """Inicia el demonio pigpio si no está ya en ejecución"""
    try:
        print("Iniciando demonio pigpio...")
        call(["sudo", "pigpiod"])
        time.sleep(1)  # Espera un momento para asegurarse de que el demonio está activo
    except Exception as e:
        print(f"Error al iniciar pigpiod: {e}")

# Reproduce la melodía de bienvenida al iniciar el script
play_welcome_melody()

# Inicia el demonio pigpio
start_pigpiod()

# Detectar pulsaciones en el botón
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=shutdown_pressed, bouncetime=300)

print("Script ejecutándose. Esperando pulsaciones en el botón...")
try:
    while True:
        time.sleep(1)  # Mantén el script activo
except KeyboardInterrupt:
    print("\nInterrumpido por el usuario. Limpiando GPIO...")
finally:
    GPIO.cleanup([BUTTON_PIN])
    buzzer.stop()



# import sys
# sys.path.append('/home/admin/Documents/llibreria_dispositius')

# from buzzer_library import Buzzer

# pin_buzzer = 18
# buzzer = Buzzer(pin_buzzer)

# try:
#     # print("Reproduint melodia de benvinguda...")
#     # buzzer.defined_melodies("welcome")

#     print("Reproduint melodia de tancament...")
#     buzzer.defined_melodies("shutdown")

# finally:
#     print("Neteja de recursos...")
#     buzzer.stop()
