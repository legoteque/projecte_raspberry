from llibreria_dispositius.gpio_manager import get_gpio as GPIO
from time import sleep

lcd_commands = {
    "Clear Display": 0x01,  # Borra la pantalla y mueve el cursor a la posición inicial
    "Return Home": 0x02,  # Mueve el cursor a la posición inicial sin borrar la pantalla
    "Initialize Step 2 (Function Set 4 bits)": 0x02,  # Configuración para modo 4 bits
    "Initialize Step 1 (Function Set)": 0x03,  # Paso inicial de la secuencia de inicialización
    "Entry Mode Set (Decrement, No Shift)": 0x04,  # Decrementa el cursor, sin desplazar pantalla
    "Entry Mode Set (Decrement, Shift)": 0x05,  # Decrementa el cursor, desplaza pantalla
    "Entry Mode Set (Increment, No Shift)": 0x06,  # Incrementa el cursor, sin desplazar pantalla
    "Entry Mode Set (Increment, Shift)": 0x07,  # Incrementa el cursor, desplaza pantalla
    "Display OFF": 0x08,  # Apaga la pantalla, el cursor y el parpadeo
    "Display ON, Cursor OFF, Blink OFF": 0x0C,  # Enciende pantalla, oculta cursor y parpadeo
    "Display ON, Cursor ON, Blink OFF": 0x0E,  # Enciende pantalla, muestra cursor, sin parpadeo
    "Display ON, Cursor ON, Blink ON": 0x0F,  # Enciende pantalla, muestra cursor y parpadeo
    "Cursor Move Left": 0x10,  # Mueve el cursor a la izquierda
    "Cursor Move Right": 0x14,  # Mueve el cursor a la derecha
    "Display Shift Left": 0x18,  # Desplaza todo el contenido de la pantalla a la izquierda
    "Display Shift Right": 0x1C,  # Desplaza todo el contenido de la pantalla a la derecha
    "Function Set (4 bits, 1 line, 5x8)": 0x20,  # Configura: 4 bits, 1 línea, matriz 5x8
    "Function Set (4 bits, 2 lines, 5x8)": 0x28,  # Configura: 4 bits, 2 líneas, matriz 5x8
    "Function Set (8 bits, 1 line, 5x8)": 0x30,  # Configura: 8 bits, 1 línea, matriz 5x8
    "Function Set (8 bits, 2 lines, 5x8)": 0x38,  # Configura: 8 bits, 2 líneas, matriz 5x8
    "Set CGRAM Address": 0x40,  # Dirección inicial de la memoria CGRAM
    "Set DDRAM Address Line 1": 0x80,  # Dirección inicial de la línea 1
    "Set DDRAM Address Line 2": 0xC0,  # Dirección inicial de la línea 2
    }

class LCD:
    def __init__(self, rs, e, d4, d5, d6, d7, auto_init=True):
        """Constructor de la clase LCD.
        auto_init: Si es True, inicializa automáticamente el LCD (por defecto True)"""
        self.RS = rs
        self.E = e
        self.DATA_PINS = [d4, d5, d6, d7]

        GPIO.setup([self.RS, self.E] + self.DATA_PINS, GPIO.OUT)

        # Inicializar el LCD si se permite
        if auto_init:
            self.lcd_init()

    def send_half_byte(self, data):
        """Envía un medio byte al LCD (modo 4 bits).
        :param data: Medio byte a enviar (4 bits, entero entre 0 y 15)"""

        for i in range(4):  # Solo se usan 4 bits (D4-D7)
            GPIO.output(self.DATA_PINS[i], (data >> i) & 0x01)
        GPIO.output(self.E, True)  # Pulso en Enable
        sleep(0.001)               # Espera breve
        GPIO.output(self.E, False)
    
    def send_byte(self, data, is_data):
        """Envía un byte completo al LCD (dividido en 2 medios bytes).
        :param data: Byte a enviar (8 bits, entero entre 0 y 255)
        :param is_data: True para enviar datos, False para comandos"""

        GPIO.output(self.RS, is_data)  # Configurar RS (0 = comando, 1 = datos)
        self.send_half_byte(data >> 4)  # Mitad alta (B7-B4)
        self.send_half_byte(data & 0x0F)  # Mitad baja (B3-B0)
        #sleep(0.002)  # Espera para que el LCD procese

    def send_command(self, command):
        data = lcd_commands[command]
        self.send_byte(data, is_data=False)
    
    def envia_caracter(self, char):
        data = ord(char)
        self.send_byte(data, is_data=True)

    def lcd_init(self):
        """Inicializa el LCD en modo 4 bits."""
        GPIO.output(self.RS, False)  # RS a 0 para comandos
        for _ in range(3):
            self.send_half_byte(0x03)  # Secuencia de inicialización
            #sleep(0.005)
        self.send_half_byte(0x02)  # Configuración de 4 bits
        self.send_command("Function Set (4 bits, 2 lines, 5x8)")
        self.send_command("Display ON, Cursor OFF, Blink OFF")
        self.send_command("Entry Mode Set (Increment, No Shift)")
        self.send_command("Clear Display")

    def lcd_write(self, message, scroll=True, delay=0.2, title="Mensaje:"):
        """Escribe un mensaje en el LCD con diferentes comportamientos según el valor de scroll.
        :param message: Mensaje a escribir (cadena de texto).
        :param scroll: True para habilitar desplazamiento en mensajes largos (por defecto True).
        :param delay: Tiempo en segundos entre cada desplazamiento (por defecto 0.2s).
        :param title: Texto fijo en la línea 1 cuando scroll=True (por defecto "Mensaje:")."""
        visible_chars = 16  # Capacidad de una línea
        message = message.strip()  # Limpiar espacios innecesarios del mensaje

        if not scroll:
            # Caso scroll=False: Escribir el mensaje en dos líneas instantáneamente
            line1 = message[:visible_chars]  # Primera línea: hasta 16 caracteres
            line2 = message[visible_chars:2 * visible_chars]  # Segunda línea: los siguientes 16 caracteres

            # Escribir en la línea 1
            self.send_command("Set DDRAM Address Line 1")
            for char in line1.ljust(visible_chars):  # Rellenar con espacios si es más corto
                self.envia_caracter(char)

            # Escribir en la línea 2
            self.send_command("Set DDRAM Address Line 2")
            for char in line2.ljust(visible_chars):  # Rellenar con espacios si es más corto
                self.envia_caracter(char)
        else:
            # Caso scroll=True:
            # Línea 1: Escribir el título solo una vez
            self.send_command("Set DDRAM Address Line 1")
            for char in title.ljust(visible_chars):  # Escribir el título y rellenar con espacios
                self.envia_caracter(char)

            # Animación inicial en la línea 2
            self.send_command("Set DDRAM Address Line 2")
            for i in range(min(len(message), visible_chars)):
                line2 = message[:i + 1].rjust(visible_chars)  # Construir línea con espacios a la izquierda
                self.send_command("Set DDRAM Address Line 2")
                for char in line2:
                    self.envia_caracter(char)
                sleep(delay)

            # Desplazamiento del mensaje en la línea 2 si es más largo que 16 caracteres
            if len(message) > visible_chars:
                extended_message = message.ljust(len(message) + visible_chars)  # Espacios para desplazamiento
                for i in range(len(extended_message) - visible_chars + 1):
                    # Línea 2: Actualizar el mensaje desplazado
                    window = extended_message[i:i + visible_chars]  # Ventana de desplazamiento
                    self.send_command("Set DDRAM Address Line 2")
                    for char in window:
                        self.envia_caracter(char)

                    # Retardo entre desplazamientos
                    sleep(delay)

    def lcd_clear(self):
        """Limpia el contenido del LCD."""
        self.send_command("Clear Display")
        sleep(0.002)
