from llibreria_dispositius.lcd_library import LCD 
from llibreria_dispositius.gpio_manager import gpio_setmode, gpio_cleanup
from time import sleep

gpio_setmode("BCM")

pins = {"rs":23, "e":24, "d4":26, "d5":19, "d6":13, "d7":6}

# Crear un objeto LCD con los pines GPIO de la Raspberry Pi
lcd = LCD(rs=pins["rs"], e=pins["e"], d4=pins["d4"], d5=pins["d5"], d6=pins["d6"], d7=pins["d7"])

# Escribir en el LCD
FRASE = ("TENGO un slfdjgnsldkgslkg sdlgkws lkgds lkedsnlgks nlskd nldskn glkdsg ")

try:
    lcd.display(content=FRASE, title="el títol")
    # Pausa para visualizar el mensaje
    sleep(5)

    # Limpiar la pantalla
    lcd.lcd_clear()

except KeyboardInterrupt:
    print("\nInterrumpido por el usuario.")
finally:
    print("limpiando")
    lcd.lcd_clear()
    gpio_cleanup(list(pins.values()))