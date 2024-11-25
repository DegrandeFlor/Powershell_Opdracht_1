Maak een Python script om een Shelly Smart Plug te configureren na een factory default.
Na de default heeft de plug altijd het IP adres 192.168.33.1 en fungeert als AP met een vast gestructureerde SSID waar het MAC adres is in verwerkt.

Je vindt de mosterd via https://shelly-api-docs.shelly.cloud/Links to an external site..

Zorg dat volgende zaken geconfigureerd zijn:

Stel de naam van de plug in op "<familienaam>-<voornaam>-Outlet1". /
Zorg als het toestel herstart de schakelaar uit staat. /
Schakel alle LEDs uit. /
Configureer MQTT, broker 172.23.83.254, subtopic to publish on: "<familienaam>-<voornaam>-Outlet1". /
Schakel alle niet-gebruikte services uit. 
Zet de maximum toegelaten belasting op 2200W. /
Configureer de Wifi zodat hij met de SSID "Howest-IoT" verbindt.
Zorg dat je via de argumenten van de script de naam van de smart plug kunt instellen en de cloudverbinding kunt aan- of afzetten (default uit).