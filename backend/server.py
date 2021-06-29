from scipy.fft import fft, fftfreq
import numpy as np
import asyncio
import websockets
import time
import random
import threading
import json

# some parameters
N = 600         # Number of sample points
F = 20000.0       # sample Frequency
T = 1.0 / F     # sample spacing
stop = False
parameters = {}
# util function
def gen_frequency_data(data, num, freq):
    N = num
    T = 1.0 / freq
    yf = fft(data)[:N//2]    
    return [int(el) for el in np.abs(yf)]


# thread for acting backend server
class FPGA_thread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.data = []
 
    def run(self):
        print(f'{self.name} start')
        while not stop:
            # TODO 
            # 1. get data from fpga
            # 2. processing
            self.data = [random.randint(0,200) for i in range(150)]
            time.sleep(0.1)
            self.data = [50 for i in range(150)]
            time.sleep(0.1)
        
# intereface to frontend
async def handledata(websocket, path):
    global parameters
    while True:
        rq = await websocket.recv()
        if rq == "request":
            for el in fpgathread.data:
                await websocket.send(str(el))
            await websocket.send('done')
        elif rq == "parameter":
            # TODO get the data
            await websocket.send('sendparameter_ack')
            receive = await websocket.recv()
            parameters = json.loads(receive)

try:
    fpgathread = FPGA_thread(1, "FPGAThread")
    fpgathread.start()
    asyncio.get_event_loop().run_until_complete(websockets.serve(handledata, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    stop = True
    print("Exiting program...")

# yf = gen_frequency_data(y, N, 1.0/T)
# import matplotlib.pyplot as plt
# xf = fftfreq(N, T)[:N//2]
# plt.plot(xf,  np.abs(yf))
# plt.grid()
# plt.show()
# print(gen_frequency_data(y, 600, 800))