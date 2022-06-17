import sklearn
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
import mat73
import pandas as pd
from scipy.optimize import curve_fit
import math

#constants
FILE = "..//data//Part_4.mat"
DATA_NAME = "Part_4"

def displayer(start, end):
    data = mat73.loadmat(FILE)
    z = data[DATA_NAME]
    #Read PPG and BP from data array
    ppg = z[0][0]
    bp = z[0][1]
    #Slice the array into the wanted interval
    bp = bp[start:end]
    #Scale PPG wave, as its magnitude is small
    ppg = 42 * ppg[start:end]
    #Generate evenly distributed x values for graphing
    x = np.linspace(1, end - start, num=len(ppg)).reshape(-1, 1)
    x1 = np.linspace(1, end - start, num=len(bp)).reshape(-1, 1)
    #Display Graph
    plt.scatter(x1, bp, color = 'blue') 
    plt.scatter(x1, ppg, color = "green")
    plt.xlabel("Time (arbitrary scaled units)")
    plt.ylabel("Magnitude (arbitrary scaled units)")
    plt.title("PPG and BP Waveform")
    plt.legend(["BP", "PPG"])
    plt.show()


def find_bp(display):
    data = mat73.loadmat(FILE)
    z = data[DATA_NAME]
    x = z[0][1]
    bp = []
    for i in range(60, 20000, 60):
        if (max(x[i - 60: i]) > 90):
            bp.append(max(x[i - 60: i]))
    bp = np.array(bp)
    if display:
        x = np.linspace(1, 1000, num=len(bp)).reshape(-1, 1)
        plt.scatter(x, bp, color = 'blue') 
        plt.show()
    print(len(bp))
    return bp


def derivative(display):
    data = mat73.loadmat(FILE)
    z = data[DATA_NAME]
    #Only looking at 20000 points for now
    deriv = np.zeros(20000)
    for k in range(1):
        y = z[k][0]
        i = 1
        j = 0
        while(i < 20000):
            slope = (y[i + 1] - y[i - 1]) / 2
            deriv[j] = slope
            i = i + 1
            j = j + 1
    zeros = []
    i = 0
    for i in range(len(deriv)):
        if(deriv[i] < 0.01 and deriv[i] > -0.01):
            zeros.append(i)
    zeros = np.array(zeros)
    proc = []
    seq = 1
    #Remove zeros that appear right next to each other due to approximation
    for i in range(1, len(zeros)):
        if(zeros[i] == zeros[i - 1] + 1):
            seq = seq + 1
        else:
            proc.append((zeros[i - seq] + zeros[i - 1]) / 2)
            seq = 1
    for i in range(len(proc) - 2, -1, -1):
        if(abs(proc[i] - proc[i + 1]) < 9):
            proc.remove(proc[i])
    proc = np.array(proc)
    time = []
    bp = []
    x = z[0][1]
    #Calculate blood pressure and crest time
    y = z[0][0]
    for i in range(2, len(proc) - 2, 2):
        if(max(x[int(proc[i]):int(proc[i + 2])]) > 100):
            if(y[int(proc[i])] > 1.277):
                time.append(proc[i + 1] - proc[i])
                bp.append(max(x[int(proc[i]):int(proc[i + 2])]))
    time = np.array(time)
    bp = np.array(bp)
    #Debugging purposes
    if display:
        x2 = np.linspace(1, 1000, len(time[0:100]))
        plt.scatter(x2, time[0:100], color = "blue")
        plt.show()
    print(len(time))
    return [time, bp]



def predicter():
    data = mat73.loadmat(FILE)
    z = data[DATA_NAME]
    temp = derivative(False)
    #bp = find_bp(False)
    regressor = RandomForestRegressor(n_estimators = 500, random_state = 25)
    time = temp[0].reshape(-1 , 1)
    bp = temp[1]
    regressor.fit(time, bp)
    plt.scatter(time, bp, color = 'blue') 
    X_grid = np.arange(min(time), max(time), 0.01)               
    X_grid = X_grid.reshape((len(X_grid), 1))
    plt.plot(X_grid, regressor.predict(X_grid),
            color = 'green')
    plt.title('Random Forest Regression')
    plt.xlabel('PPG Crest Time')
    plt.ylabel('Systolic Blood Pressure')
    plt.show()
    
#derivative(False)
#find_bp(False)
predicter()
#derivative(True)