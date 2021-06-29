from scipy.fft import fft, fftfreq
import numpy as np
import asyncio
import websockets
import time
import random
import threading
import json
from equalizer import Filter
# TODO
# 1. deal with the communication with FPGA
# 2. add Constraint?
#   (1). type (lowshelf, highshelf, peaking)
#   (2). frequency (0 - 20000)
#   (3). Gain (-15 - 15)
#   (4). Q (0.1-0.2)

# some parameters
N = 600         # Number of sample points
F = 20000.0       # sample Frequency
T = 1.0 / F     # sample spacing
stop = False
parameters = []

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
            # 3. send data to fpga
            self.data = [random.randint(0,200) for i in range(150)]
            time.sleep(0.1)
            self.data = [50 for i in range(150)]
            time.sleep(0.1)
        
# intereface to frontend
async def handledata(websocket, path):
    global filternodes
    while True:
        rq = await websocket.recv()
        if rq == "request":
            for el in fpgathread.data:
                await websocket.send(str(el))
            await websocket.send('done')
        elif rq == "parameter":
            await websocket.send('sendparameter_ack')
            receive = await websocket.recv()
            parameters_raw = json.loads(receive)
            for i, filternode in enumerate(filternodes):
                filternode.filt(parameters_raw["filters"][i]["type"], 
                parameters_raw["filters"][i]["f"], 
                parameters_raw["filters"][i]["g"], 
                parameters_raw["filters"][i]["q"])

try:
    filternodes = [Filter(F) for i in range(5)]
    fpgathread = FPGA_thread(1, "FPGAThread")
    fpgathread.start()
    asyncio.get_event_loop().run_until_complete(websockets.serve(handledata, 'localhost', 8765))
    asyncio.get_event_loop().run_forever()

except KeyboardInterrupt:
    stop = True
    print("Exiting program...")
