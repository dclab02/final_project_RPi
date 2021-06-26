import os, sys
import socket
import time

def bytes_to_bin(b):
    return bin(int.from_bytes(b, byteorder='big'))

IQ_FILE_PATH = ''

HOST, PORT = "192.168.50.168", 1234

if len(sys.argv) > 1:
    IQ_FILE_PATH = sys.argv[1]

with open(IQ_FILE_PATH, 'rb') as f:
    iq_data = f.read()

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((HOST, PORT))

size = 1024
delay = 1 # us
for i in range(0, len(iq_data), 1024):
    client.send(b'\xaa' + iq_data[i:i+size])
    print(f"{size} of iq_data sent")
    time.sleep(delay / 1000000.0)

print(f"{len(iq_data)} sent")
print(f"last byte = {bin(iq_data[-1])}")

client.close()