import os, sys
import socket
import time
import scipy.io.wavfile as wavf
import numpy as np

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



wav_sample_rate = 44100
record_frequency = 2000000

t = 10
sample_points = t * record_frequency

ubytes = np.fromfile(IQ_FILE_PATH, dtype='uint8', count=-1)
ubytes = ubytes[0:sample_points * 2] # only chooce time * record_frequency data
print("read "+str(len(ubytes))+" bytes from "+IQ_FILE_PATH)


# turn to signed integer
ufloats = np.array([(int(ubyte) - 127) for ubyte in ubytes])
ufloats.shape = (len(ubytes)//2, 2)



# sampling
sampled = np.array([(ufloats[i][0], ufloats[i][1] ) for i in range(0,len(ufloats), (record_frequency//wav_sample_rate))])
sampled = sampled * 10
print("sampled")

delay = 1 / 1000
step = 10
for i in range(0, len(sampled), step):
    data = sampled[i:i+step].flatten().astype(np.int8)
    client.send(b'\xaa' + data.tobytes())
    print(f"{step} of iq_data sent", len(data) + 1, data.tobytes(), int(np.sqrt(data[0]**2 + data[1]**2)))
    time.sleep(delay)

# print(f"{len(iq_data)} sent")
# print(f"last byte = {bin(iq_data[-1])}")

client.close()