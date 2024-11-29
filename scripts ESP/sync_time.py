import ntptime
import time

#Formateamos con la hora en españa
def local_formatted_time(current_time):
    year = current_time[0]
    month = current_time[1]
    day = current_time[2]
    hour = current_time[3]
    minute = current_time[4]
    second = current_time[5]

    # España está en UTC+1 en invierno y UTC+2 en verano
    offset = 1 * 3600  # UTC+1 en segundos

    # Verificar si estamos en horario de verano
    if month > 3 and month < 10:  # Entre abril y septiembre
        offset += 3600  # UTC+2
    elif month == 3 and is_last_sunday_of_month(year, month, day) and hour >= 2:
        offset += 3600  # Último domingo de marzo, después de las 2:00
    elif month == 10 and is_last_sunday_of_month(year, month, day) and hour < 2:
        offset += 3600  # Último domingo de octubre, antes de las 2:00

    # Ajustar la hora local
    local_time = time.localtime(time.time() + offset)
    local_year = local_time[0]
    local_month = local_time[1]
    local_day = local_time[2]
    local_hour = local_time[3]
    local_minute = local_time[4]
    local_second = local_time[5]

    # Formatear manualmente la hora
    formatted_time = f"{local_year:04d}-{local_month:02d}-{local_day:02d} {local_hour:02d}:{local_minute:02d}:{local_second:02d}"
    return formatted_time


#Sincronización horaria        
def last_day_of_month(year, month):
    """Devuelve el último día del mes."""
    if month == 12:  # Si es diciembre, pasamos al siguiente año y mes 1
        year += 1
        month = 1
    else:
        month += 1  # Pasamos al siguiente mes
    # Restamos un día al primer día del siguiente mes para obtener el último día del mes actual
    return time.localtime(time.mktime((year, month, 1, 0, 0, 0, 0, 0, -1)) - 86400)[2]

def is_last_sunday_of_month(year, month, day):
    """Devuelve True si la fecha especificada es el último domingo del mes."""
    last_day = last_day_of_month(year, month)
    return time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0, -1)))[6] == 6 and (last_day - day) < 7

def sync_time(print_time=False):
    try:
        ntptime.settime()  # Sincroniza con UTC

        # Obtener la hora UTC actual
        current_time = time.localtime()
        formatted_time = local_formatted_time(current_time)
        
    except Exception as e:
        print(f"Error al sincronizar la hora: {e}")
        
    if print_time: 
        print("Hora sincronizada correctamente.")
        print("Hora local:", formatted_time)
    else:
        return formatted_time
