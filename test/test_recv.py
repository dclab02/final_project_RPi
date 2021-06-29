import socket
import wave
import pyaudio

p = pyaudio.PyAudio()
# open stream (2)
stream = p.open(format=pyaudio.paInt16,
    channels=1,
    rate=44100,
    frames_per_buffer=10157184,
    output=True)

HOST, PORT = "192.168.50.82", 8080

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))


counter = 0
data_frame = b''
while True:
    ret = server.recvfrom(1024)
    if counter < 512:
        data = ret[0][1:]
        data_frame += data
        counter += 1
        if counter >= 512:
            counter = 0
            stream.write(data_frame)
            print("write data_frame", len(data_frame))
            data_frame = b''


