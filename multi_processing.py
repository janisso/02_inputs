import sys
import Leap
import multiprocessing
from multiprocessing import Pool
from time import sleep
from scipy import signal
from collections import deque
import numpy as np

#CIRCULAR BUFFER CLASS FOR STORING VALUES FOR FILTERING
class CircularBuffer(deque):
    def __init__(self, size=0):
        super(CircularBuffer, self).__init__(maxlen=size)
    @property
    def average(self):  # TODO: Make type check for integer or floats
        return sum(self)/len(self)

class arr:
	def __init__():
		self.values = []
		for i in range(0,20):
			self.values.append(0)


#a = []
#for i in range(0,20):
#	a.append(0)

a = np.zeros(20)

numtaps = 20
cb = CircularBuffer(size=numtaps)
for i in range(numtaps):
    cb.append(0)
    #array.append(i)

def doSmthng(q):
	while True:
		if not q.empty():
			print q.get()

def numberGen(a,lock,q):
	i = 0
	c = 0
	while True:
		if c == 20:
			lock.acquire()
			for j in range(0,20):
				a[j]=cb[j]
			q.put(a)
			lock.release()
			c = 0
			print i
		cb.append(i)
		i+=1
		c+=1
		sleep(0.05)

if __name__ == "__main__":

    q = multiprocessing.Queue()

    lock=multiprocessing.Lock()

    #pool = multiprocessing.Pool(initializer=)

    p1 = multiprocessing.Process(target=numberGen,args=(a,lock,q))
    p2 = multiprocessing.Process(target=doSmthng,args=(q,))
    
    p1.start()
    p2.start()

    p1.join()
    p2.join()