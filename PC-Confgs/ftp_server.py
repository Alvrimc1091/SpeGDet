# Script in ~/Documents/Workspace/Granos/FTP/ftp_server.py (logs in same folder as /log_ftpserver.log)

import logging
from datetime import datetime
import pytz
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Set up logging
logging.basicConfig(filename='/home/alvaro/Documents/Workspace/Granos/FTP/log_ftpserver.log',  # Path to the log file
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# Custom FTP handler with logging and Santiago timezone
class LoggingFTPHandler(FTPHandler):
    def log_with_timestamp(self, message):
        # Define Santiago, Chile timezone
        santiago_tz = pytz.timezone('America/Santiago')
        timestamp = datetime.now(santiago_tz).strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - {message}"
        logger.info(log_message)
        print(log_message)  # Also print the message to the console

    def on_connect(self):
        self.log_with_timestamp(f"Connection established from {self.remote_ip}:{self.remote_port}")

    def on_disconnect(self):
        self.log_with_timestamp(f"Connection closed from {self.remote_ip}:{self.remote_port}")

    def on_login(self, username):
        self.log_with_timestamp(f"User '{username}' logged in from {self.remote_ip}:{self.remote_port}")

    def on_login_failed(self, username, password):
        self.log_with_timestamp(f"Failed login attempt with username '{username}' from {self.remote_ip}:{self.remote_port}")

    def on_logout(self, username):
        self.log_with_timestamp(f"User '{username}' logged out from {self.remote_ip}:{self.remote_port}")

    def on_file_sent(self, file):
        self.log_with_timestamp(f"File sent: {file}")

    def on_file_received(self, file):
        self.log_with_timestamp(f"File received: {file}")

    def on_incomplete_file_sent(self, file):
        self.log_with_timestamp(f"File transfer incomplete (sent): {file}")

    def on_incomplete_file_received(self, file):
        self.log_with_timestamp(f"File transfer incomplete (received): {file}")

    def on_mkd(self, path):
        self.log_with_timestamp(f"Directory created: {path}")

    def on_rmd(self, path):
        self.log_with_timestamp(f"Directory removed: {path}")

    def on_dele(self, path):
        self.log_with_timestamp(f"File deleted: {path}")

    def on_cwd(self, path):
        self.log_with_timestamp(f"Changed directory to: {path}")

# Set up user authorization
authorizer = DummyAuthorizer()
authorizer.add_user("leia", "qwerty", "/home/alvaro/Documents/Workspace/Granos/FTP/Data_leia", perm="elradfmw")
authorizer.add_user("luke", "qwerty", "/home/alvaro/Documents/Workspace/Granos/FTP/Data_luke", perm="elradfmw")

authorizer.add_anonymous("/home/alvaro/Documents/Workspace/Granos/FTP", perm="elradfmw")


# Set up the FTP handler with logging
handler = LoggingFTPHandler
handler.authorizer = authorizer

# Define the server's IP and port
server = FTPServer(("0.0.0.0", 2121), handler)

# Start the server
server.serve_forever()
