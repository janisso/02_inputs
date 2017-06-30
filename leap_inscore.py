def getSamples(vel,playbackFlag):
    controller = Leap.Controller()
    #prevTime = time.time()
    while True:
        frame = controller.frame()
        for hand in frame.hands:
            #GETTING PALM VELOCITY
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
            #print hand_span,playbackFlag.value
            #    print "  finger, id: %d, length: %fmm, width: %fmm" % (
            #        #self.finger_names[finger.type],
            #        finger.id,
            #        finger.length,
            #        finger.width)
            #print vel.value
            #oscSendP(hand.palm_position.y,'/position')
            #PUTTOMG VALUE IN CIRCULAR BUGGER
        #currTime = time.time()
        #timeDiff = currTime - prevTime
        #prevTime = currTime
        sleep(0.01)
        #print timeDiff, vel.value