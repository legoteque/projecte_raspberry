from time import sleep
from llibreria_dispositius.gpio_manager import get_gpio as GPIO

#generem les notes establint uns minims i maxims de frecuencia utils per al buzzer
def generate_notes_in_freq_range(min_frequency=2100, max_frequency=4800):
    """
    Genera un conjunto de notas reales con frecuencias entre un rango específico.
    Las notas están en formato musical estándar (e.g., C1, A6).
    """
    base_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    c1_frequency = 32.70  # Frecuencia base para C1
    c1_position = 3  # C1 es la cuarta tecla del piano (índice 3 en 0-based)
    notes = {}
    i = 0  # Contador de notas

    while True:
        # Calcular frecuencia actual
        octave = (i + c1_position) // 12
        note = base_notes[(i + c1_position) % 12]
        semitone_offset = i - c1_position  # Distancia en semitonos desde C1
        frequency = c1_frequency * (2 ** (semitone_offset / 12))
        
        # Detener si excede el rango máximo
        if frequency > max_frequency:
            break
        
        # Añadir solo si está dentro del rango mínimo y máximo
        if frequency >= min_frequency:
            notes[f"{note}{octave}"] = round(frequency, 2)
        
        i += 1  # Avanzar al siguiente semitono

    notes["silenci"] = 0  # Agregar "silenci" como frecuencia 0

    return notes

NOTES = generate_notes_in_freq_range()


class Buzzer:
    def __init__(self, buzzer_pin):
        self.buzzer_pin = buzzer_pin
        self.pwm = None  # PWM no está inicializado al comienzo
        self._pwm_active = False  # Indica si PWM está funcionando

        GPIO.setup(self.buzzer_pin, GPIO.OUT)

    def play_tone(self, frequency, duration):
        """Reproduce un tono específico durante un tiempo."""
        if not self.pwm:  # Inicializa PWM si no está activo
            self.pwm = GPIO.PWM(self.buzzer_pin, frequency)
            self.pwm.start(50)  # Ciclo de trabajo al 50%
            self._pwm_active = True

        if frequency > 0:  # Tono válido
            self.pwm.ChangeFrequency(frequency)
            self.pwm.ChangeDutyCycle(50)  # Activa el buzzer al 50%
        else:  # Silencio
            self.pwm.ChangeDutyCycle(0)  # Ciclo de trabajo a 0%

        sleep(duration)

    def play_melody(self, melody):
        """Reproduce una melodía completa."""
        for note, duration in melody:
            frequency = NOTES.get(note, 0)  # Usa 0 si la nota no existe (silencio)
            self.play_tone(frequency, duration)

        self.stop_pwm()  # Detiene el PWM al final de la melodía

    def stop_pwm(self):
        """Detiene el PWM si está activo."""
        if self.pwm and self._pwm_active:
            self.pwm.stop()
            self._pwm_active = False

    def stop(self):
        """Detiene el PWM y elimina el objeto."""
        self.stop_pwm()
        if self.pwm:
            self.pwm = None





