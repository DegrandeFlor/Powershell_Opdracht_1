import csv
import paramiko
import time
import tftpy
import threading

def configure_switch(csv_file):
    # Lees het CSV-bestand
    with open(csv_file, mode="r") as file:
        csv_reader = csv.DictReader(file, delimiter=";")
        data = list(csv_reader)
    # check if every row has an ip address and netmask
    for row in data:
        if row["IP Address"] != "":
            ip_routing = True
            break
        else:
            ip_routing = False

    for row in data:
        vlan = row["Vlan"]
        description = row["Description"]
        ip_address = row["IP Address"]
        netmask = row["Netmask"]
        switch_ip = row["Switch"]
        ports = row["Ports"]

        # Verbind met de switch
        switch_host = "192.168.0."+switch_ip  # Pas aan naar je switch IP
        username = "flor"
        password = "flor"  # Pas aan naar je wachtwoord
        tftp_server_ip = "192.168.0.100"  # Pas aan naar je TFTP server IP

        try:
            # Stel SSH-client en transportopties in
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=switch_host,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
            )

            # Open een shell
            chan = ssh.invoke_shell()
            def send_command(command):
                """Verstuur een commando via de shell en wacht op output."""
                chan.send(command + "\n")
                while not chan.recv_ready():
                    pass
                return chan.recv(65535).decode("utf-8")

            # Configureer VLAN
            send_command("ena")
            send_command("conf t")
            send_command("vtp mode transparent")
            send_command(f"vlan {vlan}")
            send_command(f"name {description}")

            # Configureer Layer-3 interface (indien van toepassing)
            if ip_address != "" and netmask != "":
                send_command(f"interface vlan {vlan}")
                send_command(f"description {description}")
                send_command(f"ip address {ip_address} {netmask}")
                send_command("no shutdown")
            
            # Layer-2 interface configuratie
            if ip_address == "" and netmask == "":
                send_command(f"interface vlan {vlan}")
                send_command(f"description {description}")
                send_command("no shutdown")

            # Configureer poorten
            if ports:
                if "-" in ports:  # Controleer of het een bereik is
                    start_port, end_port = map(int, ports.split("-"))
                    for port in range(start_port, end_port + 1):
                        print(port)
                        interface = f"FastEthernet0/{port}"
                        send_command(f"interface {interface}")
                        send_command("switchport mode access")
                        send_command(f"switchport access vlan {vlan}")
                        send_command("no shutdown")
                        time.sleep(0.2)
                else:  # Anders is het een enkele poort
                    print(ports)
                    interface = f"FastEthernet0/{ports}"
                    send_command(f"interface {interface}")
                    send_command("switchport mode access")
                    send_command(f"switchport access vlan {vlan}")
                    send_command("no shutdown")
                    time.sleep(0.2)
            
            if "trunk" in description.lower() or "uplink" in description.lower():
                send_command("interface range FastEthernet0/1 - 24")
                send_command("switchport mode trunk")
                if vlan:
                    send_command(f"switchport trunk allowed vlan {vlan}")
            
            if ip_routing == True:
                send_command("conf t")
                send_command("ip routing")

            # Configuratie opslaan
            send_command("write memory")
            send_command("copy run start | noconfirm")
            print(f"Configuratie voltooid voor switch {switch_ip}, VLAN {vlan}")

        except Exception as e:
            print(f"Fout bij verbinden met switch {switch_ip}: {e}")

        finally:
            ssh.close()
    
    tftp_server = start_tftp_server("C:/configs")
    # time.sleep(10)
    download_config()

# # Start TFTP server en download config van switch
# Function to start TFTP server
def start_tftp_server(tftp_root):
    server = tftpy.TftpServer(tftp_root)
    server_thread = threading.Thread(target=server.listen, kwargs={'listenip': '192.168.0.100', 'listenport': 69})
    server_thread.daemon = True
    server_thread.start()
    
    return server

def download_config():
    # Verbind met de switch
    switch_host = "192.168.0.10" # Pas aan naar je switch IP
    switch_ip = switch_host
    username = "flor"
    password = "flor"  # Pas aan naar je wachtwoord
    tftp_server_ip = "192.168.0.100"  # Pas aan naar je TFTP server IP
    tftp_filename = f"switch{switch_ip}.cfg"

    try:
        # Stel SSH-client en transportopties in
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=switch_host,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
        )
        def send_command(command):
            """Verstuur een commando via de shell en wacht op output."""
            chan.send(command + "\n")
            while not chan.recv_ready():
                pass
            return chan.recv(65535).decode("utf-8")
        # Open een shell
        chan = ssh.invoke_shell()
        send_command(f"copy startup-config tftp://{tftp_server_ip}")
        send_command(f"{tftp_server_ip}")
        send_command(f"{tftp_filename}")
        time.sleep(2)
        print(f"Configuratie gedownload van switch {switch_ip}")
    
    except Exception as e:
        print(f"Fout bij verbinden met switch {switch_ip}: {e}")
    
    finally:
        ssh.close()

# Test het script
if __name__ == "__main__":
    configure_switch("config2.csv")
