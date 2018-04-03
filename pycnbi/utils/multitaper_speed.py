# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Measure multitaper computation speed.

@author: leeq
"""

import mne
import numpy as np
import pycnbi.utils.q_common as qc

def main():
    fmin = 1
    fmax = 40
    channels = 64
    wlen = 0.5 # window length in seconds
    sfreq = 512
    num_iterations = 500

    signal = np.random.rand(channels, int(np.round(sfreq * wlen)))
    psde = mne.decoding.PSDEstimator(sfreq=sfreq, fmin=fmin,\
        fmax=fmax, bandwidth=None, adaptive=False, low_bias=True,\
        n_jobs=1, normalization='length', verbose=None)
    
    tm = qc.Timer()
    times = []
    for i in range(num_iterations):
        tm.reset()
        psd = psde.transform(signal.reshape((1, signal.shape[0], signal.shape[1])))
        times.append(tm.msec())
        if i % 100 == 0:
            print('%d / %d' % (i, num_iterations))
    ms = np.mean(times)
    fps = 1000 / ms
    print('Average = %d ms (%d Hz)' % (ms, fps))

if __name__ == '__main__':
    main()
