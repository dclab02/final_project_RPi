import os, sys
import socket
from rtlsdr import RtlSdr
from pylab import psd
import matplotlib.pyplot as plt

HOST, PORT = "192.168.50.168", 1234

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((HOST, PORT))


sdr = RtlSdr()

sdr.sample_rate = 2.048e6
sdr.center_freq = 99.7e6
sdr.gain = 'auto'

# plt.show()
print(samples.shape)

while True:
    samples = sdr.read_samples(256*1024)
    client.sendto(samples, (HOST, PORT))


sdr.close()
client.close()