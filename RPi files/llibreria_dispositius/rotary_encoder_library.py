import pigpio

class RotaryEncoder:
    def __init__(self, gpio_clk, gpio_dt, gpio_sw, rotation_callback=None, button_callback=None):
        """
        Clase mejorada para manejar un encoder rotatorio.

        Args:
            gpio_clk (int): GPIO pin conectado al CLK del encoder.
            gpio_dt (int): GPIO pin conectado al DT del encoder.
            gpio_sw (int): GPIO pin conectado al SW del encoder (pulsador).
            rotation_callback (func): Función ejecutada al detectar un giro (opcional).
            button_callback (func): Función ejecutada al presionar el botón (opcional).
        """
        self.gpio_clk = gpio_clk
        self.gpio_dt = gpio_dt
        self.gpio_sw = gpio_sw
        self.rotation_callback = rotation_callback
        self.button_callback = button_callback

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("No se pudo conectar a pigpio daemon.")

        # Configuración de los pines
        self.pi.set_mode(self.gpio_clk, pigpio.INPUT)
        self.pi.set_pull_up_down(self.gpio_clk, pigpio.PUD_UP)

        self.pi.set_mode(self.gpio_dt, pigpio.INPUT)
        self.pi.set_pull_up_down(self.gpio_dt, pigpio.PUD_UP)

        self.pi.set_mode(self.gpio_sw, pigpio.INPUT)
        self.pi.set_pull_up_down(self.gpio_sw, pigpio.PUD_UP)

        # Variables internas
        self.last_clk = self.pi.read(self.gpio_clk)
        self.value = 0

        # Registro de callbacks para interrupciones
        self.pi.callback(self.gpio_clk, pigpio.EITHER_EDGE, self._handle_rotation)
        self.pi.callback(self.gpio_sw, pigpio.FALLING_EDGE, self._handle_button)

    def _handle_rotation(self, gpio, level, tick):
        """
        Maneja las interrupciones en CLK para detectar el giro.
        """
        clk_state = self.pi.read(self.gpio_clk)
        dt_state = self.pi.read(self.gpio_dt)

        if clk_state != self.last_clk:  # Cambio detectado en CLK
            if dt_state != clk_state:
                self.value += 1  # Giro horario
                direction = "Clockwise"
            else:
                self.value -= 1  # Giro antihorario
                direction = "Counterclockwise"

            if self.rotation_callback:
                self.rotation_callback(direction)

            self.last_clk = clk_state

    def _handle_button(self, gpio, level, tick):
        """
        Maneja la pulsación del botón.
        """
        if self.button_callback:
            self.button_callback()

    def get_value(self):
        """
        Retorna el valor actual del encoder.
        """
        return self.value
    
    def disable_callbacks(self):
        """
        Desactiva las interrupciones del encoder, eliminando los callbacks asociados.
        """
        self.pi.callback(self.gpio_clk).cancel()
        self.pi.callback(self.gpio_sw).cancel()
        print("Interrupciones desactivadas para el encoder.")

    def stop(self):
        """
        Libera los recursos de pigpio.
        """
        self.pi.stop()

