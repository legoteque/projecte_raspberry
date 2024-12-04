import network
import socket
import machine
from time import sleep
from sync_time_lib import sync_time
from wifi import WifiConnection

# Variables globales
wlan = None
server_socket = None

# Configuración de pines
PIN_CONFIG = {
    "RELAY": 5,  # GPIO5 (D1) para encendido/apagado
    "RASPBERRY_STATUS": 4,  # GPIO4 (D2) para estado
}

relay_pin = machine.Pin(PIN_CONFIG["RELAY"], machine.Pin.OUT)
relay_pin.value(1)  # Estado inicial: desconectado (HIGH)
raspberry_status_pin = machine.Pin(PIN_CONFIG["RASPBERRY_STATUS"], machine.Pin.IN)


# Configuración de redes
NETWORKS = [
    {"SSID": "SMART", "PASSWORD": "12345678"},
    {"SSID": "AULA-I32", "PASSWORD": "abc1234abc"},
]

# Conexión a Wi-Fi
def connect_to_network(ssid, password):
    global wlan
    if wlan is None:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
    
    print(f"Intentando conectar a {ssid}...")
    wlan.disconnect()  # Asegúrate de desconectar cualquier conexión previa
    wlan.connect(ssid, password)
    
    for retry in range(10):  # Máximo de 10 intentos
        if wlan.isconnected():
            print(f"Conectado a {ssid}. Dirección IP:", wlan.ifconfig()[0])
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

# Evaluar el estado de la Raspberry Pi
def get_raspberry_state():
    return raspberry_status_pin.value() == 1  # True si encendida, False si apagada

# Control del estado de la Raspberry Pi
def toggle_raspberry_state(action):
    if action == "encender":
        print("Enviando señal para encender la Raspberry Pi...")
        relay_pin.value(0)  # Pulso LOW
        sleep(0.5)
        relay_pin.value(1)  # Volver a HIGH
        print("Señal de encendido enviada.")
        return "Encendiendo la Raspberry Pi, espere un momento..."
    elif action == "apagar":
        print("Enviando señal para apagar la Raspberry Pi...")
        relay_pin.value(0)  # Pulso LOW
        sleep(2.5)
        relay_pin.value(1)  # Volver a HIGH
        print("Señal de apagado enviada.")
        return "Apagando la Raspberry Pi, espere un momento..."
    else:
        return "Acción no reconocida."

# Servidor HTTP
def start_server():
    global server_socket
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    print("Servidor en ejecución, esperando conexiones...")
    
    while True:
        try:
            cl, addr = server_socket.accept()
            print("Conexión desde", addr)
            request = cl.recv(1024).decode("utf-8")
            print("Solicitud recibida:", request)
            
            response = handle_request(request)  # Lógica separada
            cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + response)
            cl.close()
        except Exception as e:
            print(f"Error manejando una conexión: {e}")

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
                            <meta http-equiv="refresh" content="{countdown_time}; url=/" />
                            <script>
                                let countdown = {countdown_time};
                                function updateCountdown() {{
                                    document.getElementById('countdown').innerText = countdown--;
                                    if (countdown < 0) {{
                                        clearInterval(timer);
                                    }}
                                }}
                                const timer = setInterval(updateCountdown, 1000);
                            </script>
                        </head>
                        <body>
                            <h1>{message}</h1>
                            <p>La página se recargará automáticamente en <span id="countdown">{countdown_time}</span> segundos.</p>
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


def handle_request(request):
    if not request:
        return HTML_TEMPLATES["error"].format(message="Solicitud vacía.")
    
    formatted_time = sync_time()

    if "GET / " in request or "GET / HTTP/1.1" in request:
        raspberry_state = get_raspberry_state()
        state = "La Raspberry Pi está ENCENDIDA." if raspberry_state else "La Raspberry Pi está APAGADA."
        action_url = "/apagar" if raspberry_state else "/encender"
        action_label = "Apagar Raspberry Pi" if raspberry_state else "Encender Raspberry Pi"
        return HTML_TEMPLATES["home"].format(state=state, time=formatted_time, action_url=action_url, action_label=action_label)
    
    elif "/encender" in request:
        message = toggle_raspberry_state("encender")
        return HTML_TEMPLATES["status_change"].format(
            title="Encendiendo...",
            countdown_time=23,
            message=message,
        )
    
    elif "/apagar" in request:
        message = toggle_raspberry_state("apagar")
        return HTML_TEMPLATES["status_change"].format(
            title="Apagando...",
            countdown_time=8,
            message=message,
        )
    
    else:
        return HTML_TEMPLATES["error"].format(message="Comando no reconocido.")


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

# Main

wifi = WifiConnection(NETWORKS)
sync_time(print_time=True)

try:
    start_server()
except KeyboardInterrupt:
    print("Ejecución interrumpida por el usuario.")
    cleanup()
except Exception as e:
    print(f"Ha ocurrido un error inesperado: {e}")
    cleanup()