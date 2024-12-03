import time
from pigpio import FALLING_EDGE, RISING_EDGE, EITHER_EDGE
from llibreria_dispositius.gpio_manager import gpio_setmode, gpio_cleanup
from llibreria_dispositius.rotary_encoder_library import RotaryEncoder
from llibreria_dispositius.lcd_library import LCD 


# Menú principal y submenús
MENU_STRUCTURE = {
    "Temperatura": None,
    "Alarmas": None,
    "Disco Duro": None,
    "Memoria RAM": None,
    "APAGAR RB": ["SI", "NO"],  # Submenú para "APAGAR RB"
}

# Estado del menú
menu_stack = ["MENU"]  # Pila para rastrear el estado actual
menu_options = list(MENU_STRUCTURE.keys())  # Opciones del menú actual
current_option = 0  # Índice actual en el menú

# Callback para manejar giros
def rotation_callback(direction):
    global current_option
    lcd.lcd_clear()
    if direction == "Clockwise":
        current_option = (current_option + 1) % len(menu_options)
    elif direction == "Counterclockwise":
        current_option = (current_option - 1) % len(menu_options)

    # Mostrar la opción actual en el LCD
    lcd.display(content=menu_options[current_option], title=menu_stack[-1])

# Callback para manejar pulsaciones del botón
def button_callback():
    global menu_stack, menu_options, current_option
    selected_option = menu_options[current_option]

    # Verificar si la opción tiene un submenú
    if selected_option in MENU_STRUCTURE and MENU_STRUCTURE[selected_option]:
        # Agregar el submenú a la pila
        menu_stack.append(selected_option)
        menu_options = MENU_STRUCTURE[selected_option]
        current_option = 0
        lcd.display(content=menu_options[current_option], title=menu_stack[-1])
    elif selected_option == "SI" and menu_stack[-1] == "APAGAR RB":
        # Apagar la Raspberry Pi
        lcd.display(content="Apagando...", title="Confirmado")
        time.sleep(2)
        print("Apagar la raspberry")
    elif selected_option == "NO" and menu_stack[-1] == "APAGAR RB":
        # Volver al menú principal
        menu_stack.pop()
        menu_options = list(MENU_STRUCTURE.keys())
        current_option = 0
        lcd.display(content=menu_options[current_option], title=menu_stack[-1])
    else:
        print(f"Seleccionaste: {selected_option}")



# Inicializar el LCD
gpio_setmode("BCM")
pins = {"rs":23, "e":24, "d4":26, "d5":19, "d6":13, "d7":6}
# Crear un objeto LCD con los pines GPIO de la Raspberry Pi
lcd = LCD(rs=pins["rs"], e=pins["e"], d4=pins["d4"], d5=pins["d5"], d6=pins["d6"], d7=pins["d7"])

# Inicialización del encoder
encoder = RotaryEncoder(gpio_clk=5, gpio_dt=16, gpio_sw=20, rotation_callback=rotation_callback, button_callback=button_callback)

# Mostrar el menú inicial
lcd.display(content=menu_options[current_option], title=menu_stack[-1])

# Mantener el programa corriendo para que los callbacks funcionen
try:
    print("Esperando eventos del encoder. Presiona Ctrl+C para salir.")
    while True:
        time.sleep(1)  # El programa sigue activo para escuchar eventos
except KeyboardInterrupt:
    print("Saliendo...")
finally:
    encoder.stop()
    lcd.clean_pins()