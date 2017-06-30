import sys
import Leap
import multiprocessing
from time import sleep
import OSC
from scipy import signal
from collections import deque
import numpy as np
import time
from scipy.optimize import least_squares
from copy import deepcopy
import mido
from mido import MidiFile



#SETTING UP OSC CLIENT FOR INSCORE
cI = OSC.OSCClient()
cI.connect(('localhost', 7000))   # INSCORE

#FUNCTION TO SEND OSC MESSAGES TO INSCORE
def oscSendI(address,var):
    #msg2send = oscQ.get()
    oscmsgI = OSC.OSCMessage()
    oscmsgI.setAddress(address)
    for i in range(len(var)):
        oscmsgI.append(var[i])
    cI.send(oscmsgI)

#FUNCTION TO COLLECT LEAP MOTION DATA FOR NAVIGATION
def demoMenu():
    controller = Leap.Controller()
    flag = 0
    x_pos = 0
    y_pos = 0
    hand_span = 65
    oscSendI('/ITL/scene/button',['alpha',255])
    oscSendI('/ITL/scene/menuBall',['alpha',255])
    oscSendI('/ITL/scene/demoText',['set', 'txt', 'Demo'])
    oscSendI('/ITL/scene/demoText',['fontSize', 32])
    oscSendI('/ITL/scene/demoText',['alpha',0])
    while True:
        frame = controller.frame()
        for hand in frame.hands:
            #GETTING PALM VELOCITY
            x = hand.palm_position.x
            y = hand.palm_position.y
            for finger in hand.fingers:
                if finger.type == 0:
                    thumb_pos = finger.tip_position
                if finger.type == 4:
                    pinky_pos = finger.tip_position
            hand_span = np.sqrt((thumb_pos.x-pinky_pos.x)**2+(thumb_pos.y-pinky_pos.y)**2+(thumb_pos.z-pinky_pos.z)**2)
            x_pos = x/150
            y_pos = (y-200)/200*(-1)
        print hand_span
        #f.write('%f, %f, %f, %f\n' % (time.time(),x,y,hand_span))
        oscSendI('/ITL/scene/menuBall',['x',x_pos])
        oscSendI('/ITL/scene/menuBall',['y',y_pos])
        oscSendI('/ITL/scene/menuBall',['scale',(hand_span-40)/100])
        #THIS IF STATEMENT INSIDE THE BUTTON
        if (-0.5 < x_pos < 0.5) and (-0.5 < y_pos < 0.5) and (flag == 0):
            oscSendI('/ITL/scene/button',['effect','none'],)
            oscSendI('/ITL/scene/menuBall',['alpha',127])
            oscSendI('/ITL/scene/demoText',['alpha',255])
            #print 'in'
            flag = 1
        #THIS IF STATEMENT OUTSIDE THE BUTTON
        if ((x_pos < (-0.5)) or (x_pos > (0.5))) or ((y_pos < (-0.5)) or (y_pos > (0.5))) and (flag == 1):
            oscSendI('/ITL/scene/button',['effect','blur',32])
            oscSendI('/ITL/scene/menuBall',['alpha',255])
            oscSendI('/ITL/scene/demoText',['alpha',0])
            #print 'out'
            flag = 0
        #THIS IF STATEMENT FOR CHOOSING A BUTTON
        if (flag == 1) and (hand_span< 60):
            oscSendI('/ITL/scene/button',['alpha',0])
            oscSendI('/ITL/scene/menuBall',['alpha',0])
            oscSendI('/ITL/scene/demoText',['alpha',0])
            break
        sleep(0.05)

if __name__ == "__main__":
	p0 = multiprocessing.Process(target=demoMenu,args=())
	p0.start()
	p0.join()