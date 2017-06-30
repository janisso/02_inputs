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
import OSC


#IMPORT MIDI FILE
import mido
from mido import MidiFile



#FUNCTION FOR TRIGGERING


mid = MidiFile('schubert_impromptu.mid')


#SETTING UP OSC CLIENT FOR PROCESSING
c = OSC.OSCClient()
c.connect(('127.0.0.1', 7111))   # connect to PROCESSING IDE

#SENDING OSC MESSAGES
def oscSend(q,stri):
    oscmsg = OSC.OSCMessage()
    oscmsg.setAddress(stri)
    oscmsg.append(q)
    c.send(oscmsg)


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
Signal = genfromtxt('interpolated_values.csv',delimiter=',')[:,1]
#Signal = genfromtxt('array.csv')
#plt.plot(Signal)
#plt.show()

#SET UP WINDOW LENGTH AND HOP SIZE FOR REGRESSION
window_length = 200
hop_size = 50

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

#SET UP CIRCULAR BUFFER FOR FIR FILTER
cb = CircularBuffer(size=window_length)
for i in range(window_length):
    cb.append(0)

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

    def doReg(self,q,uPhase):
        while True:
            if not q.empty():
                start = time.time()
                yo = q.get()
                data = yo[0]
                #print data
                nr = yo[1]
                guess_std = self.est_std
                guess_phase = self.est_phase + self.est_frac*hop_size
                guess_frac = self.est_frac
                optimize_func = lambda x: x[0]*np.sin(t*x[1]+x[2]) - data
                self.est_std, self.est_frac, self.est_phase = least_squares(optimize_func, [guess_std, guess_frac, guess_phase],bounds=([0,0,-np.inf],[1500,0.05,np.inf]),max_nfev=50).x
                if (self.est_phase < self.prev_phase) or (self.est_phase > self.prev_phase+np.pi):
                    #self.est_phase = self.prev_phase
                    self.est_phase = uPhase.value
                self.prev_phase = self.est_phase
                #data_fit = self.est_std*np.sin(t*self.est_frac+self.est_phase)        
                #self.inv_phase = np.arcsin(data_fit[-1]/self.est_std)
                end = time.time()
                oscSend(self.est_phase,'/phase')
                #print self.est_phase-np.pi, self.counts, end-start,nr
                print self.est_phase/(2*np.pi), self.est_frac*1000
                if end-start > 0.05:
                    print 'WHAT THE FUCK'
                self.counts+=1

#COLLECTING SAMPLES
def collectSamples(q,uPhase):
    #uPhase = 0
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
                #PUTTOMG VALUE IN CIRCULAR BUGGER
        cb.append(vel)

        #GETTING SMOOTHED VALUE
        avg_vel = sum(cb*coeffs)
        avg_velS = schmit(avg_vel,50)
        #oscSend(avg_vel,"/vel")

        #GETTING ACCELERAION
        avg_acc = (avg_vel - prev_vel)*100
        avg_accS = schmit(avg_acc,150)
        #oscSend(avg_acc,"/acc")

        #VERIFICATION MODULE
        if ((avg_accS*prev_accS<0) and (flag == 0) and (avg_velS>0) and (timer_ting < 0)):
            flag = 1
            timer_ting = 10
            uPhase.value+=np.pi/2
            print 'Phase is ', uPhase.value/(np.pi*2), hello
            #oscSend(flag,"/flag")
        elif ((avg_velS*prev_velS<0) and (flag == 1) and (timer_ting < 0)):
            flag = 2
            timer_ting = 10
            uPhase.value+=np.pi/2
            print 'Phase is ', uPhase.value/(np.pi*2), hello
            #oscSend(flag,"/flag")
        elif ((avg_accS*prev_accS<0) and (flag == 2) and (avg_velS<0) and (timer_ting < 0)):
            flag = 3
            timer_ting = 10
            uPhase.value+=np.pi/2
            print 'Phase is ', uPhase.value/(np.pi*2), hello
            #oscSend(flag,"/flag")
        elif ((avg_velS*prev_velS<0) and (flag == 3) and (timer_ting < 0)):
            flag = 0
            timer_ting = 10
            uPhase.value+=np.pi/2
            print 'Phase is ', uPhase.value/(np.pi*2), hello
            #oscSend(flag,"/flag")
        timer_ting -= 1
        #print hello

        #SETTING PREVIOUS VALUE TO CURRENT
        prev_vel = avg_vel
        prev_velS = avg_vel
        prev_acc = avg_acc
        prev_accS = avg_acc

        if window_time == hop_size:
            window_time = 0
            for j in range(window_length):
                data[j]=cbReg[j]
            q.put((data,hello))
        #print i
        cbReg.append(avg_vel)
        window_time+=1
        hello+=1
        sleep(0.0005)
        #print vel

#MAIN FUNCTION THAT STARTS ALL OF THE PROCESSES
if __name__ == "__main__":
    #SET UP QUEUE FOR STORING REGRESSION DATA
    q = multiprocessing.Queue()

    #lock=multiprocessing.Lock()

    #INITIALISATION OF REGRESSION CLASS
    r = REG()
    uPhase = multiprocessing.Value('d',0.0)

    #pool = multiprocessing.Pool(initializer=)

    #PROCESSES FOR COLLECTING SAMPLES AND DOING REGRESSION
    p1 = multiprocessing.Process(target=collectSamples,args=(q,uPhase))
    p2 = multiprocessing.Process(target=r.doReg,args=(q,uPhase))
    
    #START THE PROCESSES
    p1.start()
    p2.start()

    #JOIN PRECESSES
    p1.join()
    p2.join()