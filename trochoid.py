import matplotlib.pyplot as plt
import numpy as np
import sympy

from numpy import genfromtxt
from scipy.signal import find_peaks_cwt

vals = genfromtxt('/Users/mb/Desktop/Janis.So/06_qmul/BB/05_data/G8/dummy/1_e4/0/get_samples.csv',delimiter=',')[1:]
t = vals[:,0]
pos = vals[:,1]

a = np.full(100,8)#+np.sin(np.linspace(0,3,100)) #radius of circle
b = np.full(100,4)#+np.sin(np.linspace(0,3,100)) #distance from center

fr = np.pi*2

phis = np.linspace(0,fr*4,100)

x = a*phis - b*np.sin(phis)
y = a - b*np.cos(phis)

f, axarr = plt.subplots(2, sharex=True)
axarr[0].plot(x,y)
axarr[1].plot(x[1:],np.diff(y))


t = np.linspace(0,99,100)

#phi = -(t/2)+np.pi*(np.abs(8-4))/(2*(8-4))-sympy.atan((8-4)/(8+4)*sympy.cot(t/2))+np.pi*(1/(2*np.pi))




peakind = find_peaks_cwt(pos, np.arange(1,10))

f, axarr = plt.subplots(3, sharex=True)
axarr[0].plot(t,pos)
axarr[0].plot(t[peakind],pos[peakind],'o')
axarr[1].plot(t[1:],np.diff(pos))
axarr[2].plot(t[1:],np.diff(t))