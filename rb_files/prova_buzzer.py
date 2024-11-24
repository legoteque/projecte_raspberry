from llibreria_dispositius.buzzer_library import Buzzer, generate_notes_in_freq_range
from llibreria_dispositius.gpio_manager import gpio_setmode, gpio_cleanup
from time import sleep

gpio_setmode("BCM")

#generem melodies agafant totes les notes(frequencies) que interpreta be (parametres per defecte) i amb durada determinada
notes_dic = generate_notes_in_freq_range()
duration = .1
#la melodia es una llista de tuples amb el format (nota, durada), ascendent o descendent
welcome_melody = [(note, duration) for note in notes_dic.keys()]
shutdown_melody = welcome_melody[::-1]

pin_buzzer = 22

try:
    buzzer = Buzzer(pin_buzzer)  # Pin GPIO 22
    buzzer.play_melody(welcome_melody)
    buzzer.play_melody(shutdown_melody)
    
finally:
    #elimina l'objecte
    buzzer.stop()
    #Allibera el pin GPIO asociat al PWM, tornant-lo al seu estat inicial (generalment d'alta impedancia o entrada).
    gpio_cleanup(pins_l=[pin_buzzer])