import mido
from mido import MidiFile
import time
import numpy as np
import multiprocessing
from copy import deepcopy
import OSC


mid = MidiFile('/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/lalaland.mid')
port = mido.open_output(mido.get_output_names()[0])
all_time = 0
msg_count = 0
all_messages = []
#slave_times = np.zeros((1013,2))

for msg in mid:
    all_time += msg.time
    if not msg.is_meta:
        all_time+=msg.time
        all_messages.append(msg)
        #slave_times[msg_count]=[msg_count,all_time]
        msg_count += 1

'''for i in range(len(master_times)):
    if slave_times[0,1]<master_times[i]:
        port.send(all_messages[int(slave_times[0,0])])
        slave_times = np.delete(slave_times,0,0)
    time.sleep(0.001)'''

#SETTING UP OSC CLIENT FOR INSCORE
#cI = OSC.OSCClient()
#cI.connect(('localhost', 7000))   # connect to SuperCollider
#oscmsgI = OSC.OSCMessage()
#oscmsgI.setAddress('/ITL/scene/sync')
#oscmsgI.append('cursor')
#oscmsgI.append('score')
#cI.send(oscmsg)

#SENDING OSC MESSAGES
def oscSendI(unravelTime):
    while True:
        #msg2send = oscQ.get()
        oscmsgI = OSC.OSCMessage()
        oscmsgI.setAddress('/ITL/scene/cursor')
        oscmsgI.append('date')
        oscmsgI.append(int(unravelTime.value*4))
        oscmsgI.append(16)
        #oscmsg.append(str(msg2send)+' '+str(16))
        #cI.send(oscmsgI)
        time.sleep(0.01)

def keepTime(unravelTime):
    while unravelTime.value<90:
        unravelTime.value+=0.005
        #print unravelTime.value
        time.sleep(0.001)
        #oscQ.put(unravelTime.value)

def playMIDI(unravelTime):
    mid = MidiFile('/Users/mb/Desktop/Janis.so/06_qmul/BB/02_inputs/schubert_impromptu.mid')
    port = mido.open_output(mido.get_output_names()[0])
    all_time = 0
    msg_count = 0
    all_messages = []
    slave_times = np.zeros((904,2))
    
    for msg in mid:
        all_time += msg.time
        if not msg.is_meta:
            all_time+=msg.time
            all_messages.append(msg)
            slave_times[msg_count]=[msg_count,all_time]
            msg_count += 1
        
    yo = deepcopy(slave_times)
    print yo[0,1],'dfsdfsdfsdfsdfs'
    while len(yo)!=0:
        if yo[0,1]<unravelTime.value:
            #oscSend(str(int(unravelTime.value*4)))
            port.send(all_messages[int(yo[0,0])])
            #oscSend(int(unravelTime.value*4))
            #print 'Play Midi ',unravelTime.value, all_messages[int(yo[0,0])]
            yo = np.delete(yo,0,0)

'''vel = 0
for msg in mid:
    time.sleep(msg.time)
    if not msg.is_meta:
        print msg.time
        msg.velocity = vel
        port.send(msg)
        vel = (vel+1)%127'''

'''master_array = np.arange(1,2001)
slave_array = np.linspace(0,2000,1972)

for i in range(len(master_array)):
    print master_array[i]
    if slave_array[0] < master_array[i]:
        print slave_array[0]
        slave_array = np.delete(slave_array,0)
    time.sleep(0.001)'''

if __name__ == "__main__":

    #q = multiprocessing.Queue()

    #lock=multiprocessing.Lock()

    #pool = multiprocessing.Pool(initializer=)
    unravelTime = multiprocessing.Value('d',0.0)
    #oscQ = multiprocessing.Queue()
    
    p1 = multiprocessing.Process(target=keepTime,args=(unravelTime,))
    p2 = multiprocessing.Process(target=playMIDI,args=(unravelTime,))
    #p3 = multiprocessing.Process(target=oscSend,args=(unravelTime,))
    
    p2.start()
    time.sleep(0.5)
    p1.start()
    #p3.start()
    
    p2.join()
    time.sleep(0.5)
    p1.join()
    #p3.join()