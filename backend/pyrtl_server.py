from rtlsdr import RtlSdr
from pylab import psd
import matplotlib.pyplot as plt

sdr = RtlSdr()

sdr.sample_rate = 2.048e6
sdr.center_freq = 99.7e6
sdr.gain = 'auto'

samples = sdr.read_samples(256*1024)
sdr.close()

# use matplotlib to estimate and plot the PSD
# psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
# plt.xlabel('Frequency (MHz)')
# plt.ylabel('Relative power (dB)')

# plt.show()
print(samples.shape)