import subprocess
import re
import argparse
import requests
import json
import time
import os

def scan_networks_windows():
    """
    Scant beschikbare WiFi-netwerken op een Windows-machine en retourneert een lijst van SSID's.
    """
    try:
        print("Scannen naar beschikbare WiFi-netwerken...")
        result = subprocess.run(["netsh", "wlan", "show", "network", "mode=bssid"],
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Fout bij het scannen: {result.stderr}")
            return []

        networks = []
        for line in result.stdout.splitlines():
            match = re.search(r"SSID\s\d+\s*:\s(.+)", line)
            if match:
                networks.append(match.group(1).strip())

        print(f"Gevonden netwerken: {networks}")
        return networks
    except FileNotFoundError:
        print("Het commando 'netsh' is niet gevonden. Zorg ervoor dat je dit script op Windows draait.")
        return []


def find_shelly_network(last_four):
    """
    Zoekt naar een netwerk waarvan de SSID eindigt op de laatste vier cijfers van het MAC-adres.
    """
    networks = scan_networks_windows()
    shelly_ssid = None
    for network in networks:
        if network.endswith(last_four.upper()):
            shelly_ssid = network
            break

    if shelly_ssid:
        print(f"Shelly netwerk gevonden: {shelly_ssid}")
        return shelly_ssid
    else:
        print(f"Geen Shelly netwerk gevonden dat eindigt op '{last_four}'.")
        return None


def connect_to_network(ssid):
    """
    Verbindt met een WiFi-netwerk op Windows.
    """
    print(f"Proberen verbinding te maken met netwerk: {ssid}...")
    try:
        result = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Succesvol verbonden met {ssid}!")
            return True
        else:
            print(f"Fout bij het verbinden: {result.stderr}")
            return False
    except FileNotFoundError:
        print("Het commando 'netsh' is niet gevonden. Zorg ervoor dat je dit script op Windows draait.")
        return False

def configure_shelly(ip, name, enable_cloud):
    max_power = 2200
    default_state="off"
    led_status_disable="true"
    mqtt_enable = "true"
    mqtt_server = "172.23.83.254:1883"
    topic = "Degrande-Flor-Outlets2"
    wifi_ap_enabled = "false"
    wifi_sta_enabled = True
    wifi_ip_method = "dhcp"
    ssid="Howest-IoT"
    # read password from file
    with open("password.txt", "r") as file:
        password = file.read()


    """
    Configureert een Shelly Smart Plug met de gegeven naam en cloudinstellingen.
    """
    print(f"Configuratie van Shelly Smart Plug op IP {ip} met naam '{name}' en cloud {'ingeschakeld' if enable_cloud else 'uitgeschakeld'}...")
    # Implementeer configuratie hier
    requests.post("http://192.168.33.1/settings/relay/0", data=f'name={name}')
    requests.post("http://192.168.33.1/settings/relay/0", data=f'max_power={max_power}')
    requests.post("http://192.168.33.1/settings/relay/0", data=f'default_state={default_state}')
    requests.post("http://192.168.33.1/settings/", data=f'led_status_disable={led_status_disable}')
    time.sleep(0.5)
    print("Settings 1 finished")
    requests.post("http://192.168.33.1/settings/mqtt", data=f'mqtt_enable={mqtt_enable}')
    requests.post("http://192.168.33.1/settings/mqtt", data=f'mqtt_server={mqtt_server}')
    requests.post("http://192.168.33.1/settings/mqtt", data=f'mqtt_id={topic}')
    print("MQTT settings finished")
    time.sleep(1)

    # disable unused services
    requests.post("http://192.168.33.1/settings/coiot", data=f'enabled=false')
    requests.post("http://192.168.33.1/settings/sntp", data=f'enabled=false')

    json = {"ssid": ssid, "key": password, "ipv4_method": wifi_ip_method, "enabled": wifi_sta_enabled}

    requests.post("http://192.168.33.1/settings/sta", data=json)

    print("Configuratie voltooid!")
    

if __name__ == "__main__":
    # Vraag de laatste vier cijfers van het MAC-adres op
    parser = argparse.ArgumentParser(description="Configureer een Shelly Smart Plug.")
    parser.add_argument("plug_name", type=str, help="De naam van de plug, bv. '<familienaam>-<voornaam>-Outlet1'")
    parser.add_argument("--enable_cloud", action="store_true", help="Schakel cloudverbinding in (standaard uit)")

    args = parser.parse_args()

    # Standaard IP van een Shelly Smart Plug na factory reset
    last_four = input("Geef de laatste vier cijfers van het MAC-adres op (bv. '1A2B'): ").strip()
    if len(last_four) != 4 or not re.match(r"^[0-9A-Fa-f]{4}$", last_four):
        print("Ongeldige invoer. Voer exact vier hexadecimale cijfers in (bijv. '1A2B').")
    else:
        # Zoek en verbind met het Shelly-netwerk
        shelly_ssid = find_shelly_network(last_four)
        if shelly_ssid:
            result_wifi = connect_to_network(shelly_ssid)
            if result_wifi == True:
                configure_shelly("192.168.33.1", args.plug_name, args.enable_cloud)
            else:
                print("Wifi not connected")
                exit
        