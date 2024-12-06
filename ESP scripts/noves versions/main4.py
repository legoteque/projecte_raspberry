import network
import socket
import machine
from time import sleep
from sync_time_lib import sync_time

# Configuración de pines
PIN_CONFIG = {
    "RELAY": 5,  # GPIO5 (D1) para encendido/apagado
    "RASPBERRY_STATUS": 4,  # GPIO4 (D2) para estado
}

# Configuración de redes
NETWORKS = [
    {"SSID": "SMART", "PASSWORD": "12345678"},
    {"SSID": "AULA-I32", "PASSWORD": "abc1234abc"},
]

# Plantillas HTML
HTML_TEMPLATES = {
    "home": """
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Estado de la Raspberry Pi</title>
            </head>
            <body>
                <h1>{state}</h1>
                <p>Última actualización: {time}</p>
                <a href="{action_url}"><button>{action_label}</button></a>
            </body>
        </html>
    """,
    "status_change": """
        <html>
            <head>
                <meta charset="UTF-8">
                <title>{title}</title>                
            </head>
            <body>
                <h1>{message}</h1>
                <p>La página se recargará automáticamente</p>
            </body>
        </html>
    """,
    "error": """
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Error</title>
            </head>
            <body>
                <h1>{message}</h1>
            </body>
        </html>
    """,
}


# Conexión a Wi-Fi
def connect_to_network(ssid, password):
    global wlan, ip
    if wlan is None:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
    
    print(f"Intentando conectar a {ssid}...")
    wlan.disconnect()  # Asegúrate de desconectar cualquier conexión previa
    wlan.connect(ssid, password)
    
    for retry in range(10):  # Máximo de 10 intentos
        global ip
        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print(f"Conectado a {ssid}. Dirección IP:", ip)
            return True
        print(f"Intento {retry + 1}/10 fallido para {ssid}.")
        sleep(2)
    
    print(f"No se pudo conectar a {ssid}.")
    return False

def connect_wifi(networks_dic):
    for network in networks_dic:
        if connect_to_network(network["SSID"], network["PASSWORD"]):
            print(f"Conexión exitosa a la red {network['SSID']}.")
            return  # Sal del bucle una vez conectado
    print("No se pudo conectar a ninguna red. Verifica la configuración.")
    #machine.reset()




def simulate_request(host, port, route="/"):
    """Simula una solicitud HTTP al servidor."""
    if not host:
        print("Error: Dirección IP no configurada.")
        return
    try:
        # Crear un socket como cliente
        client_socket = socket.socket()
        client_socket.connect((host, port))
        
        # Construir la solicitud HTTP
        http_request = f"GET {route} HTTP/1.1\r\nHost: {host}\r\n\r\n"
        print("Enviando solicitud:")
        print(http_request)
        
        # Enviar la solicitud al servidor
        client_socket.send(http_request.encode())
        
        # Leer la respuesta del servidor
        response = client_socket.recv(1024).decode()
        print("Respuesta recibida del servidor:")
        print(response)
        
        # Cerrar la conexión
        client_socket.close()
    except OSError as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        client_socket.close()  # Garantiza que el socket se cierre siempre




# Evaluar el estado de la Raspberry Pi
def get_raspberry_state(pin):
    return pin.value() == 1  # True si encendida, False si apagada


# Control del estado de la Raspberry Pi
def toggle_raspberry_state(action, relay_pin):
    """Controla el encendido o apagado de la Raspberry Pi mediante un pulso."""
    print(f"Enviando señal para {action} la Raspberry Pi...")
    relay_pin.value(0)  # Pulso LOW
    sleep(0.5 if action == "encender" else 2.5)  # Duración del pulso
    relay_pin.value(1)  # Volver a HIGH
    print(f"Señal para {action} enviada.")
    return f"{action[0].upper() + action[1:]} la Raspberry Pi, espere un momento..."



# Interrupción para manejar cambios en el estado de la Raspberry Pi
def handle_state_change(raspberry_status_pin):
    global raspberry_state, ip
    # Pequeño debounce en la interrupción para manejar solicitudes no deseadas si se genera un cambio de estado muy rápido (por ejemplo, múltiples flancos en el pin)
    sleep(0.1)  # Debounce
    new_state = raspberry_status_pin.value()
    
    if new_state != raspberry_state:
        raspberry_state = new_state
        print(f"Estado de la Raspberry Pi cambiado: {raspberry_state}")
        # Simular un request a la página raíz
        print(f"Simulando solicitud al servidor en {ip}:80")
        simulate_request(ip, 80, "/")
        #desactivamos la interrupcion
        raspberry_status_pin.irq(handler=None)


# Manejo de solicitudes HTTP
def handle_request(request, raspberry_status_pin, relay_pin):
    if not request:
        return HTML_TEMPLATES["error"].format(message="Solicitud vacía.")
    
    formatted_time = sync_time()

    if "GET / " in request or "GET / HTTP/1.1" in request:
        state = "La Raspberry Pi está ENCENDIDA." if get_raspberry_state(raspberry_status_pin) else "La Raspberry Pi está APAGADA."
        action_url = "/apagar" if get_raspberry_state(raspberry_status_pin) else "/encender"
        action_label = "Apagar Raspberry Pi" if get_raspberry_state(raspberry_status_pin) else "Encender Raspberry Pi"
        return HTML_TEMPLATES["home"].format(state=state, time=formatted_time, action_url=action_url, action_label=action_label)
    elif "/encender" in request:
        # Configuramos interrupción de ascenso en el pin de estado
        raspberry_status_pin.irq(trigger=machine.Pin.IRQ_RISING, handler=handle_state_change)
        message = toggle_raspberry_state("encender", relay_pin)
        return HTML_TEMPLATES["status_change"].format(
            title="Encendiendo...",
            message=message,
        )
    elif "/apagar" in request:
        # Configuramos interrupción de descenso en el pin de estado
        raspberry_status_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_state_change)
        message = toggle_raspberry_state("apagar", relay_pin)
        return HTML_TEMPLATES["status_change"].format(
            title="Apagando...",
            message=message,
        )
    if "GET /favicon.ico" in request:
        return "HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\n\r\n"  # Respuesta para un favicon vacío
    else:
        return HTML_TEMPLATES["error"].format(message="Comando no reconocido.")


# Servidor HTTP
def start_server(raspberry_status_pin, relay_pin):
    global server_socket
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    print("Servidor HTTP en ejecución, esperando conexiones...")
    
    while True:
        try:
            cl, addr = server_socket.accept()
            print("Conexión desde", addr)
            request = cl.recv(1024).decode("utf-8")
            print("Solicitud recibida:", request)
            
            response = handle_request(request, raspberry_status_pin, relay_pin)  # Lógica separada
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + response)
            cl.close()
        except Exception as e:
            print(f"Error manejando una conexión: {e}")





# Limpieza y cierre
def cleanup():
    global server_socket
    global wlan
    print("Cerrando servidor y desconectando Wi-Fi...")
    if server_socket:
        server_socket.close()
    if wlan and wlan.isconnected():
        wlan.disconnect()
        wlan.active(False)
    print("Reiniciando dispositivo...")
    #machine.reset()



# Inicializamos variables globales
wlan = None
server_socket = None
ip = None

connect_wifi(NETWORKS)
sync_time(print_time=True)

# Configurar los pines
relay_pin = machine.Pin(PIN_CONFIG["RELAY"], machine.Pin.OUT)
relay_pin.value(1)  # Estado inicial: HIGH (desconectado)
raspberry_status_pin = machine.Pin(PIN_CONFIG["RASPBERRY_STATUS"], machine.Pin.IN)

raspberry_state = get_raspberry_state(raspberry_status_pin)  # Estado inicial de la Raspberry Pi tambien como variable global

# Main
try:
    # Iniciar el servidor HTTP
    start_server(raspberry_status_pin, relay_pin)

except KeyboardInterrupt:
    print("Ejecución interrumpida por el usuario.")
    cleanup()
except Exception as e:
    print(f"Ha ocurrido un error inesperado: {e}")
    cleanup()

