import os, sys
import socket
import time
import math
import pyaudio
import wave
from scipy import signal
import numpy as np


IQ_FILE_PATH = ''


if len(sys.argv) > 1:
    IQ_FILE_PATH = sys.argv[1]

with open(IQ_FILE_PATH, 'rb') as f:
    iq_data = f.read()

# data = b''

# p = pyaudio.PyAudio()
# # open stream (2)
# stream = p.open(format=pyaudio.paInt16,
#     channels=1,
#     rate=44100,
#     frames_per_buffer=2**16,
#     output=True)


wf = wave.open('./output1.wav', 'wb')
wf.setnchannels(1)
wf.setsampwidth(2) # 2byte
wf.setframerate(48000) #


delay = 1 / (2 * 10**6)

data_i = []
data_q = []

data32_all = []

data_all = []


# downsample 32
for k in range(0, int(len(iq_data)/2), 2):
    # i = iq_data[k]
    # q = iq_data[k + 1]
    data_i.append(iq_data[k])
    data_q.append(iq_data[k + 1])
    # data_all.append(math.sqrt(i**2+q**2))
print("finish calculate iq")

down32_i = signal.decimate(data_i, 417)
down32_q = signal.decimate(data_q, 417)

for k in range(0, len(down32_q)):
    data32_all.append(math.sqrt(down32_i[k]**2+down32_q[k]**2))


print(f'resampled={len(data32_all)}')


# # downsample 4
# data_all = data_all[::4]

# # upsample 3
# for k in range(0, len(data_all)):
#     for i in range(3):
#         data = data_all[k]
#         data = int.to_bytes(int(data), 2, byteorder='big')
#         wf.writeframes(data)
# print(type(data_all))
data_all = np.asarray(data32_all)

# print(data_all)
data_all = data_all.astype(np.int16)
for d in data_all:
    wf.writeframes(d)


print("finish calculate audio")


