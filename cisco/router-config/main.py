import csv

def generate_cisco_config(csv_file, output_file):
    # Open het CSV-bestand
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')

        # Lijst om configuratieopdrachten op te slaan
        config_lines = []

        for row in reader:
            network = row['network']
            interface = row['interface']
            description = row['description']
            vlan = row['vlan']
            ip_address = row['ipaddress']
            subnetmask = row['subnetmask']
            default_gateway = row.get('defaultgateway', '')

            # Interfaceconfiguratie
            if interface:
                config_lines.append(f"interface {interface}")
                if description:
                    config_lines.append(f" description {description}")
                if vlan and int(vlan) != 0:
                    config_lines.append(f" encapsulation dot1Q {vlan}")
                if ip_address:
                    if ip_address.lower() == 'dhcp':
                        config_lines.append(" ip address dhcp")
                    else:
                        config_lines.append(f" ip address {ip_address} {subnetmask}")
                config_lines.append(" no shutdown")
                config_lines.append(" exit")

            # VLAN-configuratie (indien VLAN is gespecificeerd zonder interface)
            if not interface and vlan and int(vlan) != 0:
                config_lines.append(f"vlan {vlan}")
                if description:
                    config_lines.append(f" name {description}")
                config_lines.append(" exit")
            
            # NAT-configuratie voor WAN- en LAN-netwerken
            if network.lower() == 'wan' and interface:
                config_lines.append(f"interface {interface}")
                config_lines.append(" ip nat outside")
                config_lines.append(" exit")
            elif network.lower() == 'lan' and interface:
                config_lines.append(f"interface {interface}")
                config_lines.append(" ip nat inside")
                config_lines.append(" exit")
            
            # Statische route toevoegen (indien default gateway is gespecificeerd)
            if default_gateway and ip_address and subnetmask:
                network_address = f"{ip_address}/{subnetmask}"
                config_lines.append(f"ip route {network_address} {default_gateway}")

        # Access-list configuratie voor NAT-overload
        config_lines.append("access-list 1 permit any")
        config_lines.append("ip nat inside source list 1 interface gi0/0 overload")
        
        # Schrijf naar het uitvoerbestand
        with open(output_file, 'w') as output:
            output.write("\n".join(config_lines))

    print(f"Configuratie gegenereerd en opgeslagen in {output_file}")

# Pad naar CSV-bestand en uitvoerbestand
csv_file = "config.csv"  # Vervang door je eigen CSV-bestand
output_file = "cisco_config.txt"

# Configuratie genereren
generate_cisco_config(csv_file, output_file)
