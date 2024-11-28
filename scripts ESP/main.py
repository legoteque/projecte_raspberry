import network
import socket
import machine
import time
import ntptime

# Configuración de red
SSID = "SMART"
PASSWORD = "12345678"

# Configuración de pines
relay_pin = machine.Pin(5, machine.Pin.OUT)  # GPIO5 (D1) para controlar encendido/apagado
relay_pin.value(1)  # Estado inicial: desconectado (HIGH)
raspberry_status_pin = machine.Pin(4, machine.Pin.IN)  # GPIO4 (D2) para leer estado de la Raspberry

# Conexión a Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    max_retries = 10
    retries = 0
    while not wlan.isconnected() and retries < max_retries:
        print(f"Intentando conectar a WiFi... ({retries + 1}/{max_retries})")
        time.sleep(2)
        retries += 1
    
    if wlan.isconnected():
        print("Conectado a WiFi. Dirección IP:", wlan.ifconfig()[0])
    else:
        print("No se pudo conectar a WiFi. Verifica el SSID/contraseña o la configuración de la red.")
        machine.reset()

# Sincronizar con NTP
def sync_time():
    try:
        print("Sincronizando hora con NTP...")
        ntptime.settime()  # Sincroniza con el servidor NTP predeterminado (pool.ntp.org)
        print("Hora sincronizada correctamente.")
    except Exception as e:
        print(f"Error al sincronizar la hora: {e}")

# Evaluar el estado real de la Raspberry Pi
def get_raspberry_state():
    if raspberry_status_pin.value() == 1:
        return True  # Encendida
    else:
        return False  # Apagada

# Función para encender o apagar la Raspberry Pi
def toggle_raspberry_state(action):
    if action == "encender":
        print("Enviando señal para encender la Raspberry Pi...")
        relay_pin.value(0)  # Pulso LOW
        time.sleep(0.5)     # Mantener LOW durante 0.5 segundos
        relay_pin.value(1)  # Volver a HIGH
        print("Señal de encendido enviada.")
        return "Encendiendo la Raspberry Pi, espere un momento..."
    
    elif action == "apagar":
        print("Enviando señal para apagar la Raspberry Pi...")
        relay_pin.value(0)  # Pulso LOW
        time.sleep(2.5)     # Mantener LOW durante 2.5 segundos
        relay_pin.value(1)  # Volver a HIGH
        print("Señal de apagado enviada.")
        return "Apagando la Raspberry Pi, espere un momento..."
    
    else:
        return "Acción no reconocida."

# Servidor HTTP
def start_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Servidor en ejecución, esperando conexiones...")

    while True:
        cl, addr = s.accept()
        print("Conexión desde", addr)
        request = cl.recv(1024).decode("utf-8")
        print("Solicitud recibida:", request)

        # Hora actual para mostrar en la web
        current_time = time.localtime()
        formatted_time = f"{current_time[3]:02}:{current_time[4]:02}:{current_time[5]:02}"

        # Verificar la página principal
        if "GET / " in request or "GET / HTTP/1.1" in request:
            raspberry_state = get_raspberry_state()  # Leer el estado de la Raspberry Pi
            
            if raspberry_state:
                # Si la Raspberry está encendida
                response = f"""
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Estado de la Raspberry Pi</title>
                    </head>
                    <body>
                        <h1>La Raspberry Pi está ENCENDIDA.</h1>
                        <p>Última actualización: {formatted_time}</p>
                        <a href="/apagar"><button>Apagar Raspberry Pi</button></a>
                    </body>
                </html>
                """
            else:
                # Si la Raspberry está apagada
                response = f"""
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Estado de la Raspberry Pi</title>
                    </head>
                    <body>
                        <h1>La Raspberry Pi está APAGADA.</h1>
                        <p>Última actualización: {formatted_time}</p>
                        <a href="/encender"><button>Encender Raspberry Pi</button></a>
                    </body>
                </html>
                """
        
        # Acciones específicas para encender o apagar
        elif "/encender" in request:
            countdown_time = 23  # Tiempo en segundos para recargar
            message = toggle_raspberry_state("encender")
            response = f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Encendiendo...</title>
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
            """
        
        elif "/apagar" in request:
            countdown_time = 8  # Tiempo en segundos para recargar
            message = toggle_raspberry_state("apagar")
            response = f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Apagando...</title>
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
            """
        
        else:
            response = """
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Error</title>
                </head>
                <body>
                    <h1>Comando no reconocido.</h1>
                </body>
            </html>
            """

        # Enviar la respuesta al cliente
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n" + response)
        cl.close()

# Ejecutar
connect_wifi()
sync_time()
start_server()
