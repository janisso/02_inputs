import sys
import Leap
import multiprocessing
#from multiprocessing import Pool
from time import sleep
from scipy import signal
from collections import deque
import numpy as np
from numpy import genfromtxt
from scipy.optimize import least_squares
import time
import matplotlib.pyplot as plt



#CIRCULAR BUFFER CLASS FOR STORING VALUES FOR FILTERING
class CircularBuffer(deque):
    def __init__(self, size=0):
        super(CircularBuffer, self).__init__(maxlen=size)
    @property
    def average(self):  # TODO: Make type check for integer or floats
        return sum(self)/len(self)

#SCHMIT TRIGGER TO DISCOUNT DEVIATIONS AROUND ZERO FOR VELOCITY AND ACCELERATION
def schmit(val,thresh):
    if 0 < val <= thresh:
        new_sig = thresh
    if thresh*(-1) <= val <= 0:
        new_sig = thresh*(-1)
    else:
        new_sig = val
    return new_sig

#ARRAY WITH NEAREST INTERPOLATED DATA COLLECTED FROM LEAP MOTION
#Signal = genfromtxt('interpolated_values.csv',delimiter=',')[:,1]
#Signal = genfromtxt('array.csv')
#plt.plot(Signal)
#plt.show()

#SET UP WINDOW LENGTH AND HOP SIZE FOR REGRESSION
window_length = 200
hop_size = window_length/4

#TIME ARRAY TO BE USED IN REGRESSION
t = np.arange(window_length)

#ARRAY WITH DATA TO PASS ON TO REGRESSION
data = np.zeros(window_length)

#CIRCULAR BUFFER TO COLLECT THE DATA
cbReg = CircularBuffer(size=window_length)
for i in range(window_length):
    cbReg.append(0)

#SET UP FILTER
f = 0.005
coeffs = signal.firwin(window_length, f)

#REGRESSION CLASS
class REG():
    def __init__(self):
        self.est_frac = 0#3/(1000/(2*np.pi))
        self.prev_frac = 0
        self.est_phase = 0
        self.prev_phase = 0
        self.est_std = 250
        self.prev_std = 0
        #self.window_size = 100
        #self.hop_size = 50
        #self.inv_phase = 0
        self.counts = 0

    def doReg(self,q):
        while True:
            if not q.empty():
                start = time.time()
                yo = q.get()
                data = yo[0]
                nr = yo[1]
                guess_std = self.est_std
                guess_phase = self.est_phase + self.est_frac*hop_size
                guess_frac = self.est_frac
                optimize_func = lambda x: x[0]*np.sin(t*x[1]+x[2]) - data
                self.est_std, self.est_frac, self.est_phase = least_squares(optimize_func, [guess_std, guess_frac, guess_phase],bounds=([0,0,-np.inf],[1500,5,np.inf]),max_nfev=50).x
                if self.est_phase < self.prev_phase:
                    self.est_phase = self.prev_phase
                self.prev_phase = self.est_phase
                #data_fit = self.est_std*np.sin(t*self.est_frac+self.est_phase)        
                #self.inv_phase = np.arcsin(data_fit[-1]/self.est_std)
                end = time.time()
                print self.est_phase, self.counts, end-start,nr
                self.counts+=1

#COLLECTING SAMPLES
def collectSamples(q):
    uPhase = 0
    vel = 0
    avg_vel = 0
    avg_velS = 0
    prev_vel = 0
    prev_velS = 0
    avg_acc = 0
    avg_accS = 0
    prev_acc = 0
    prev_accS = 0
    flag = 3
    timer_ting = -1
    window_time = 0
    #array_time = 0.0
    hello = 0
    for i in range(len(Signal)):
        vel = Signal[i]
        if window_time == hop_size:
            window_time = 0
            for j in range(window_length):
                data[j]=cbReg[j]
            q.put((data,hello))
        #print i
        cbReg.append(Signal[i])
        window_time+=1
        hello+=1
        sleep(0.001)

#MAIN FUNCTION THAT STARTS ALL OF THE PROCESSES
if __name__ == "__main__":
    #SET UP QUEUE FOR STORING REGRESSION DATA
    q = multiprocessing.Queue()

    #lock=multiprocessing.Lock()

    #INITIALISATION OF REGRESSION CLASS
    r = REG()

    #pool = multiprocessing.Pool(initializer=)

    #PROCESSES FOR COLLECTING SAMPLES AND DOING REGRESSION
    p1 = multiprocessing.Process(target=collectSamples,args=(q,))
    p2 = multiprocessing.Process(target=r.doReg,args=(q,))
    
    #START THE PROCESSES
    p1.start()
    p2.start()

    #JOIN PRECESSES
    p1.join()
    p2.join()