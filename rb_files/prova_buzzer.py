from llibreria_dispositius.buzzer_library import Buzzer, generate_notes_in_freq_range
from llibreria_dispositius.gpio_manager import gpio_setmode, gpio_cleanup
from time import sleep

gpio_setmode("BCM")

notes_dic = generate_notes_in_freq_range()
welcome_melody = [(note, .1) for note in notes_dic.keys()]
shutdown_melody = welcome_melody[::-1]

try:
    buzzer = Buzzer(22)  # Pin GPIO 18
    buzzer.play_melody(welcome_melody)
    buzzer.play_melody(shutdown_melody)

    
finally:
    buzzer.stop()
    gpio_cleanup()