from time import sleep
from llibreria_dispositius.gpio_manager import get_gpio

#generem les notes establint uns minims i maxims de frecuencia
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

    return notes

NOTES = generate_notes_in_freq_range()

#construiom funcio per extreure les frequencies de les notes que estan en un rang de 2 a 4kz que es on les especificacions del buzzer passiu ens diu que funciona millor
def generate_notes_in_range(note_min, note_max):
    freq_min = NOTES[note_min]
    freq_max = NOTES[note_max]

    # Reintento con manejo explícito del rango de frecuencias
    filtered_notes = {
        note: freq for note, freq in NOTES.items()
        if freq_min <= freq <= freq_max
    }

    return filtered_notes


class Buzzer:
    def __init__(self, buzzer_pin):
        self.buzzer_pin = buzzer_pin
        get_gpio().setup(self.buzzer_pin, get_gpio().OUT)
        self.pwm = None  # PWM se inicializa como None
        self._pwm_active = False


    def play_tone(self, frequency, duration):
        """Reproduce un tono específico durante un tiempo."""
        if not self.pwm:  # Inicializa PWM si no está activo
            self.pwm = get_gpio().PWM(self.buzzer_pin, frequency)
            self.pwm.start(50)  # Ciclo de trabajo al 50%

        if frequency > 0:
            self.pwm.ChangeFrequency(frequency)  # Cambia la frecuencia del tono
        else:
            self.pwm.ChangeDutyCycle(0)  # Silencio: cambia el ciclo de trabajo a 0

        sleep(duration)  # Espera la duración del tono
        self.pwm.ChangeDutyCycle(50)  # Vuelve a preparar el PWM para el siguiente tono


    def play_melody(self, melody):
        """Reproduce una melodía completa."""
        for note, duration in melody:
            frequency = NOTES.get(note, 0)
            self.play_tone(frequency, duration)
        self.stop_pwm()  # Detiene el PWM después de la melodía

    def stop_pwm(self):
        """Detiene el PWM si está activo."""
        if self.pwm and self._pwm_active:
            self.pwm.stop()
            self._pwm_active = False

    def stop(self):
        """Limpia la configuración del GPIO."""
        self.stop_pwm()  # Detiene el PWM si sigue activo
        if self.pwm:
            self.pwm = None
        get_gpio().cleanup()

