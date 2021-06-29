import socket
import time

def bytes_to_bin(b):
    return bin(int.from_bytes(b, byteorder='big'))

HOST, PORT = "192.168.50.168", 1234

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((HOST, PORT))

# while True:
#     data = input()
#     client.send(data.encode())
#     ret = client.recv(1024)
#     print('Server:', ret)

data = b'\xff' + b'\x01' + b'\x11' * 20
client.send(data)
print("sent:", data, bytes_to_bin(data), len(data))

# while True:
# #print("sent:", data, bytes_to_bin(data), len(data))
#     print(f"sent {len(data)}")
#     client.send(data)
#     # time.sleep(1)

ret = client.recv(1500)
print("recv:", ret, bytes_to_bin(ret), len(ret))

client.close()
