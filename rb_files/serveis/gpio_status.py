import RPi.GPIO as GPIO
import os

# Configuración del GPIO
GPIO_PIN = 4  # GPIO4 (físico 7)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Función para establecer el estado
def set_raspberry_status(is_on):
    if is_on:
        GPIO.output(GPIO_PIN, GPIO.HIGH)  # Encendida
        print("Raspberry Pi: GPIO4 establecido en HIGH (ENCENDIDA)")
    else:
        GPIO.output(GPIO_PIN, GPIO.LOW)  # Apagada
        print("Raspberry Pi: GPIO4 establecido en LOW (APAGADA)")

# Ejecutar al inicio o apagado
if __name__ == "__main__":
    if "start" in os.sys.argv:  # Evento de inicio
        set_raspberry_status(True)
    elif "stop" in os.sys.argv:  # Evento de apagado
        set_raspberry_status(False)
        GPIO.cleanup()
