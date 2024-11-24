import RPi.GPIO as GPIO

def gpio_setmode(mode):
    if mode not in ["BCM", "BOARD"]:
        raise ValueError("El modo debe ser 'BCM' o 'BOARD'.")
    GPIO.setmode(GPIO.BCM if mode == "BCM" else GPIO.BOARD)

def gpio_cleanup(pins_l=[]):
    """Limpia la configuración de GPIO. Los pins especificos de pins_l si le pasamos la lista por parametro, todos los pins si no"""
    if not pins_l: 
        GPIO.cleanup()
    else: 
        GPIO.cleanup(pins_l)
    

def get_gpio():
    """Retorna el módulo GPIO para ser pasado como dependencia."""
    return GPIO