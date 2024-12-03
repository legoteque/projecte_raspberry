from llibreria_dispositius.buzzer_library import Buzzer, generate_notes_in_freq_range

# Generem melodies utilitzant les notes disponibles (ascendent i descendent)
notes_dic = generate_notes_in_freq_range()
duration = 0.1
welcome_melody = [(note, duration) for note in notes_dic.keys()]
shutdown_melody = welcome_melody[::-1]

pin_buzzer = 22  # Canvia al GPIO on has connectat el buzzer

try:
    buzzer = Buzzer(pin_buzzer)  # Inicialitza el buzzer al pin GPIO 22
    print("Reproduint melodia de benvinguda...")
    buzzer.play_melody(welcome_melody)

    print("Reproduint melodia de tancament...")
    buzzer.play_melody(shutdown_melody)

finally:
    print("Neteja de recursos...")
    buzzer.stop()
