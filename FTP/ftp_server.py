from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Set up user authorization
authorizer = DummyAuthorizer()
authorizer.add_user("aimc", "qwerty", "/home/pi/SpeGDet/FTP", perm="elradfmw")  # Modify the path as needed
authorizer.add_anonymous("/home/pi/SpeGDet/FTP", perm="elradfmw")  # Allow anonymous access

# Set up the FTP handler
handler = FTPHandler
handler.authorizer = authorizer

# Define the server's IP and port
server = FTPServer(("192.168.0.50", 2121), handler)

# Start the server
server.serve_forever()
