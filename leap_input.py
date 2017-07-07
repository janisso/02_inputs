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



#SENDING OSC MESSAGES
def oscSendI(unravelTime,stop_all):
    #SETTING UP OSC CLIENT FOR INSCORE
    cI = OSC.OSCClient()
    cI.connect(('localhost', 7000))   # INSCORE
    oscmsgI = OSC.OSCMessage()
    oscmsgI.setAddress('/ITL/scene/sync')
    oscmsgI.append('cursor')
    oscmsgI.append('score')
    cI.send(oscmsgI)
    while True:
        #msg2send = oscQ.get()
        oscmsgI = OSC.OSCMessage()
        oscmsgI.setAddress('/ITL/scene/cursor')
        oscmsgI.append('date')
        oscmsgI.append(int(unravelTime.value*4))
        oscmsgI.append(16)
        #oscmsg.append(str(msg2send)+' '+str(16))
        cI.send(oscmsgI)
        time.sleep(0.01)
        if stop_all.value == 1:
            cI.close()
            break

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

#SET UP WINDOW LENGTH AND HOP SIZE FOR REGRESSION
window_length = 400
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
f = 0.001
coeffs = signal.firwin(window_length, f)

#SET UP CIRCULAR BUFFER FOR FIR FILTER
cb = CircularBuffer(size=window_length)
for i in range(window_length):
    cb.append(0)

#REGRESSION CLASS
class REG():
    def __init__(self):
        self.est_frac = 0#3/(1000/(2*np.pi))
        self.est_phase = 0
        self.est_std = 250
        self.prev_std = 0
        self.counts = 0
        self.prev_phase = 0

    def doReg(self,q,u_phase,q1,amp,stop_all,savePath):
        f = open(savePath+'/do_reg.csv','w+')
        f.write('time,est_amp,est_freq,est_phase\n')
        while True:
            if not q.empty():
                start = time.time()
                yo = q.get()
                data = yo[0]
                #print data
                nr = yo[1]
                guess_std = self.est_std
                guess_phase = self.est_phase + self.est_frac*50
                guess_frac = self.est_frac
                optimize_func = lambda x: x[0]*np.sin(t*x[1]+x[2]) - data
                #self.est_std, self.est_frac, self.est_phase = least_squares(optimize_func, [guess_std, guess_frac, guess_phase],bounds=([0,0,self.est_phase],[1500,5,self.est_phase+np.pi/2]),max_nfev=100).x
                self.est_std, self.est_frac, self.est_phase = least_squares(optimize_func, [guess_std, guess_frac, guess_phase],bounds=([0,0,self.est_phase],[1500,0.05,np.inf]),max_nfev=50).x
                if (self.est_phase < self.prev_phase) or (self.est_phase > self.prev_phase+np.pi):
                    #self.est_phase = self.prev_phase
                    self.est_phase = u_phase.value
                if (self.est_std > 1200):
                    self.est_std = self.prev_std
                amp.value = self.est_std
                #print amp.value
                #print amp.value
                self.prev_std = self.est_std
                self.prev_phase = self.est_phase
                self.prev_frac = self.est_frac
                q1.put(self.est_phase)
                #data_fit = self.est_std*np.sin(t*self.est_frac+self.est_phase)        
                #self.inv_phase = np.arcsin(data_fit[-1]/self.est_std)
                end = time.time()
                #print self.est_phase, nr
                #print self.est_phase, self.counts, end-start,nr
                #if end-start > 0.05:
                #    print 'LONGER THAN 50ms'
                f.write("%f, %f, %f, %f\n"%(time.time(),self.est_std,self.est_frac,self.est_phase))
                self.counts+=1
            if stop_all.value == 1:
                f.close
                break

class dummy():
    def __init__(self):
        self.x = 0
        self.y = 0
    def do_array(time,data):
        self.x = sum(time)
        self.y = sum(data)
        print self.x, self.y

def getSamples(vel,playbackFlag,stop_all,savePath):
    f = open(savePath+'/get_samples.csv','w+')
    f.write('time,palm_pos,palm_vel,span\n')
    controller = Leap.Controller()
    #prevTime = time.time()
    palm_pos = 0
    hand_span = 500
    while True:
        frame = controller.frame()
        for hand in frame.hands:
            #GETTING PALM VELOCITY
            palm_pos = hand.palm_position.y
            vel.value = hand.palm_velocity.y
            #print hand.fingers[0].position
            for finger in hand.fingers:
                if finger.type == 0:
                    thumb_pos = finger.tip_position
                if finger.type == 4:
                    pinky_pos = finger.tip_position
            hand_span = np.sqrt((thumb_pos.x-pinky_pos.x)**2+(thumb_pos.y-pinky_pos.y)**2+(thumb_pos.z-pinky_pos.z)**2)
            if (hand_span > 80) and (playbackFlag.value==0):
                playbackFlag.value = 1
        f.write("%f, %f, %f, %f\n"%(time.time(),palm_pos,vel.value,hand_span))
        sleep(0.01)
        if stop_all.value == 1:
            f.close
            break

#GATHERING THE DATA FROM LEAP MOTION
def runLeap(q,vel,u_phase,unravelTime,stop_all,savePath):
    f = open(savePath+'/run_leap.csv','w+')
    f.write('time,palm_vel,avg_vel,avg_vel_s,avg_acc,avg_acc_s,sparse_phase,window_time\n')
    #controller = Leap.Controller()
    #uPhase = 0
    #vel = 0
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
    #reg_hop = 0
    while True:
        cb.append(vel.value)
        #print vel.value
        #GETTING SMOOTHED VALUE
        avg_vel = sum(cb*coeffs)
        avg_velS = schmit(avg_vel,100)
        #oscSend(avg_vel,"/vel")

        #GETTING ACCELERAION
        avg_acc = (avg_vel - prev_vel)*100
        avg_accS = schmit(avg_acc,150)
        #oscSend(avg_acc,"/acc")
        #VERIFICATION MODULE
        if ((avg_accS*prev_accS<0) and (flag == 0) and (avg_velS>0) and (timer_ting < 0)):
            flag = 1
            timer_ting = 10
            u_phase.value+=np.pi/2
            #unravelTime.value = u_phase.value/(np.pi*2)
            #print 'Phase is ', u_phase.value
            #oscSend(flag,"/flag")
        if ((avg_velS*prev_velS<0) and (flag == 1) and (timer_ting < 0)):
            flag = 2
            timer_ting = 10
            u_phase.value+=np.pi/2
            #unravelTime.value = u_phase.value/(np.pi*2)
            #print 'Phase is ', u_phase.value
            #oscSend(flag,"/flag")
        if ((avg_accS*prev_accS<0) and (flag == 2) and (avg_velS<0) and (timer_ting < 0)):
            flag = 3
            timer_ting = 10
            u_phase.value+=np.pi/2
            #unravelTime.value = u_phase.value/(np.pi*2)
            #print 'Phase is ', u_phase.value
            #oscSend(flag,"/flag")
        if ((avg_velS*prev_velS<0) and (flag == 3) and (timer_ting < 0)):
            flag = 0
            timer_ting = 10
            u_phase.value+=np.pi/2
            #unravelTime.value = u_phase.value/(np.pi*2)
            #print 'Phase is ', u_phase.value
            #oscSend(flag,"/flag")
        #print u_phase.value
        timer_ting -= 1

        #SETTING PREVIOUS VALUE TO CURRENT
        prev_vel = avg_vel
        #amp.value = avg_vel
        prev_velS = avg_vel
        prev_acc = avg_acc
        prev_accS = avg_acc
        
        #FILLING UP CBREG
        #cbTam.append(array_time)
        #cbReg.append(vel.value)
        #f.write('time,palm_vel,avg_vel,avg_vel_s,avg_acc,avg_acc_s,sparse_phase,window_time\n')
        f.write("%f, %f, %f, %f,%f, %f, %f, %f\n"%(time.time(),vel.value,avg_vel,avg_velS,avg_acc,avg_accS,u_phase.value,window_time))
        cbReg.append(vel.value)
        sent_to = 0
        if window_time==50:
            window_time=0
            for i in range(window_length):
                #t[i]=cbTam[i]
                data[i]=cbReg[i]
            #qT.put(t)
            q.put((data,hello))
            sent_to = 1
        window_time+=1
        #print hello, vel
        #array_time+=0.001
        hello+=1
        sleep(0.0005)
        if stop_all.value == 1:
            f.close
            break


def printPhase(q1,vel,unravelTime,u_phase,playbackFlag,stop_all,savePath):
    f = open(savePath+'/print_phase.csv','w+')
    f.write('time,phase_from_reg,plbck_pos,corrected_plbck_pos\n')
    #header_text = ['Time in S','Phase from Regression','Difference in Beats','Beats sent to Playback']
    preffP = 0
    curr_time = time.time()
    prev_time = time.time()
    #time_diff = 0
    curr_date = 0
    prev_date = 0
    temp_date = 0
    prev_temp_date = temp_date
    #date_diff = 0
    while True:
        if not q1.empty():
            fP = q1.get()
            #if fP > u_phase.value:
            #    fP = u_phase.value
            #print fP
            curr_time = time.time()
            curr_date = fP/(2*np.pi)
            time_diff = curr_time - prev_time
            date_diff = curr_date - prev_date
            #print playbackFlag.value
            if playbackFlag.value==1:
                temp_date += date_diff
            if temp_date > u_phase.value+0.25:
                temp_date = u_phase.value
            #qI.put([prev_time,curr_time,prev_date,curr_date])
            #unravelTime.value = curr_date
            #if (unravelTime.value + date_diff) > u_phase.value:
            #unravelTime.value = unravelTime.value + date_diff
            #temp_date_diff = temp_date - prev_temp_date
            unravelTime.value = temp_date
            #print unravelTime.value,u_phase.value/(2*np.pi)
            #print unravelTime.value
            #loopThis = int((time_diff)*1000)
            #increment = date_diff/loopThis
            #for i in range(loopThis):
            #    unravelTime.value+=increment
            #    #sleep(0.001)
            #print curr_date,time_diff, date_diff, loopThis
            prev_time = curr_time
            prev_date = curr_date
            f.write("%f, %f, %f, %f\n"%(time.time(),fP,curr_date,temp_date))
        if stop_all.value == 1:
            break

def playMIDI(unravelTime,amp,stop_all,which_one,savePath,g):

    path = '/Users/mb/Desktop/Janis.So/06_qmul/BB/02_inputs/inscore_stuff/main_menu/l_'+str(g)+'/'
    f = open(savePath+'/play_midi.csv','w+')
    f.write('time,phase,midi_note,midi_vel\n')
    mids = ['demo','01','02','03','04','05','06']
    #times = [45]

    mid = MidiFile(path+mids[which_one]+'.mid')
    s_times = []#np.zeros((times[0],2))
    #print mido.get_output_names()
    #mid = MidiFile('/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/schubert_impromptu.mid')
    #mid = MidiFile('/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/grade_1_1.mid')
    #mid = MidiFile('/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/polonaise.mid')
    #mid = MidiFile('/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/moonlight.mid')
    #mid = MidiFile('/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/lalaland.mid')
    port = mido.open_output(mido.get_output_names()[0])
    all_time = 0
    msg_count = 0
    all_messages = []
    #s_times = np.zeros((904,2))
    #s_times = np.zeros((34,2))
    #s_times = np.zeros((1013,2))
    #s_times = np.zeros((2266,2))
    #s_times = np.zeros((1134,2))
    for msg in mid:
        all_time += msg.time
        if not msg.is_meta:
            all_time+=msg.time
            all_messages.append(msg)
            s_times.append([msg_count,all_time])
            msg_count += 1
    s_times = np.array(s_times)
    yo = deepcopy(s_times)
    while True:
        if len(yo)!=0:
            #print 'hello',yo[0,1],unravelTime.value
            #print yo[0,1],'dfsdfsdfsdfsdfs',unravelTime.value
            if yo[0,1]<unravelTime.value:
                #print 'hello'
                bim = amp.value
                #oscSend(str(int(unravelTime.value*4)))
                midiVel = int(abs(bim)/1200*127)
                if midiVel > 127:
                    midiVel = 127
                msgMIDI = all_messages[int(yo[0,0])]
                msgMIDI.velocity = midiVel
                f.write("%f, %f, %f, %f\n"%(time.time(),unravelTime.value,all_messages[int(yo[0,0])].note,midiVel))
                #print msgMIDI.velocity,midiVel
                port.send(msgMIDI)
                #oscSend(int(unravelTime.value*4))
                #print 'Play Midi ',unravelTime.value, all_messages[int(yo[0,0])]
                msg_count += 1
                yo = np.delete(yo,0,0)
        else:
            f.close
            stop_all.value = 1
            'Print MIDI Playback Finished'
            break

# def interPol(qI,unravelTime):
#     while True:
#         if not qI.empty():
#             data = qI.get()
#             prev_time = data[0]
#             curr_time = data[1]
#             prev_date = data[2]
#             curr_date = data[3]
#             unravelTime.value = prev_date
#             loopThis = int((curr_time - prev_time)*1000)
#             increment = (curr_date - prev_date)/loopThis
#             #print increment
#             #print 'YOooooooooooooooo'
#             #for i in range(loopThis):
#             #    unravelTime.value+=increment
#             #    #print unravelTime.value
#             #    sleep(0.001)

'''def printNumber2(q):
    while True:
        if not q.empty():
            x = q.get()
            print "Printing 2 "+str(x)
            sleep(0.1)'''

def doIt(savePath,which_one,g):
    r = REG()
    q = multiprocessing.Queue()
    q1 = multiprocessing.Queue()
    #qI = multiprocessing.Queue()
    amp = multiprocessing.Value('d', 0.0)
    playbackFlag = multiprocessing.Value('i', 0)
    vel = multiprocessing.Value('d', 0.0)
    u_phase = multiprocessing.Value('d', 0.0)
    unravelTime = multiprocessing.Value('d',0.0)
    stop_all = multiprocessing.Value('i', 0)
    lock=multiprocessing.Lock()
    p0 = multiprocessing.Process(target=playMIDI,args=(unravelTime,amp,stop_all,which_one,savePath,g))
    p1 = multiprocessing.Process(target=runLeap,args=(q,vel,u_phase,unravelTime,stop_all,savePath))
    p2 = multiprocessing.Process(target=r.doReg,args=(q,u_phase,q1,amp,stop_all,savePath))
    p3 = multiprocessing.Process(target=getSamples,args=(vel,playbackFlag,stop_all,savePath))
    p4 = multiprocessing.Process(target=printPhase,args=(q1,vel,unravelTime,u_phase,playbackFlag,stop_all,savePath))
    p5 = multiprocessing.Process(target=oscSendI,args=(unravelTime,stop_all))
    #p6 = multiprocessing.Process(target=interPol,args=(qI,unravelTime))
    p0.start()
    sleep(0.5)
    p3.start()
    p1.start()
    p2.start()
    p4.start()
    p5.start()
    #p6.start()
    p0.join()
    sleep(0.5)
    p3.join()
    p1.join()
    p2.join()
    p4.join()
    p5.join()
    #p6.join()

#if __name__ == "__main__":
#    doIt()