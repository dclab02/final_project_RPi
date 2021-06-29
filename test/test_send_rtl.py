import socket

HOST, PORT = "192.168.50.168", 1234
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((HOST, PORT))

path = "./RCSS_ATIS_2.bin"
