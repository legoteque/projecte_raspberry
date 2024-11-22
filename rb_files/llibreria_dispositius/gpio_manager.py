import RPi.GPIO as GPIO

def gpio_setmode(mode):
    if mode == "BCM": GPIO.setmode(GPIO.BCM)
    if mode == "BOARD": GPIO.setmode(GPIO.BOARD)

def gpio_cleanup():
    """Limpia la configuración de GPIO."""
    GPIO.cleanup()

def get_gpio():
    """Retorna el módulo GPIO para ser pasado como dependencia."""
    return GPIO