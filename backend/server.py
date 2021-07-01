from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter, freqz, filtfilt
import numpy as np
import asyncio
import websockets
import time
import random
import threading
import json
from equalizer import *
from collections import deque
import math
import socket

# from rtlsdr import RtlSdr
# from pylab import psd
# import matplotlib.pyplot as plt
# TODO
# 1. deal with the communication with FPGA

# Filter requirements.
order = 4
fs = 44100.0       # sample rate, Hz
low_cutoff = 400
high_cutoff = 900  # desired cutoff frequency of the filter, Hz
###############################################################
# some parameters
record_frequency = 2000000
wav_sample_rate = 44100
N = 20000         # Number of sample points
datalength = 200
stop = False
parameters = []
buffer = [0] * N
PLAN = "B"
lock = False

# util function
def gen_frequency_data(data, num):
    N = num
    yf = fft(data)[:N//2]
    normalization_y=np.abs(yf)/N
    return [el for el in normalization_y]
    # return [int(el) for el in np.abs(yf)]

def butter_bandpass(high, low, fs, order=5):
    nyq = 0.5 * fs
    low_cutoff = low / nyq
    high_cutoff = high / nyq
    b, a = butter(order, [low_cutoff, high_cutoff], btype='bandpass', analog=False)
    return b, a

def butter_bandpass_filter(data, highcutoff, lowcutoff, fs, order=5):
    b, a = butter_bandpass(highcutoff, lowcutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# thread for acting backend server
class FPGA_thread (threading.Thread):
    def __init__(self, threadID, name):
        global N,downsampling_rate

        threading.Thread.__init__(self)
        self.N = N
        self.threadID = threadID
        self.name = name
        self.data = [0] * datalength
        self.buffer = deque([0] * N)

    def run(self):
        global eq, stop
        print(f'{self.name} start')
        if PLAN == "B":
            self.play()
        elif PLAN == "BIQ":
            self.playIQ()
        else:
        # TODO 
        # 1. get data from fpga
        # 2. processing
        # 3. send data to fpga
            pass
                    

    def play(self):
        global eq, stop, wf, lock, client
        CHUNK = 1
        p = pyaudio.PyAudio()
        channels, sampwidth, framerate, nframes, comptype, compname = wf.getparams()
        stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=framerate,
                    output=True)
        # read data
        streamdata = wf.readframes(CHUNK)
        
        samplecount = 0
        _buffer = [0] * 1000
        # play stream
        while len(streamdata) > 1 and not stop:
            filter_data = eq.run(streamdata)
            self.buffer.popleft()
            self.buffer.append(byte_to_int(filter_data))
            samplecount += 1
            if(samplecount == 10000):
                lock = True
                samplecount = 0
                rawdata = gen_frequency_data(list(self.buffer), len(self.buffer))
                section = len(self.buffer) // datalength
                for i in range(0, len(self.buffer), section):
                    self.data[i//section] = sum(rawdata[i:i+section]) / section
                lock = False
            stream.write(filter_data)
            streamdata = wf.readframes(CHUNK)
            client.send(b'\xaa' + filter_data)
        client.close()

    def playIQ(self):
        global eq, stop, IQubytes, lock
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=framerate,
                    output=True)
        samplecount = 0
        signals = [ math.sqrt(IQubytes[i] ** 2+ IQubytes[i+1] ** 2) *1024 for i in range(0,len(IQubytes),2)]
        # signals = butter_bandpass_filter(amplitudes, high_cutoff, low_cutoff, fs, order)* 4096
        for i in range(len(signals)):
            if stop:
                break
            # get IQ
            # Ibyte = (int(IQubytes[i]) - 127)
            # Qbyte = (int(IQubytes[i+1]) - 127)
            # # demodulate
            # signal = math.sqrt(Ibyte ** 2 + Qbyte ** 2)
            
            _buffer = [0] * 1000
            filter_data = eq.run(int_to_byte(int(signals[i])))
            self.buffer.popleft()
            self.buffer.append(byte_to_int(filter_data))
            samplecount += 1
            if(samplecount == 10000):
                lock = True
                samplecount = 0
                rawdata = gen_frequency_data(list(self.buffer), len(self.buffer))
                section = len(self.buffer) // datalength
                for i in range(0, len(self.buffer), section):
                    self.data[i//section] = sum(rawdata[i:i+section]) / section
                lock = False
            stream.write(filter_data)
        print('fin')

# intereface to frontend
async def handledata(websocket, path):
    global eq, lock
    while True:
        rq = await websocket.recv()
        if rq == "request":
            while True:
                if not lock:
                    for el in fpgathread.data:
                        await websocket.send(str(el))
                    await websocket.send('done')
                    break
        elif rq == "parameter":
            await websocket.send('sendparameter_ack')
            receive = await websocket.recv()
            parameters_raw = json.loads(receive)
            for i in range(5):
                eq.set_coef(i+1, parameters_raw["filters"][i]["type"], 
                parameters_raw["filters"][i]["f"],
                parameters_raw["filters"][i]["g"],
                parameters_raw["filters"][i]["q"])

HOST, PORT = "192.168.50.168", 1234
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((HOST, PORT))

if PLAN == 'B':
    wf = wave.open('../utils/out_demo.wav', 'rb')
    channels, sampwidth, framerate, nframes, comptype, compname = wf.getparams()
if PLAN == 'BIQ':
    inFileName = '../utils/143.36-2.bin'
    IQubytesraw = np.fromfile(inFileName, dtype='uint8', count=-1)
    
    IQubytesraw_ = [ IQubytesraw[i] for i in range(0,len(IQubytesraw), (record_frequency//wav_sample_rate)*2) ]
    IQubytes = [(int(ubyte) - 127) for ubyte in IQubytesraw_]
    framerate = 44100

eq = Equalizer(framerate)
eq.set_coef(1, "allpass", 1000, 6, 1)
eq.set_coef(2, "allpass", 1000, 6, 1)
eq.set_coef(3, "allpass", 1000, 6, 1)
eq.set_coef(4, "allpass", 1000, 6, 1)
eq.set_coef(5, "allpass", 1000, 6, 1)


try:
    fpgathread = FPGA_thread(1, "FPGAThread")
    fpgathread.start()
    asyncio.get_event_loop().run_until_complete(websockets.serve(handledata, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    stop = True
    print("Exiting program...")
    # sdr.close()