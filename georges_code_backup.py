import multiprocessing
import threading
from time import sleep
import sys
#import getch
import os
import subprocess
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
import leap_input

import argparse

#FUNCTION TO SEND OSC MESSAGES TO INSCORE
def oscSendI(address,var):
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
    while True:
        frame = controller.frame()
        for hand in frame.hands:
            #GETTING PALM VELOCITY
            x = hand.palm_position.x
            y = hand.palm_position.y
            for finger in hand.fingers:
                if finger.type == 0:
                    thumb_pos = finger.tip_position
                if finger.type == 2:
                    pinky_pos = finger.tip_position
            hand_span = np.sqrt((thumb_pos.x-pinky_pos.x)**2+(thumb_pos.y-pinky_pos.y)**2+(thumb_pos.z-pinky_pos.z)**2)
            x_pos = x/150
            y_pos = (y-200)/200*(-1)
        print hand_span
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
            flag = 0
        #THIS IF STATEMENT FOR CHOOSING A BUTTON
        if (flag == 1) and (hand_span< 60):
            break
        sleep(0.05)



def retryMenu(retry):
    controller = Leap.Controller()
    flag = 0
    x_pos = 0
    y_pos = 0
    hand_span = 65
    oscSendI('/ITL/scene/textQ',['set', 'txt', 'Finish'])
    oscSendI('/ITL/scene/textQ',['fontSize',64])
    oscSendI('/ITL/scene/textQ',['x',0.5])
    oscSendI('/ITL/scene/textQ',['y',0])
    oscSendI('/ITL/scene/textQ',['alpha',0])

    oscSendI('/ITL/scene/textR',['set','txt','Retry'])
    oscSendI('/ITL/scene/textR',['fontSize',64])
    oscSendI('/ITL/scene/textR',['x',-0.5])
    oscSendI('/ITL/scene/textR',['y',0])
    oscSendI('/ITL/scene/textR',['alpha',0])

    oscSendI('/ITL/scene/menuBall1',['set','ellipse',0.5,0.5])
    oscSendI('/ITL/scene/menuBall1',['color',0,0,255])

    while True:
        frame = controller.frame()
        for hand in frame.hands:
            #GETTING PALM VELOCITY
            x = hand.palm_position.x
            y = hand.palm_position.y
            for finger in hand.fingers:
                if finger.type == 0:
                    thumb_pos = finger.tip_position
                if finger.type == 2:
                    pinky_pos = finger.tip_position
            hand_span = np.sqrt((thumb_pos.x-pinky_pos.x)**2+(thumb_pos.y-pinky_pos.y)**2+(thumb_pos.z-pinky_pos.z)**2)
            x_pos = x/150
            y_pos = (y-200)/200*(-1)
        print x_pos, y_pos#hand_span
        oscSendI('/ITL/scene/menuBall1',['x',x_pos])
        oscSendI('/ITL/scene/menuBall1',['y',y_pos])
        oscSendI('/ITL/scene/menuBall1',['scale',(hand_span-40)/100])

        #THIS IF STATEMENT INSIDE THE RETRY BUTTON
        if (((-1) < x_pos < 0) and (-0.5 < y_pos < 0.5)) and (flag != 1):#(-0.5 < y_pos < 0.5)) and (flag == 0):
            print 'in R'
            oscSendI('/ITL/scene/buttonR',['effect','none'],)
            oscSendI('/ITL/scene/menuBall1',['alpha',127])
            oscSendI('/ITL/scene/buttonQ',['effect','blur',32])
            oscSendI('/ITL/scene/textR',['alpha',255])
            oscSendI('/ITL/scene/textQ',['alpha',0])
            #print 'in'
            flag = 1

        #THIS IF STATEMENT INSIDE THE QUIT BUTTON
        if ((1 > x_pos > 0) and (-0.5 < y_pos < 0.5)) and (flag != 2):#(-0.5 < y_pos < 0.5)) and (flag == 0):
            print 'in Q'
            oscSendI('/ITL/scene/buttonQ',['effect','none'],)
            oscSendI('/ITL/scene/menuBall1',['alpha',127])
            oscSendI('/ITL/scene/buttonR',['effect','blur',32])
            oscSendI('/ITL/scene/textR',['alpha',0])
            oscSendI('/ITL/scene/textQ',['alpha',255])
            #print 'in'
            flag = 2

        #THIS STATEMENT FOR OUTSIDE OF BUTTONS
        if ((y_pos < (-0.5)) or (y_pos > 0.5)) and (flag != 3):
            oscSendI('/ITL/scene/buttonR',['effect','blur',32])
            oscSendI('/ITL/scene/buttonQ',['effect','blur',32])
            oscSendI('/ITL/scene/textR',['alpha',0])
            oscSendI('/ITL/scene/textQ',['alpha',0])
            flag = 3

        #THIS IF STATEMENT FOR CHOOSING A BUTTON
        if (flag == 1) and (hand_span< 60):
            retry.value = 0
            break
        if (flag == 2) and (hand_span< 60):
            retry.value = 1
            break
        sleep(0.05)



def worker1(name):
    i =0
    while True:
        #print i
        if i == 5:
            break #terminate this worker
        i+=1
        sleep(0.1)
    return



def worker2(name):
    i = 0
    while True:
        #print i
        if i == 10:
            break #terminate this worker
        i+=1
        sleep(0.1)
    return



def worker3(name):
    i = 0
    while True:
        #print i
        if i == 15:
            break #terminate this worker
        i+=1
        sleep(0.1)
    return



def launcher(jobs,select):
    if select==1 :
        p = multiprocessing.Process(target=worker1, args=('fancy process',))
    elif select==2 :
        p = multiprocessing.Process(target=worker2, args=('boring process',))
    elif select==3 :
        p = multiprocessing.Process(target=worker3, args=('booring process',))
    else:
        return
    jobs.append(p)
    p.start()



def relaunch():
    jobs = []
    launcher(jobs,2)
    launcher(jobs,1)
    launcher(jobs,3)
    for proc in jobs:
        proc.join()
    return jobs
    print 'OK.'

if __name__ == '__main__':

    #PARSED ARGUMENTS
    path = '/Users/mb/Desktop/Janis.So/06_qmul/BB/05_data/'

    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--userid',help='Enter user ID')
    parser.add_argument('-g','--grade',help='Enter level of the pianist (1-8 ABRSM grades)')
    parser.add_argument('-e','--excerpts',help='Enter two excerpts that will be practised')
    #parser.add_argument('-l','--level',help='Enter level of the pianist (1-8 ABRSM grades)')
    args = parser.parse_args()

    #print args.group
    g = int(args.grade)
    # if g == 1:
    #     savePath = path+'G1/'+args.userid
    # elif g == 2:
    #     savePath = path+'G2/'+args.userid
    if g > 8:
        print 'Enter level of the pianist (1-8 ABRSM grades)'
        sys.exit(-1)
    elif g == 0:
        print 'Enter level of the pianist (1-8 ABRSM grades)'
        sys.exit(-1)
    else:
        savePath = path+'G'+str(g)+'/'+args.userid

    # print savePath
    if not os.path.exists(savePath):
         os.makedirs(savePath)

    e = [0]
    for i in range(len(args.excerpts)):
        e.append(int(args.excerpts[i]))
    #print e

    titles = ['demo','e1','e2','e3','e4','e5','e6']

    #BEGIN DEMO
    retry = multiprocessing.Value('i',0)
    os.system('open /Applications/INScoreViewer-1.21.app')
    sleep(2)
    #SETTING UP OSC CLIENT FOR INSCOR
    cI = OSC.OSCClient()
    cI.connect(('localhost', 7000))   # INSCORE
    sleep(3)
    oscSendI('/ITL/scene',['load','/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/menu.inscore'])
    sleep(1)
    os.system('open -a Terminal')
    p0 = multiprocessing.Process(target=demoMenu,args=())
    p0.start()
    p0.join()
    os.system('open /Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/demo.inscore')
    os.system('open -a Terminal')
    for i in range(3,0,-1):
        oscSendI('/ITL/scene/demoText1',['set', 'txt', i])
        print 'Play in '+str(i)
        sleep(1)
    oscSendI('/ITL/scene/demoText1',['alpha',0])
    cI.close()
    #os.system('open -a Terminal')

    count = 0
    saveHere = savePath+'/0_'+str(titles[e[0]])+'/'+str(count)
    if not os.path.exists(saveHere):
        os.makedirs(saveHere)
    #print count
    os.system('open -a Terminal')
    leap_input.doIt(saveHere,e[0],g)
    #relaunch()
    
    #FINISH / RETRY WINDOW
    while True:
    	cI = OSC.OSCClient()
    	cI.connect(('localhost', 7000))   # INSCORE
        oscSendI('/ITL/scene',['load','/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/retry_quit.inscore'])
        os.system('open -a Terminal')
        p0 = multiprocessing.Process(target=retryMenu,args=(retry,))
        p0.start()
        p0.join()
        oscSendI('/ITL/scene/*','del')
        if retry.value == 0:
            count += 1
            saveHere = savePath+'/0_'+str(titles[e[0]])+'/'+str(count)
            if not os.path.exists(saveHere):
                os.makedirs(saveHere)
            os.system('open /Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/demo.inscore')
            for i in range(3,0,-1):
                oscSendI('/ITL/scene/demoText1',['set', 'txt', i])
                oscSendI('/ITL/scene/demoText1',['fontSize', 64])
                #oscSendI('/ITL/scene/demoText1',['alpha',255])
                print 'Play in '+str(i)
                sleep(1)
            oscSendI('/ITL/scene/demoText1',['alpha',0])
            os.system('open -a Terminal')
            leap_input.doIt(saveHere,e[0],g)
            os.system('open -a Terminal')
            #relaunch()
        if retry.value == 1:
            break

    for j in range(1,7):
        #BEGIN PRACTICE
        oscSendI('/ITL/scene',['load','/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/begin_practice.inscore'])
        oscSendI('/ITL/scene/demoText',['set','txt', 'Begin Practicing '+str(e[j])])
        oscSendI('/ITL/scene/demoText',['fontSize',64])
        oscSendI('/ITL/scene/demoText',['alpha',0])
        sleep(1)
        os.system('open -a Terminal')
        p0 = multiprocessing.Process(target=demoMenu,args=())
        p0.start()
        p0.join()
        os.system('open /Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/l_'+str(g)+'/0'+str(e[j])+'.inscore')
        os.system('open -a Terminal')
        for i in range(3,0,-1):
            oscSendI('/ITL/scene/demoText1',['set', 'txt', i])
            print 'Play in '+str(i)
            sleep(1)
        oscSendI('/ITL/scene/demoText1',['alpha',0])
        count = 0
        saveHere = savePath+'/'+str(j)+'_'+str(titles[e[j]])+'/'+str(count)
        if not os.path.exists(saveHere):
            os.makedirs(saveHere)
        os.system('open -a Terminal')
        leap_input.doIt(saveHere,e[j],g)
        os.system('open -a Terminal')

        #FINISH / RETRY WINDOW
        while True:
            oscSendI('/ITL/scene',['load','/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/retry_quit.inscore'])
            os.system('open -a Terminal')
            p0 = multiprocessing.Process(target=retryMenu,args=(retry,))
            p0.start()
            p0.join()
            oscSendI('/ITL/scene/*','del')
            if retry.value == 0:
                count += 1
                saveHere = savePath+'/'+str(j)+'_'+str(titles[e[j]])+'/'+str(count)
                if not os.path.exists(saveHere):
                    os.makedirs(saveHere)
                os.system('open /Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/l_'+str(g)+'/0'+str(e[j])+'.inscore')
                for i in range(3,0,-1):
                    oscSendI('/ITL/scene/demoText1',['set', 'txt', i])
                    oscSendI('/ITL/scene/demoText1',['fontSize', 64])
                    #oscSendI('/ITL/scene/demoText1',['alpha',255])
                    print 'Play in '+str(i)
                    sleep(1)
                oscSendI('/ITL/scene/demoText1',['alpha',0])
                os.system('open -a Terminal')
                leap_input.doIt(saveHere,e[j],g)
                os.system('open -a Terminal')
            if retry.value == 1:
                break

    os.system('open /Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/inscore_stuff/main_menu/good_bye.inscore')
    for i in range(10,0,-1):
        sleep(1)
    subprocess.call(['osascript', '-e', 'quit app "/Applications/INScoreViewer-1.21.app"'])
    sys.exit(-1)