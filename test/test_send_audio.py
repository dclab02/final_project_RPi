import pyaudio
import wave
import socket
import time

def bytes_to_bin(b):
    return bin(int.from_bytes(b, byteorder='big'))

HOST, PORT = "192.168.50.168", 1234
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.connect((HOST, PORT))
CHUNK = 100000

if __name__ == "__main__":
    # args = parse_arg()

    wf = wave.open('./input2.wav', 'rb')

    p = pyaudio.PyAudio()

    channels, sampwidth, framerate, nframes, comptype, compname = wf.getparams()
    print(wf.getparams())

    # open stream (2)
    # stream = p.open(format=pyaudio.paInt16,
    #                 channels=channels,
    #                 rate=framerate,
    #                 output=True)

    # read data
    data = wf.readframes(CHUNK)

    # play stream (3)
    data_all = b''
    while len(data) > 0:
        # stream.write('')
        data_all += data
        # print(len(data_all))
        data = wf.readframes(CHUNK)

    print(f"wave data len={len(data_all)}")


    step = 10
    delay =  1 / (4410000) # second
    for i in range(0, len(data_all), step):
        client.send(b'\xaa' + data_all[i:i+step])
        print(f"sent {step + 1}", data_all[i:i+step])
        time.sleep(delay)

    
    # stop stream (4)
    # stream.stop_stream()
    # stream.close()

    # close PyAudio (5)
    p.terminate()
