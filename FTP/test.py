import ftplib

# FTP server details
ftp_server = "127.0.0.1"
username = "aimc"
password = "qwerty"
port = 2121

# Connect to the FTP server
ftp = ftplib.FTP()
ftp.connect(ftp_server, port)
ftp.login(user=username, passwd=password)

# List files in the root directory
ftp.retrlines('LIST')

# Close the connection
ftp.quit()
