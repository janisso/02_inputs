import tkMessageBox
import Tkinter as root
import os

class  Canvas(object):
    window = None
    def __init__(self, id, title,width,height):
        self.window = root.Tk()
        self.window.title(title)
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        x = (ws/2) - (width/2)    
        y = (hs/2) - (height/2)
        self.window.geometry('%dx%d+%d+%d' % (width, height, x, y))
        
    def show(self):
        self.window.mainloop()
        return

    def add(self,widget):
        widget_type = widget.Type
        if(widget_type == "Button" or isinstance(widget,Button) ):
            frame = self.abs_frame(widget)
            widget.controller = root.Button(frame, text=widget.title, command=widget.callbackMethod)
            widget.controller.pack(fill=root.BOTH, expand=1)

        elif(widget_type == "TextArea" or isinstance(widget,TextArea) ):
            frame = self.abs_frame(widget)
            widget.controller = root.Text(frame)
            widget.controller.pack(fill=root.BOTH, expand=1)
            widget.controller.insert(root.INSERT,widget.text)

        elif(widget_type == "Label"  or isinstance(widget,Label) ):
            temp = widget.label_var
            widget.label_var = root.StringVar()
            widget.label_var.set(temp)
            frame = self.abs_frame(widget)
            widget.controller = root.Label(frame, textvariable=widget.label_var)
            widget.controller.pack(fill=root.BOTH, expand=1)

        # elif(widget_type == "CheckBox" or isinstance(widget,CheckBox) ):
        #     frame = self.abs_frame(widget)
        #     var = widget.value 
        #     widget.value = root.IntVar()
        #     if(var):
        #         widget.value.set(1)
        #     else:
        #         widget.value.set(0)
        #     widget.controller = root.Checkbutton(frame, text=widget.title, variable=widget.value, onvalue=1, offvalue=0)
        #     widget.controller.grid(sticky=root.W)
        #     if(widget.value):
        #         widget.controller.select()
        #     else:
        #         widget.controller.deselect()

        elif(widget_type == "RadioGroup" or isinstance(widget,RadioGroup) ):
            frame = self.abs_frame1(widget.width,widget.height,widget.positions_X[0],widget.positions_Y[0])
            widget.controller = []
            radio_var = widget.value
            widget.value = root.IntVar()
            widget.value.set(radio_var)
            radio_controller = root.Radiobutton(frame, text=widget.labels[0], variable=widget.value, value=0)
            radio_controller.pack(fill=root.BOTH, expand=1)
            widget.controller.append(radio_controller)
            for i in range(1,len(widget.labels)):
                frame = self.abs_frame1(widget.width,widget.height,widget.positions_X[i],widget.positions_Y[i])
                radio_controller = root.Radiobutton(frame, text=widget.labels[i], variable=widget.value,value=i)
                radio_controller.pack(fill=root.BOTH, expand=1)
                widget.controller.append(radio_controller)

        # elif(widget_type=="ValueList" or isinstance(widget,ValueList) ):
        #     array = ['']
        #     array[0] = widget.value
        #     array = array + widget.choices
        #     widget.list_var = root.StringVar()
        #     widget.list_var.set(array[0])
        #     frame = self.abs_frame(widget)
        #     widget.controller = apply(root.OptionMenu, (frame, widget.list_var) + tuple(array))
        #     widget.controller.pack(fill=root.BOTH, expand=1)

        # elif(widget_type == "SpinBox" or isinstance(widget,SpinBox) ):
        #     frame = self.abs_frame(widget)
        #     widget.controller = root.Spinbox(frame, from_=widget.start, to=widget.end )
        #     widget.controller.pack(fill=root.BOTH, expand=1)

        elif(widget_type == "Slider" or isinstance(widget,Slider) ):
            frame = self.abs_frame(widget)
            widget.controller = root.Scale(frame, from_=widget.start, to=widget.end , orient=root.HORIZONTAL)
            widget.controller.pack(fill=root.BOTH, expand=1)

        # elif(widget_type == "Password" or isinstance(widget,Slider) ):
        #     frame = self.abs_frame(widget)
        #     widget.controller = root.Entry(frame, show="*")
        #     widget.controller.pack(fill=root.BOTH, expand=1)

        elif(widget_type == "TextLine" or isinstance(widget,Slider) ):
            frame = self.abs_frame(widget)
            widget.controller = root.Entry(frame)
            widget.controller.pack(fill=root.BOTH, expand=1)

    def abs_frame(self,widget):
        frame = root.Frame(self.window, width=widget.width,height=widget.height)
        frame.pack_propagate(0) # don't shrink
        frame.pack()
        frame.place(x=widget.position_X,y=widget.position_Y)
        return frame

    def abs_frame1(self,W,H,X,Y):
        frame = root.Frame(self.window, width=W,height=H)
        frame.pack_propagate(0) # don't shrink
        frame.pack()
        frame.place(x=X,y=Y)
        return frame

        
''' WIDGETS: Button '''
class Button(object):
    controller = None
    callbackMethod = None
    Type = None
    def __init__(self,title,X,Y,width,height):
        self.Type = "Button"
        self.title = title
        self.position_X = X
        self.position_Y = Y
        self.width = width
        self.height = height


    def clickListener(self,method):
        if(self.controller == None):
            self.callbackMethod = method
        else:
            self.controller.config(command=method)
        return True
        
class Slider(object):
    controller = None
    callback = None
    Type = "Slider"
    def __init__(self,start,end,X,Y,width,height):
        self.start=start
        self.end=end
        self.position_X = X
        self.position_Y = Y
        self.width = width
        self.height = height
    def getValue(self):
        if(self.controller == None):
            return ''
        else:   
            return self.controller.get()

# class Password(object):
#     controller = None
#     callback = None
#     Type= "Password"
#     def __init__(self,X,Y,width,height):
#         self.position_X = X
#         self.position_Y = Y
#         self.width = width
#         self.height = height
#     def getText(self):
#         if(self.controller == None):
#             return ''
#         else:   
#             return self.controller.get()

''' WIDGETS: TextArea '''
class TextArea(object):
    #controller = None
    callback = None
    Type = None
    def __init__(self,title,X,Y,width,height):
        self.Type = "TextArea"
        self.text = title
        self.position_X = X
        self.position_Y = Y
        self.width = width
        self.height = height

    def setText(self,text):
        if(self.controller == None):
            self.text = text
            self.controller.configure(state='disabled')
        else:
            self.controller.delete(1.0, root.END)
            self.controller.insert(root.INSERT,text)
            self.controller.configure(state='disabled')
        return True

    def getText(self):
        if(self.controller == None):
            print len(self.text)
            return self.text
            self.controller.configure(state='disabled')
        else:
            print len(self.text)
            return self.controller.get(1.0, root.END)

    def appendText(self,text):
        if(self.controller == None):
            self.text = self.text + text
            print self.text
            self.controller.configure(state='disabled')
        else:
            self.controller.insert(root.INSERT, text)
            self.controller.configure(state='disabled')
        return True              

    def clear(self):
        self.controller.delete(1.0, root.END)
        return True


''' WIDGETS: Label '''
class Label(object):
    controller = None
    Type = None
    label_var = 0
    def __init__(self,text,X,Y,width,height):
        self.Type = "Label"
        self.label_var = text
        self.position_X = X
        self.position_Y = Y
        self.width = width
        self.height = height

    def setText(self,text):
        if(self.controller == None):
            self.text = text
        else:
            self.label_var.set(text)
        return True

    def clear(self):
        self.controller.Clear()
        return True


''' WIDGETS: CheckBox '''
# class CheckBox(object):
#     controller = None
#     value = False
#     Type = None
#     def __init__(self,title,X,Y,width,height):
#         self.Type = "CheckBox"
#         self.title = title
#         self.position_X = X
#         self.position_Y = Y
#         self.width = width
#         self.height = height

#     def setValue(self,value):
#         if(self.controller == None):
#             self.value = value
#         else:
#             if(value):
#                 self.controller.select()
#             else:
#                 self.controller.deselect()

#     def getValue(self):
#         if(self.controller == None):
#             return self.value
#         else:
#             if(self.value.get() == 1):
#                 return True
#             else:
#                 return False

# class SpinBox(object):
#     controller = None
#     callback = None
#     Type = None
#     def __init__(self,start,end,X,Y,width,height):
#         self.type = "SpinBox"
#         self.start=start
#         self.end=end
#         self.position_X = X
#         self.position_Y = Y
#         self.width = width
#         self.height = height

#     def getValue(self):
#         if(self.controller == None):
#             return ''
#         else:   
#             return self.controller.get()

''' WIDGETS: RadioGroup '''
class RadioGroup(object):
    controller = None
    selected_index = None
    Type = None
    value = 0
    def __init__(self,width,height):
        self.Type = "RadioGroup"
        self.labels = []
        self.positions_X = []
        self.positions_Y = []
        self.width = width
        self.height = height

    def addRadioButton(self,label,X,Y):
        self.labels.append(label)
        self.positions_X.append(X)
        self.positions_Y.append(Y)
        return True

    def getValue(self):
        for i in range(len(self.controller)):
            if(self.value.get()==i):
                return self.labels[i]
        return None

    def setButtonTrue(self,index):
        if(self.controller == None):
            self.value=index
        else:
            button_controller = self.controller[index]
            button_controller.select()

class TextLine(object):
    controller = None
    callback = None
    Type= "TextLine"    
    def __init__(self,X,Y,width,height):
        self.position_X = X
        self.position_Y = Y
        self.width = width
        self.height = height
    def getText(self):
        if(self.controller == None):
            return ''
        else:
            return self.controller.get()

    def setText(self,text):
        if(self.controller == None):
            self.text = text
        else:
            self.controller.delete(0, root.END)
            self.controller.insert(0, text)
            return True

''' WIDGETS: ValueList '''
# class ValueList(object):
#     controller = None
#     Type = None
#     list_var = 0
#     def __init__(self,choices,X,Y,width,height,value=""):
#         self.Type = "ValueList"
#         self.choices = choices
#         self.position_X = X
#         self.position_Y = Y
#         self.width = width
#         self.height = height
#         self.value = value

#     def getValue(self):
#             if(self.controller == None):
#                 return self.title
#             else:
#                 return self.list_var.get()

''' ----------------------------------------------------------------
        This is just demo! 
        IT IS NOT THE PART OF LIB '''

if __name__ == '__main__':
    #Functions bind to button events
    def SubmitButtonClick(event=None):
        if (groupB.getValue()=='G3') or (len(uidT.getText())==0):
            print 'Please select treatment group and enter user ID'
            return
        path = '/Users/mb/Desktop/Janis.So/06_qmul/BB/05_data/'+str(groupB.getValue())+'/'+uidT.getText()+'/'
        if not os.path.exists(path):
            #os.makedirs(savePath)
            print 'No such user'
            return
        f = open(path+uidT.getText()+'_psq.csv','w+')
        f.write(str(q1S.getValue())+'\n')
        f.write(str(q2S.getValue())+'\n')
        f.write(str(q3S.getValue())+'\n')
        f.write(str(q4S.getValue())+'\n')
        f.write(str(q5S.getValue())+'\n')
        f.write(str(q6S.getValue())+'\n')
        f.write(str(q7S.getValue())+'\n')
        f.write(str(q8S.getValue())+'\n')
        f.write(str(q9S.getValue())+'\n')
        f.write(str(q10S.getValue())+'\n')
        f.close()
        print 'CSV file saved\n'
        print 'Group: '+ str(groupB.getValue())
        print 'User ID: '+ uidT.getText()
        print str(q1S.getValue())+'\n'+str(q2S.getValue())+'\n'+str(q3S.getValue())+'\n'+str(q4S.getValue())+'\n'+str(q5S.getValue())+'\n'+str(q6S.getValue())+'\n'+str(q7S.getValue())+'\n'+str(q8S.getValue())+'\n'+str(q9S.getValue())+'\n'+str(q10S.getValue())+'\n'
        #f.write('Time,Value\n')
        #print path
        #report = "\n"
        # if(checkbox1.getValue()):
        #     report = report + " you have read the code\n"
        # else:
        #     report = report + " you have not read the code\n"
    
        # if(checkbox2.getValue()):
        #     report = report + " you have read the documentation\n"
        # else:
        #     report = report + " you have not read the documentation\n"
        #report = report + " you are "+groupB.getValue()+"\n"
        #report = report + " you need "+rb2.getValue()+"\n"
        #textarea.appendText(" password :  \n"+ pas.getText()+"\n"+report+"\n" + " Slider value " + str(sli.getValue())+" SpinBox value  " + str(spin.getValue())+" \n")
        #textarea.appendText(" text submitted :  \n"+ str(len(uidT.getText()))+"\n"+report+"\n" + " Slider value " + str(sli.getValue())+"\n")
    #textarea.appendText(sli.getValue())
        return True
    
    # def AboutButtonClick(event=None):
    #     textarea.setText("Created by qtGUI Author : Prateek Mukati\n")
    #     return True
    
    #Constructor Frame
    Frame = Canvas(1, 'Survey ' ,600,1000)

    uidL=Label('User ID',50,0,100,30)
    Frame.add(uidL)   
    uidT=TextLine(150,0,50,30)
    Frame.add(uidT)


    #ANSWERS
    q1L0=TextArea('Strongly \nDisagree',25,50,150,50)
    Frame.add(q1L0)
    q1L1=TextArea('\nDisagree',155,50,150,50)
    Frame.add(q1L1)
    q1L2=TextArea('\nUndecided',265,50,150,50)
    Frame.add(q1L2)
    q1L3=TextArea('\nAgree',390,50,150,50)
    Frame.add(q1L3)
    q1L4=TextArea('Strongly \nAgree',500,50,150,50)
    Frame.add(q1L4)

    #Q1
    q1T = TextArea("1. I would recommend this instrument to a friend",25,100,400,40)
    Frame.add(q1T)
    q1S=Slider(1,5,50,125,500,40)
    Frame.add(q1S)

    #Q2
    q2T = TextArea("2. I like the instrument/experience",25,175,400,40)
    Frame.add(q2T)
    q2S=Slider(1,5,50,200,500,40)
    Frame.add(q2S)

    #Q3
    q3T = TextArea("3. Were absorbed in the activity (flow)",25,250,400,40)
    Frame.add(q3T)
    q3S=Slider(1,5,50,275,500,40)
    Frame.add(q3S)
    
    #Q4
    q4T = TextArea("4. Did you have some issues operating the device",25,325,400,40)
    Frame.add(q4T)
    q4S=Slider(1,5,50,350,500,40)
    Frame.add(q4S)

    #Q5
    q5T = TextArea("5. It increase my understanding of expressivity",25,400,400,40)
    Frame.add(q5T)
    q5S=Slider(1,5,50,425,500,40)
    Frame.add(q5S)

    #Q6
    q6T = TextArea("6. It is clear to me how to use the instrument",25,475,400,40)
    Frame.add(q6T)
    q6S=Slider(1,5,50,500,500,40)
    Frame.add(q6S)

    #Q7
    q7T = TextArea("7. I felt in control of the music",25,550,400,40)
    Frame.add(q7T)
    q7S=Slider(1,5,50,575,500,40)
    Frame.add(q7S)

    #Q8
    q8T = TextArea("8. Interesting teaching device",25,625,400,40)
    Frame.add(q8T)
    q8S=Slider(1,5,50,650,500,40)
    Frame.add(q8S)

    #Q9
    q9T = TextArea("9. Interesting teaching device",25,700,400,40)
    Frame.add(q9T)
    q9S=Slider(1,5,50,725,500,40)
    Frame.add(q9S)

    #Q10
    q10T = TextArea("10. I was able to express my desire using BB",25,775,400,40)
    Frame.add(q10T)
    q10S=Slider(1,5,50,800,500,40)
    Frame.add(q10S)


    
    #Dropdown valuelist
    # cities = ['New Delhi', 'Mumbai', 'Ropar', 'Lucknow', 'Chandigrah', 'Wasseypur', 'Jaipur' ]
    # valuelist = ValueList(cities,10,10,200,20,"<Select your city>")
    # Frame.add(valuelist)
    
    # #checkboxs
    # checkbox1 = CheckBox("I have read the code.",10,45,215,15)
    # checkbox2 = CheckBox("I have read the documentation.",10,70,215,15)
    # checkbox1.setValue(True)
    # Frame.add(checkbox1)
    # Frame.add(checkbox2)

    groupL=Label('Group',250,0,100,30)
    Frame.add(groupL)  
    
    #radioGroup1
    groupB = RadioGroup(100,20)
    groupB.addRadioButton("G1",350,10)
    groupB.addRadioButton("G2",450,10)
    groupB.addRadioButton("G3",650,10)
    groupB.setButtonTrue(2)
    Frame.add(groupB)
    
    #radioGroup2
    # rb2 = RadioGroup(100,50)
    # rb2.addRadioButton("Option #1",10,160)
    # rb2.addRadioButton("Option #2",110,160)
    # rb2.setButtonTrue(0)
    # Frame.add(rb2)
    #TextArea
    #textarea = TextArea("\n Click submit button to see output here!!",250,100,250,200)
    #Frame.add(textarea)
    #Creating Buttons
    submitBtn = Button("Submit",240,875,120,30)
    #aboutBtn = Button("About",260,230,120,30)
    #Callback methods on buttons click
    submitBtn.clickListener(SubmitButtonClick)
    # aboutBtn.clickListener(AboutButtonClick)
    ## password
    # pas=Password(130,280,150,30)
    # Frame.add(pas)
    #sli=Slider(1,5,130,320,150,30) 
    #Frame.add(sli)
    # spin=SpinBox(0,10,130,360,150,30) 
    # Frame.add(spin)   
    #Adding buttons to Frame
    # Frame.add(aboutBtn)
    Frame.add(submitBtn)
    Frame.show()