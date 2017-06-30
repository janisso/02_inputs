from multiprocessing import Process, Manager
from time import sleep

def f(process_number):
    try:
        print "starting thread: ", process_number
        while True:
            print process_number
            sleep(3)
    except KeyboardInterrupt:
        print "Keyboard interrupt in process: ", process_number
    finally:
        print "cleaning up thread", process_number

if __name__ == '__main__':

    processes = []

    manager = Manager()

    for i in xrange(4):
        p = Process(target=f, args=(i,))
        p.start()
        processes.append(p)

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print "Keyboard interrupt in main"
    finally:
        print "Cleaning up Main"