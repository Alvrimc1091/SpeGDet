import socket
import threading
import time
import datetime
import zoneinfo
import csv
import pandas as pd

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

df = pd.read_csv("data_low.csv")
print(df.tail())
