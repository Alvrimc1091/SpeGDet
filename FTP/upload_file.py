from ftplib import FTP

# FTP server details
ftp_server = "192.168.0.102"
port = 2121
username = "aimc"
password = "qwerty"
filename = "photofile.txt"  # File to upload
remote_path = "photofile.txt"  # Path on the FTP server

# Connect to the FTP server
ftp = FTP()
ftp.connect(ftp_server, port)
ftp.login(user=username, passwd=password)

# Upload the file
with open(filename, 'rb') as file:
    ftp.storbinary(f'STOR {remote_path}', file)

print(f"Uploaded {filename} to {remote_path}")

# Close the connection
ftp.quit()
