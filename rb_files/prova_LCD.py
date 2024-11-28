from llibreria_dispositius.lcd_library import LCD 
from llibreria_dispositius.gpio_manager import gpio_setmode, gpio_cleanup
from time import sleep

gpio_setmode("BCM")

pins = {"rs":23, "e":24, "d4":26, "d5":19, "d6":13, "d7":6}

# Crear un objeto LCD con los pines GPIO de la Raspberry Pi
lcd = LCD(rs=pins["rs"], e=pins["e"], d4=pins["d4"], d5=pins["d5"], d6=pins["d6"], d7=pins["d7"])

# Escribir en el LCD
FRASE = ("TENGO UN DEFECTO EN LA NARIZ QUE ES MUY MOLESTO QUE ME SUCEDE IGUAL EN VIGO "
"QUE EN MADRID NO SE POR QUE CUANDO ME PONGO MUY NERVIOSO ME DA UN PICOR IRRESISTIBLE "
"EN LA NARIZ. SI EN EL COLEGIO HAY UN EXAMEN IMPORTANTE O POR LAS NOTAS ME REGANA MI PAPA "
"ME DA ENSEGUIDA ESE PICOR TAN EXCITANTE QUE POR DESGRACIA SIEMPRE ME HACE ESTORNUDAR AH  "
"AH ACHIS COMO ME PICA LA NARIZ COMO ME PICA LA NARIZ YA NO LO PUEDO RESISTIR COMO ME PICA LA NARIZ")

try:
    lcd.lcd_write(FRASE, scroll=True)
    # Pausa para visualizar el mensaje
    sleep(5)

    # Limpiar la pantalla
    lcd.lcd_clear()

except KeyboardInterrupt:
    print("\nInterrumpido por el usuario.")
finally:
    lcd.lcd_clear()
    gpio_cleanup(list(pins.values()))