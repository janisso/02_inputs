import sys
import Leap
import multiprocessing
from time import sleep



def worker1():
    i =0
    while True:
        #print i
        if i == 5:
            break #terminate this worker
        i+=1
        sleep(0.1)
    return



def worker2():
    i = 0
    while True:
        #print i
        if i == 10:
            break #terminate this worker
        i+=1
        sleep(0.1)
    return



if __name__ == '__main__':
	while True:
		p1 = multiprocessing.Process()
