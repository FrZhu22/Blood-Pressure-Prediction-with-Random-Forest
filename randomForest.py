import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import wfdb
import wfdb.processing
import scipy.io.wavfile as wavf
import pandas as pd
from scipy.io import loadmat
import scipy.signal as sig
from sklearn.ensemble import RandomForestRegressor
from scipy.stats import pearsonr

HEAD = "MAT_Files\\p000543\\p000543-2148-12-13-21-51m"
REC = "MAT_Files\p087247\p087247-2105-12-23-15-35m"
REC2 = "MAT_Files\p084479\p084479-2121-11-19-15-12m"
REC3 = "MAT_Files\p046429\p046429-2151-10-13-04-41m"
REC4 = "MAT_Files\p079372\p079372-2197-12-27-17-23m"
REC5 = "MAT_Files\p002639\p002639-2112-09-04-09-16m"
REC6 = "MAT_Files\p068564\p068564-2119-08-17-12-07m"
REC7 = "MAT_Files\p060747\p060747-2188-08-29-15-31m"
REC8 = "MAT_Files\p068744\p068744-2161-06-24-19-25m"
DATA_NAME = "val"
DIR = "MAT_Files\\p000160"

def hampel(vals_orig, k=7, t0=3):
    '''
    vals: pandas series of values from which to remove outliers
    k: size of window (including the sample; 7 is equal to 3 on either side of value)
    '''
    #Make copy so original not edited
    vals=vals_orig.copy()    
    #Hampel Filter
    L= 1.4826
    rolling_median=vals.rolling(k).median()
    difference=np.abs(rolling_median-vals)
    median_abs_deviation=difference.rolling(k).median()
    threshold= t0 *L * median_abs_deviation
    outlier_idx=difference>threshold
    vals[outlier_idx]=np.nan
    return(vals)

#implementing butterworth bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = sig.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = sig.lfilter(b, a, data)
    return y

def find_peaks(arr, hinty, hintf):
    peaks = []
    df = hintf/2
    currentVal = hinty
    increasing = False
    for i in range(len(arr)):
        #print(i, arr[i])
        if (arr[i] < hinty):
            increasing = False
            continue
        if (arr[i] < currentVal): 
            if (increasing):
                # found a possible peak, compare with previous peak
                #print('possible peak at', i-1)
                np = len(peaks)
                if (np > 0):
                    # there is a previous peak, need to compare
                    pos = peaks[np-1]
                    if (i - 1 - pos < hintf/2):
                        # current peak is close to previous peak. check amplitude
                        if (arr[pos] < arr[i-1]):
                            # current peak is higher, so use current peak instead.
                            peaks[np-1] = i - 1
                    else:
                        # current peak is far from previous peak. It's a new peak
                        peaks.append(i-1)
                else:
                    # this is the first peak found, append to list.
                    peaks.append(i - 1)
                increasing = False
        else:
            increasing = True
        currentVal = arr[i]
    #print('found peaks', peaks)  
    return peaks   

#Plots a signal with its peaks
def peak_plot(signal, peaks):
    peakPlot = np.array([])
    for i in range(len(signal)):
        if i in peaks:
            peakPlot = np.append(peakPlot, [signal[i]])
        else:
            peakPlot = np.append(peakPlot, [0.4])
    plt.plot(signal)
    plt.plot(peakPlot)
    plt.show()

def find_CT(ppg, abp, hint):
    ct = np.array([])
    sbp = find_peaks(abp, 100, 125)
    ppg_peaks = find_peaks(ppg, hint, 125)
    ct = np.array([])
    bp = np.array([])
    for i in range(len(ppg_peaks) - 1):
        #double check to make sure peaks are not too close to each other
        if np.argmin(ppg[ppg_peaks[i]:ppg_peaks[i + 1]]) != 0 and ppg_peaks[i + 1] - ppg_peaks[i] > 10 and ppg_peaks[i + 1] - ppg_peaks[i] < 100:
            #check between 2 peaks for PPG foot and SBP
            cts = np.where(ppg[ppg_peaks[i]:ppg_peaks[i + 1]] == min(ppg[ppg_peaks[i]:ppg_peaks[i + 1]]))[0][0] + ppg_peaks[i]
            ct = np.append(ct, [cts - ppg_peaks[i]])
            bps = find_peaks(abp[ppg_peaks[i]:ppg_peaks[i + 1]], 80, 125)
            bp = np.append(bp, [bps[0] + ppg_peaks[i]])
    peak_plot(ppg, ppg_peaks)
    return bp, ct
    
#displays PPG and ABP waveforms in a certain record and interval
def displayer(start, end, nums, rec):
    record1 = wfdb.rdrecord(rec)
    signal = record1.p_signal
    signal = signal.T
    ppg = signal[nums[0]][start:end]
    signal = signal[nums[1]][start:end]
    plt.plot(ppg, color="blue")
    plt.plot(signal, color="red")
    plt.show()

def estimation(start, end):
    #read signal from patients
    record1 = wfdb.rdrecord(REC)
    record2 = wfdb.rdrecord(REC2)
    record3 = wfdb.rdrecord(REC3)
    record4 = wfdb.rdrecord(REC4)
    record5 = wfdb.rdrecord(REC5)
    record6 = wfdb.rdrecord(REC6)
    record7 = wfdb.rdrecord(REC7)
    record8 = wfdb.rdrecord(REC8)
    signal = record1.p_signal
    signal2 = record2.p_signal
    signal3 = record3.p_signal
    signal4 = record4.p_signal
    signal5 = record5.p_signal
    signal6 = record6.p_signal
    signal7 = record7.p_signal
    signal8 = record8.p_signal
    signal = signal.T
    signal2 = signal2.T
    signal3 = signal3.T
    signal4 = signal4.T
    signal5 = signal5.T
    signal6 = signal6.T
    signal7 = signal7.T
    signal8 = signal8.T
    ppg = signal[5][start[0]:end[0]]
    ppg2 = signal2[4][start[1]:end[1]]
    ppg3 = signal3[6][start[2]:end[2]]
    ppg4 = signal4[4][start[3]:end[3]]
    ppg5 = signal5[9][start[4]:end[4]]
    ppg6 = signal6[5][start[5]:end[5]]
    ppg7 = signal7[5][start[6]:end[6]]
    ppg8 = signal8[4][start[7]:end[7]]
    abp = signal[6][start[0]:end[0]]
    abp2 = signal2[5][start[1]:end[1]]
    abp3 = signal3[7][start[2]:end[2]]
    abp4 = signal4[5][start[3]:end[3]]
    abp5 = signal5[10][start[4]:end[4]]
    abp6 = signal6[6][start[5]:end[5]]
    abp7 = signal7[6][start[6]:end[6]]
    abp8 = signal8[5][start[7]:end[7]]
    #calculate CT and SBP
    bp, ct = find_CT(ppg, abp, 1.5)
    bp2, ct2 = find_CT(ppg2, abp2, 0.5)
    bp3, ct3 = find_CT(ppg3, abp3, 1.5)
    bp4, ct4 = find_CT(ppg4, abp4, 1.2)
    bp5, ct5 = find_CT(ppg5, abp5, 0.62)
    bp6, ct6 = find_CT(ppg6, abp6, 0.65)
    bp7, ct7 = find_CT(ppg7, abp7, 0.62)
    bp8, ct8 = find_CT(ppg8, abp8, 0.62)
    bp = np.hstack((bp, bp2, bp3, bp4, bp5, bp6, bp7, bp8))
    ct = np.hstack((ct, ct2, ct3, ct4, ct5, ct6, ct7, ct8))
    sbp = np.array([])
    for x in bp:
        sbp = np.append(sbp, [abp[int(x)]])
    #calculate correlation factor
    corr, _ = pearsonr(ct, bp)
    print(corr)
    #train Random Forest
    regressor = RandomForestRegressor(n_estimators = 10, random_state = 25)
    regressor.fit(ct.reshape(-1, 1), sbp)
    #Plot results
    plt.scatter(ct, sbp, color = 'blue') 
    X_grid = np.arange(min(ct), max(ct), 0.01)               
    X_grid = X_grid.reshape((len(X_grid), 1))
    plt.plot(X_grid, regressor.predict(X_grid),
            color = 'green')
    plt.xlabel("Crest Time (arbitrary scaled units)")
    plt.ylabel("SBP (mmHg)")
    plt.title("SBP vs CT")
    plt.show()

estimation([70000, 70000, 60000, 70000, 70000, 70000, 70000, 70000], [100000, 74000, 72000, 90000, 80000, 80000, 80000, 80000])
#displayer(70000, 71000, [5, 6], REC)
