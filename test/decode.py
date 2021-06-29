# from pwn import *
import math
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavf
from scipy.signal import butter, lfilter, freqz, filtfilt
import numpy as np

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

# Filter requirements.
order = 4
fs = 44100.0       # sample rate, Hz
low_cutoff = 400
high_cutoff = 900  # desired cutoff frequency of the filter, Hz

# plot filter###############################################
b, a = butter_bandpass(high_cutoff, low_cutoff, fs, order)
w, h = freqz(b, a, worN=8000)
plt.subplot(2, 1, 1)
plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
# plt.plot(low_cutoff, 0.5*np.sqrt(2), 'ko')
# plt.plot(high_cutoff, 0.5*np.sqrt(2), 'ko')
plt.axvline(low_cutoff, color='k')
plt.axvline(high_cutoff, color='k')
plt.xlim(0, 0.5*fs)
plt.title("Bandpass Filter Frequency Response")
plt.xlabel('Frequency [Hz]')
plt.grid()
# plt.show()
#####################################################################
time = 20
wav_sample_rate = 44100
wav_sample_rate = 44100
record_frequency = 2000000
sample_points = time * record_frequency
inFileName = 'RCSS_ATIS_2.bin'
outFileName = 'out'

ubytes = np.fromfile(inFileName, dtype='uint8', count=-1)


ubytes = ubytes[0:sample_points * 2]
print("read "+str(len(ubytes))+" bytes from "+inFileName)

# turn to signed integer
ufloats = np.array([(int(ubyte) - 127) for ubyte in ubytes])
ufloats.shape = (len(ubytes)//2, 2)
# sampling and count magnitude
amplitudes = [ math.sqrt(ufloats[i][0] ** 2+ ufloats[i][1] ** 2) for i in range(0,len(ufloats), (record_frequency//wav_sample_rate)) ]

# pass bandpass filter
y = butter_bandpass_filter(amplitudes, high_cutoff, low_cutoff, fs, order) * 4096

# output .wav
out_f = 'out.wav'
wavf.write(out_f, wav_sample_rate, np.array(y).astype(np.int16))

# plot figure######################################3
plt.subplot(2, 1, 2)
plt.plot(amplitudes[0:10000], 'b-', label='data')
plt.plot(y[0:10000], 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplots_adjust(hspace=0.35)
plt.show()


