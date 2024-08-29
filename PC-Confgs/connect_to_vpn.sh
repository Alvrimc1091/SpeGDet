# Script running in /usr/local/bin/connect_to_vpn.sh
# (log in /var/log/vpn_connection_log.txt)
#!/bin/bash

# Definir la zona horaria de Santiago de Chile
TZ="America/Santiago"

# Obtener la fecha y hora actual en Santiago de Chile
current_time=$(date "+%Y-%m-%d %H:%M:%S")

# Archivo de log
log_file="/var/log/vpn_connection_log.txt"

VPN_SERVER="vpn.uchile.cl"
USERNAME="username"

# Conectar a la VPN
echo "Conectando a la VPN..."

echo "pass" | openconnect --user=$USERNAME --passwd-on-stdin $VPN_SERVER

# Verificar si la conexión VPN se ha establecido correctamente
if [ $? -eq 0 ]; then
    connection_message="Conexión VPN establecida en $current_time."
else
    connection_message="Falló la conexión VPN en $current_time."
fi

# Guardar el mensaje de conexión VPN en el log
echo "$current_time - $connection_message" >> "$log_file"

# Ejecutar script para enviar y guardar direcciones IP
/usr/local/bin/send_ip_info.sh
