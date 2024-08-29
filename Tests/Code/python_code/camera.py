# # https://picamera.readthedocs.io/en/release-1.13/recipes1.html

# from time import sleep
# from picamera import PiCamera
# from io import BytesIO

# # Capturing to a file
# camera = PiCamera()
# camera.resolution = (1024, 768)
# camera.start_preview()
# # Camera warm-up time
# sleep(2)
# camera.capture('foo.jpg')

# # Capturing to a stream
# # Create an in-memory stream
# my_stream = BytesIO()
# camera = PiCamera()
# camera.start_preview()
# # Camera warm-up time
# sleep(2)
# camera.capture(my_stream, 'jpeg')

# # Explicitly open a new file called my_image.jpg
# my_file = open('my_image.jpg', 'wb')
# camera = PiCamera()
# camera.start_preview()
# sleep(2)
# camera.capture(my_file)
# # At this point my_file.flush() has been called, but the file has
# # not yet been closed
# my_file.close()

# Script to live stream on a webpage
# Go to http://<your-pi-address>:8000/
# In some cases http://192.168.0.50:8000/

import io
import logging
import socketserver
from http import server
from gpiozero import LED
from threading import Condition


from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

led_array = LED(17)

# HTML page for the MJPEG streaming demo
PAGE = """\
<html>
<head>
<title>RaspberryTips Pi Cam Stream</title>
</head>
<body>
<h1>Raspberry Tips Pi Camera Live Stream Demo</h1>
<img src="stream.mjpg" width="640" height="640" />
</body>
</html>
"""

# Class to handle streaming output
class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

# Class to handle HTTP requests
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Redirect root path to index.html
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            # Serve the HTML page
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            # Set up MJPEG streaming
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            # Handle 404 Not Found
            self.send_error(404)
            self.end_headers()

# Class to handle streaming server
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# Create Picamera2 instance and configure it
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 640)}))
output = StreamingOutput()
picam2.start_recording(JpegEncoder(), FileOutput(output))

try:
    # Set up and start the streaming server
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    led_array.on()
    server.serve_forever()
finally:
    # Stop recording when the script is interrupted
    picam2.stop_recording()
    led_array.off()
