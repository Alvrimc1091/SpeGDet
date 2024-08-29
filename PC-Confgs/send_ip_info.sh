# Script running in boot in /usr/local/bin/send_ip_info.sh 
#(log in /var/log/vpn_connection_log.txt and /var/log/vpn_ip_log.txt)

#!/bin/bash

sleep 2

# Configuraciones
EMAIL_RECIPIENTS="aimc2918@hotmail.com, example2@example.com"
EMAIL_SUBJECT="Direcciones IP después de la conexión VPN de PC Gradian"
LOG_FILE="/var/log/vpn_ip_log.txt"
log_filevpn="/var/log/vpn_connection_log.txt"
TIMESTAMP=$(TZ="America/Santiago" date '+%Y-%m-%d %H:%M:%S')

# Obtener direcciones IP
#IP_ETH0=$(ip -4 addr show enp2s0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
#IP_WLAN0=$(ip -4 addr show wlp0s20f3 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
#IP_VPN=$(ip -4 addr show tun | grep -oP '(?<=inet\s)\d+(\.\d+){3}')

# Capturar las direcciones IP usando hostname -I
ips=$(hostname -I)

# Separar las IPs en un array
IFS=' ' read -r -a ip_array <<< "$ips"

# Asignar IPs a variables
wlan0_ip=${ip_array[0]} # Primer IP en la lista
eth0_ip=${ip_array[1]}  # Segunda IP en la lista
vpn_ip=${ip_array[2]}   # Tercer IP en la lista

# Construir el mensaje
MESSAGE="Conexión VPN establecida en $TIMESTAMP.\n
Direcciones IP:
  - wlan0: ${wlan0_ip:-"No disponible"}
  - eth0: ${eth0_ip:-"No disponible"}
  - vpn: ${vpn_ip:-"No disponible"}\n"

#MESSAGE+="Direcciones IP:\n"
#[ -n "$IP_ETH0" ] && MESSAGE+="  - eth0: $IP_ETH0\n"
#[ -n "$IP_WLAN0" ] && MESSAGE+="  - wlan0: $IP_WLAN0\n"
#[ -n "$IP_VPN" ] && MESSAGE+="  - vpn: $IP_VPN\n"

# Guardar en el log
echo -e "$MESSAGE" >> $LOG_FILE

# Intentar enviar el correo
echo -e "$MESSAGE" | mail -s "$EMAIL_SUBJECT" $EMAIL_RECIPIENTS
echo "$TIMESTAMP - Direcciones IP enviadas a $EMAIL_RECIPIENTS" >> "$log_filevpn"

if [ $? -ne 0 ]; then
    echo "$TIMESTAMP - Error al enviar correo: falta de conexión." >> $LOG_FILE
    echo "$TIMESTAMP - Error al enviar correo con direcciones IP.\n
          Verifique /var/log/vpn_ip_log.txt." >> "$log_filevpn"
    # Aquí puedes añadir un reintento o cualquier otra acción
fi
