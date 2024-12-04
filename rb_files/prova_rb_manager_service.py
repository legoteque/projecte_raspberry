import RPi.GPIO as GPIO
import os, sys, time, subprocess
from pigpio import FALLING_EDGE, RISING_EDGE, EITHER_EDGE
from llibreria_dispositius.gpio_manager import gpio_setmode, gpio_cleanup
from llibreria_dispositius.buzzer_library import Buzzer
from llibreria_dispositius.rotary_encoder_library import RotaryEncoder
from llibreria_dispositius.lcd_library import LCD

#Display-Menu--------------------------------
MENU_STRUCTURE = {
    "Temperatura": None,
    "Alarmas": None,
    "Disco Duro": None,
    "Memoria RAM": None,
    "APAGAR RB": ["SI", "NO"],  # Submenú para "APAGAR RB"
}

# Estado del menú
menu_stack = ["MENU:"]  # Pila para rastrear el estado actual
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
        shutdown_system()
    elif selected_option == "NO" and menu_stack[-1] == "APAGAR RB":
        # Volver al menú principal
        menu_stack.pop()
        menu_options = list(MENU_STRUCTURE.keys())
        current_option = 0
        lcd.display(content=menu_options[current_option], title=menu_stack[-1])
    else:
        print(f"Seleccionaste: {selected_option}")
#----------------------------------------

def start_pigpiod():
    """Inicia el demonio pigpio si no está ya en ejecución."""
    try:
        # Comprueba si el demonio ya está corriendo
        result = subprocess.run(["pgrep", "pigpiod"], capture_output=True, text=True)
        if result.returncode == 0:
            print("El demonio pigpio ya está en ejecución.")
        else:
            print("Iniciando el demonio pigpio...")
            subprocess.run(["sudo", "pigpiod"], check=True)
            time.sleep(2)  # Espera un momento para asegurarse de que el demonio está activo

        # Verifica si el demonio está operativo
        result = subprocess.run(["pgrep", "pigpiod"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("No se pudo iniciar el demonio pigpio.")
        print("Demonio pigpio iniciado correctamente.")
    except Exception as e:
        print(f"Error al iniciar el demonio pigpio: {e}")
        raise

def start_lcd_menu():
    lcd.lcd_clear()
    lcd.display(content="Iniciando Raspberry..", title="Bienvenido!")
    time.sleep(4)

def play_melody(melody):
    #buzzer.defined_melodies("melody")
    pass

def shutdown_system():
    """Apaga el sistema de forma segura"""
    #desactivamos el rotatory encoder
    encoder.disable_callbacks()

    lcd.display(content="Cerrando Raspberry..", title="Adios!")
    play_melody("shutdown") # Reproduce la melodía de apagado
    gpio_cleanup()
    sys.exit()
    #os.system("sudo shutdown -h now")

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

# Configuración del GPIO
#GPIO.setmode(GPIO.BCM)
gpio_setmode("BCM")

#Inicia el LCD
pins = {"rs":23, "e":24, "d4":26, "d5":19, "d6":13, "d7":6}
# Crear un objeto LCD con los pines GPIO de la Raspberry Pi
lcd = LCD(rs=pins["rs"], e=pins["e"], d4=pins["d4"], d5=pins["d5"], d6=pins["d6"], d7=pins["d7"])

#Mensaje de bienvenida
start_lcd_menu()

# Configuración del pin del encendido/apagado (BUTTON)
BUTTON_PIN = 3
PRESS_DURATION = 2  # Duración mínima (en segundos) para ejecutar el apagado
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Usamos pull-up interno


# Inicia el demonio pigpio
start_pigpiod()

# Configuración del buzzer
PIN_BUZZER = 18
buzzer = Buzzer(PIN_BUZZER)

# Reproduce la melodía de bienvenida al iniciar el script
play_melody("welcome")

# Inicialización del encoder
encoder = RotaryEncoder(gpio_clk=5, gpio_dt=16, gpio_sw=20, rotation_callback=rotation_callback, button_callback=button_callback)

# Mostrar el menú inicial
lcd.display(content=menu_options[current_option], title=menu_stack[-1])

# Detectar pulsos encendido/apagado en GPIO3
#GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=shutdown_pressed, bouncetime=300)

print("Script ejecutándose. Esperando pulsaciones en el botón...")
try:
    while True:
        time.sleep(3600)  # Mantén el script activo
except KeyboardInterrupt:
    print("\nInterrumpido por el usuario. Limpiando GPIO...")
finally:
    buzzer.stop()
    lcd.lcd_clear()
    encoder.stop()
    gpio_cleanup()
