import RPi.GPIO as GPIO
import time
import os

# Configuración del pin del botón
BUTTON_PIN = 3
PRESS_DURATION = 2  # Duración mínima (en segundos) para ejecutar el apagado

# Configuración del GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Usamos pullº-up interno

def shutdown_system():
    print("Duración suficiente. Apagando el sistema...")
    GPIO.cleanup()
    os.system("sudo shutdown -h now")

def shutdown_pressed(channel):
    """Función para apagar el sistema"""
    print("Botón presionado. Verificando duración...")
    start_time = time.time()
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Mientras el botón esté presionado
        time.sleep(0.1)
        press_duration = time.time() - start_time
        if press_duration >= PRESS_DURATION:
            shutdown_system()
    print("Pulsación demasiado breve. Ignorando...")

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
