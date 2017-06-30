import threading
import multiprocessing as mp
import sys

def ask(stdin):
    print 'Your name? ',
    a = stdin.readline().strip()
    if a == 'Tester':
        print 'Hello'
    else:
        print 'Bye'   
    stdin.close()

def writeFiles():
    pass

if __name__ == '__main__': 
    p1 = mp.Process(target=writeFiles)   
    p1.start()
    t1 = threading.Thread(target=ask, args=(sys.stdin,))
    t1.start()
    p1.join()
    t1.join()