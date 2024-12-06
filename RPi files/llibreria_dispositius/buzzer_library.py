import pigpio
from time import sleep

# Genera les notes musicals dins d'un rang de freqüències
def generate_notes_in_freq_range(min_frequency=2100, max_frequency=4800):
    """
    Genera un conjunt de notes musicals reals amb freqüències dins d'un rang específic.
    Les notes estan en format musical estàndard (ex. C1, A6).
    """
    base_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    c1_frequency = 32.70  # Freqüència base per a C1
    c1_position = 3  # C1 és la quarta tecla del piano (índex 3 en base 0)
    notes = {}
    i = 0  # Comptador de notes

    while True:
        # Calcula la freqüència actual
        octave = (i + c1_position) // 12
        note = base_notes[(i + c1_position) % 12]
        semitone_offset = i - c1_position  # Distància en semitons des de C1
        frequency = c1_frequency * (2 ** (semitone_offset / 12))
        
        # Atura si excedeix el rang màxim
        if frequency > max_frequency:
            break
        
        # Afegeix només si està dins del rang mínim i màxim
        if frequency >= min_frequency:
            notes[f"{note}{octave}"] = round(frequency, 2)
        
        i += 1  # Avança al següent semitò

    notes["silenci"] = 0  # Afegeix "silenci" com a freqüència 0

    return notes

NOTES = generate_notes_in_freq_range()


class Buzzer:
    def __init__(self, buzzer_pin):
        self.buzzer_pin = buzzer_pin
        self.pi = pigpio.pi()  # Inicia la connexió amb el dimoni de pigpio
        if not self.pi.connected:
            raise RuntimeError("No s'ha pogut connectar al dimoni pigpio.")
        self.pi.set_mode(self.buzzer_pin, pigpio.OUTPUT)

    def play_tone(self, frequency, duration):
        """Reprodueix un to específic durant un temps determinat."""
        if frequency > 0:  # To vàlid
            self.pi.hardware_PWM(self.buzzer_pin, int(frequency), 500000)  # Cicle de treball 50% (500000 = 50%)
        else:  # Silenci
            self.pi.hardware_PWM(self.buzzer_pin, 0, 0)  # Atura el PWM

        sleep(duration)

    def play_melody(self, melody):
        """Reprodueix una melodia completa."""
        for note, duration in melody:
            frequency = NOTES.get(note, 0)  # Utilitza 0 si la nota no existeix (silenci)
            self.play_tone(frequency, duration)
        
        self.stop_pwm()  # Atura el PWM al final de la melodia

    def defined_melodies(self, name, duration=.1):
        welcome_melody = [(note, duration) for note in NOTES.keys()]

        if name == "welcome":
            self.play_melody(welcome_melody)

        elif name == "shutdown":
            shutdown_melody = welcome_melody[::-1]
            self.play_melody(shutdown_melody)

    def stop_pwm(self):
        """Atura el PWM"""
        self.pi.hardware_PWM(self.buzzer_pin, 0, 0)  # Atura el PWM

    def stop(self):
        """Atura el PWM i neteja l'estat del buzzer."""
        self.stop_pwm()  # Atura el PWM
        self.pi.set_mode(self.buzzer_pin, pigpio.INPUT)  # Configura el pin com a entrada (neteja el pin GPIO)
        self.pi.stop()  # Finalitza la connexió amb el dimoni pigpio
    

