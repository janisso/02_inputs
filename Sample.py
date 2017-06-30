#!/usr/bin/env python2.7
import sys
import Leap
import multiprocessing
from multiprocessing import Pool
from time import sleep

import argparse
import random

from pythonosc import osc_message_builder
from pythonosc import udp_client

#v = multiprocessing.Value('d',)

'''class OSC:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",
            help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=5005,
            help="The port the OSC server is listening on")
        args = parser.parse_args()
        self.client = udp_client.SimpleUDPClient(args.ip, args.port)

    def oscSend(q):
        self.client.send_message("/filter", q)'''

def runLeap(q):
    invalid = True
    controller = Leap.Controller()
    while invalid:
        frame = controller.frame()
        for hand in frame.hands:
            handType = "Left hand" if hand.is_left else "Right hand"
            #print "  %s, id %d, position: %s" % (
            #    handType, hand.id, hand.palm_position.y)
            #scSend(hand.palm_position.y)
            q.put(hand.palm_position.y)
            print "LeapMotion "+str(hand.palm_position.y)
        sleep(0.01)
    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass

'''def getNumber(q):
    x = 0
    invalid = True
    while invalid:
        x+=1
        if x > 100:
            x = 0
        sleep(0.1)
        q.put(x)
        print "Putting "+str(x)'''

def printNumber(q):
    while True:
        if not q.empty():
            x = q.get()
            print "Printing   "+str(x)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1",
        help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005,
        help="The port the OSC server is listening on")
    args = parser.parse_args()
    client = udp_client.SimpleUDPClient(args.ip, args.port)

    #v = multiprocessing.Value('d',)
    #p = Pool()
    #p.map()

    q = multiprocessing.Queue()

    p1 = multiprocessing.Process(target=runLeap,args=(q,))
    p2 = multiprocessing.Process(target=printNumber,args=(q,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()