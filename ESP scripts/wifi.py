import network
from time import sleep

class WifiConnection:
    def __init__(self, networks, retries=10, delay=3):
        """
        Inicializa el objeto y conecta automáticamente a una red predefinida.

        Args:
            networks (list): Lista de diccionarios con SSID y PASSWORD.
            retries (int): Número de intentos de conexión por red.
            delay (int): Tiempo entre intentos de conexión en segundos.
        """
        self._wlan = network.WLAN(network.STA_IF)
        self._wlan.active(True)
        self._networks = networks
        self._retries = retries
        self._delay = delay

        # Inicia el proceso de conexión automáticamente
        self._connect()

    def disconnect(self):
        """
        Desconecta de la red Wi-Fi actual.
        """
        if self._wlan.isconnected():
            self._wlan.disconnect()
            print("Desconectado de la red Wi-Fi.")
        else:
            print("No hay ninguna red conectada.")

    def _scan_networks(self):
        """
        Escanea y devuelve una lista de SSIDs visibles.
        """
        networks = self._wlan.scan()  # Escanea redes disponibles
        visible_ssids = [net[0].decode() for net in networks]  # Extrae SSIDs visibles
        print(f"Redes visibles: {visible_ssids}")
        return visible_ssids

    def _connect_to_network(self, ssid, password):
        """
        Intenta conectar a una red Wi-Fi específica.

        Args:
            ssid (str): Nombre de la red Wi-Fi.
            password (str): Contraseña de la red Wi-Fi.

        Returns:
            bool: True si se conecta exitosamente, False en caso contrario.
        """
        if self._wlan.isconnected():
            self._wlan.disconnect()
            sleep(1)

        print(f"Intentando conectar a {ssid}...")
        self._wlan.connect(ssid, password)

        for retry in range(self._retries):
            if self._wlan.isconnected():
                ip = self._wlan.ifconfig()[0]
                print(f"Conectado a {ssid}. Dirección IP: {ip}")
                return True
            print(f"Intento {retry + 1}/{self._retries} fallido para {ssid}.")
            sleep(self._delay)

        print(f"No se pudo conectar a {ssid}.")
        return False

    def _connect(self):
        """
        Gestiona la conexión a las redes predefinidas, priorizando visibles.
        """
        visible_ssids = self._scan_networks()

        # Redes visibles que están en la lista predefinida
        prioritized_networks = [net for net in self._networks if net["SSID"] in visible_ssids]
        # Redes no visibles (resto de la lista)
        remaining_networks = [net for net in self._networks if net["SSID"] not in visible_ssids]

        print("Intentando conectar a redes visibles...")
        for network in prioritized_networks:
            if self._connect_to_network(network["SSID"], network["PASSWORD"]):
                print(f"Conexión exitosa a la red visible {network['SSID']}.")
                return True

        print("No coincide ninguna red con las visibles. Intentando todas las redes en orden...")
        for network in remaining_networks:
            if self._connect_to_network(network["SSID"], network["PASSWORD"]):
                print(f"Conexión exitosa a la red {network['SSID']}.")
                return True

        print("No se pudo conectar a ninguna red.")

