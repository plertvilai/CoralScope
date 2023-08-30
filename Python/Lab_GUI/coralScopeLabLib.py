import tkinter as tk
import os
import time
from PIL import Image, ImageTk
from datetime import datetime
import RPi.GPIO as GPIO
import subprocess
# for sensors
import bme280

# general function for interacting with bash script
def runCmdTimeout(cmd, timeout=15):
    """run a command in terminal with timeout. Shell = False
    return True is command successfully runs before timeout
    """
    success = True
    try:
        subprocess.check_output(cmd.split(" "), timeout=timeout)
    except:
        print("Process Timeout")
        success = False

    return success

def runShellTimeout(cmd, timeout=15):
    """run a command in terminal with timeout. Shell = True
    return True is command successfully runs before timeout
    Source: https://stackoverflow.com/questions/36952245/subprocess-timeout-failure
    """
    success = True
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid) as process:
        try:
            output = process.communicate(timeout=timeout)[0]
        except:
            print("Process Timeout")
            os.killpg(process.pid, signal.SIGINT) # send signal to the process group
            output = process.communicate()[0]
            success = False
    return success

class coralScopeLabApp():

    def __init__(self,outputDir):

        self.dir = outputDir
        self.time = time.time()

        

        # Initialize output directory
        if not os.path.exists(self.dir+'videos/'):
            print("Videos folder not found. Making the folder ...")
            os.mkdir(self.dir+'videos/')
        if not os.path.exists(self.dir+'frames/'):
            print("Frames folder not found. Making the folder ...")
            os.mkdir(self.dir+'frames/')
        if not os.path.exists(self.dir+'sensors/'):
            print("Sensors folder not found. Making the folder ...")
            os.mkdir(self.dir+'sensors/')

        # file for data logging
        self.data_log_file = self.dir + 'sensors/%d.csv'%time.time()

        # GPIO assignment
        self.push_pin = [5,6]
        self.strobe_en_pin = 26 
        self.trigger_pin = 13
        self.led_en_pin = 10
        self.dim_pin = 18
        self.fan_pin = 27

        # Time keeping
        self.shdn_cnt_sec = 10 # time to shutdown in seconds
        self.shdn_start_t = time.time()
        self.shdn_flag = False

        # for limits
        self.max_duration = 120 # max video duration in seconds

    def GPIOinit(self):

        GPIO.setmode(GPIO.BCM)
        # GPIO.cleanup()
        time.sleep(10)
        GPIO.setup(self.strobe_en_pin, GPIO.OUT)
        GPIO.setup(self.trigger_pin, GPIO.IN)
        GPIO.setup(self.led_en_pin, GPIO.OUT)

        for push_pin_num in self.push_pin:
            GPIO.setup(push_pin_num, GPIO.IN)

        # strobe is enabled by default
        GPIO.output(self.strobe_en_pin,GPIO.LOW) # active low
        GPIO.output(self.led_en_pin,GPIO.HIGH) # active high

        # fan pin
        GPIO.setup(self.fan_pin, GPIO.OUT)
        GPIO.output(self.fan_pin,GPIO.HIGH)

    def sensorsInit(self,n_try=10):

        cnt = 0
        while(cnt<n_try):
            try:
                self.bme280data = bme280.readBME280All()
                print("Successfully initialize bme280")
                self.bme280_stat = True
                break
            except Exception:
                print("Fail to initialize BME280: %d"%cnt)
                self.bme280_stat = False
                self.bme280data = [-1,-1,-1,-1]
                cnt = cnt+1

    def readSensors(self,read_bme280=False):

        if read_bme280:
            self.bme280data = bme280.readBME280All()

    def logData(self):
        data_str = '%.2f,%.2f,%.2f,%.2f,%.2f\n'%(time.time(),
            self.bme280data[0],self.bme280data[1],self.bme280data[2],self.bme280data[3])
        f = open(self.data_log_file, "a")
        f.write(data_str)
        f.close()


    def runGUI(self,w=800,h=480,logo_dir=''):
        self.w = w # window width
        self.h = h # window height
        
        self.root = tk.Tk() # main GUI object
        
        self.strobe_stat = tk.IntVar(None, 1)
        
        #---------- App Components ---------#
        self.root.title("coralScope")
        # create a full screen window
        self.root.geometry('%dx%d+%d+%d' % (self.w, self.h, 0, 0))
        # root.configure(bg='white')

        # display logo
        load = Image.open(logo_dir)
        resize_image  = load.resize((100,100))
        render = ImageTk.PhotoImage(resize_image)
        img = tk.Label(image=render)
        img.image = render
        img.place(x=25, y=25)

        # Logo Text Label
        self.logo_label = tk.Label(text="CoralScope Lab",font=("Arial", 35))
        self.logo_label.place(x=150, y=25)

        # Message Test Box
        self.message_box_label = tk.Label(text="Message",font=("Arial", 15))
        self.message_box_label.place(x=550, y=75)
        self.message_box = tk.Text(height = 7, width = 30,font=("Arial", 10))
        self.message_box.place(x=550, y=100)
        self.message_box.config(state='disabled')
        
        # version label
        self.version_label = tk.Label(text="v1.0",font=("Arial", 15))
        self.version_label.place(x=750, y=450)
        
        # Time label
        self.time_label = tk.Label(text="00:00:00",font=("Arial", 25))
        self.time_label.place(x=625, y=25)
        
        # status label
        self.status_label = tk.Label(text="STATUS: OK",font=("Arial", 25),bg='green', fg='white')
        self.status_label.place(x=150, y=100)
        
        # -------- Parameter Labels ------#
        parameter_font_size = 35
        # -- Column 1 --
        # Preview button
        self.preview_button = tk.Button(self.root, text ="PREVIEW",font=("Arial", 25), command = self.previewCamera)
        self.preview_button.place(x=300, y=250)
        
        self.preview_button_s = tk.Label(self.root, text ="S",font=("Arial", 25))
        self.preview_button_s.place(x=200, y=260)
        
        self.preview_seconds = tk.Entry(self.root,width = 5,font=("Arial", 25))
        self.preview_seconds.insert(0,"30")
        self.preview_seconds.place(x=100, y=260)
        # Record button
        self.record_button = tk.Button(self.root, text ="RECORD",font=("Arial", 25), command = self.recordVideo)
        self.record_button.place(x=300, y=350)
        
        self.record_button_s = tk.Label(self.root, text ="S",font=("Arial", 25))
        self.record_button_s.place(x=200, y=360)
        
        self.record_seconds = tk.Entry(self.root,width = 5,font=("Arial", 25))
        self.record_seconds.insert(0,"30")
        self.record_seconds.place(x=100, y=360)
        
        # Strobe radio button
        strobe_options = {'Strobe OFF':'0', 'Strobe ON':'1'}
        
        self.strobe_button = tk.Radiobutton(self.root,text='Strobe ON',variable= self.strobe_stat,
                                           value=1,command = self.strobeON,font=("Arial", 25))
        self.strobe_button.place(x=550,y=250)
        self.strobe_button = tk.Radiobutton(self.root,text='Strobe OFF',variable= self.strobe_stat,
                                           value=0,command = self.strobeOFF,font=("Arial", 25))
        self.strobe_button.place(x=550,y=300)

        self.updateApp()
        self.root.mainloop()
    
    def updateApp(self):
        now_string = time.strftime("%H:%M:%S")
        self.time_label.configure(text=now_string)

        # log data
        # self.logData()

        self.root.after(1000,self.updateApp)

    def updateMessage(self,message='\n',clear=False):
        '''Update the message to the message box.'''
        # get timestamp
        now_string = time.strftime("[%H:%M:%S] ")
        self.message_box.configure(state='normal') # need to enable change first
        self.message_box.insert('end', now_string + message + '\n')
        self.message_box.configure(state='disabled') # disable change
        self.message_box.see('end') # scroll to the end of message box

    def updateTime(self):
        '''Update timestamp of dIPAX.
        Return current unix timestamp in seconds'''
        self.time = time.time()
        return self.time

    def updateMode(self):
        if GPIO.input(self.push_pin):
            self.mode = 1
        else:
            self.mode = 0

    def checkPush(self,sw_num):
        return GPIO.input(self.push_pin[sw_num])

    def setMode(self,mode_string):
        if mode_string.casefold() == 'highres'.casefold():
            self.mode = 1
        elif mode_string.casefold() == 'highfps'.casefold():
            self.mode = 0
        else:
            self.mode = 0

    def takeVideo(self,duration_s=60):
        '''Take video of duration tt.
        INPUT: 
            duration_s = duration of raspistill/raspivid execution in seconds
        OUTPUT:
            ret = (boolean) True if command is successfully executed. False if there is an error
            '''
        # First check whether duration exceeds the max value
        if duration_s > self.max_duration:
            self.updateMessage(message='Duration exceed max. Set to max.')
            duration_s = self.max_duration
        duration_ms = duration_s*1000 # convert from seconds to milliseconds
        command = (self.raspicamPipeline(duration_ms))
        print(command)
        ret = runCmdTimeout(command,timeout=duration_ms/1000+10) # timeout is set to video duration +10s
        return ret

    def raspicamPipeline(self,tt=1000):
        '''Return bash script for executing raspistill or raspivid
        INPUT: 
                tt = duration of raspistill/raspivid execution in milliseconds
                mode=0 -> raspistill
                mode=1 -> raspivid
        OUTPUT:
            string of bash script for executing raspistill/raspivid command.'''
        if self.mode==0: # for high frame rate
            return ('raspivid -w 1280 -h 720 '
                '-awb off -awbg 0.6,1.5 -ISO 100 -fps 65 '
                '-ss 16500 -t %d -o %svideos/%d.h264 -pts %sframes/%d.pts' %(tt,self.dir,self.time,self.dir,self.time))
        elif self.mode==1: # for high resolution
            return ('raspivid -w 1920 -h 1080 '
                '-awb off -awbg 0.6,1.5 -ISO 100 -fps 30 '
                '-ss 16500 -t %d -o %svideos/%d.h264 -pts %sframes/%d.pts' %(tt,self.dir,self.time,self.dir,self.time))
        else: # for preview only
            return ('raspivid -w 1920 -h 1080 '
                '-awb off -awbg 0.6,1.5 -ISO 100 -fps 30 '
                '-ss 16500 -t %d' %(tt))

    def strobeOFF(self):
        print("Strobe OFF")
        self.updateMessage(message='Strobe OFF.')
        GPIO.output(self.led_en_pin,GPIO.LOW)
        
    def strobeON(self):
        print("Strobe ON")
        self.updateMessage(message='Strobe ON.')
        GPIO.output(self.led_en_pin,GPIO.HIGH)
        
    def previewCamera(self):
        self.status_label.config(text="STATUS: Preview in Progress",font=("Arial", 25),bg='orange', fg='white')
        self.root.update_idletasks()
        self.mode = 99 # set mode to preview
        duration_str = self.preview_seconds.get()
        ret = self.takeVideo(int(duration_str))
        time.sleep(2) # wait for camera closing
        self.status_label.config(text="STATUS: OK",font=("Arial", 25),bg='green', fg='white')
        return ret
        
    def recordVideo(self):
        self.status_label.config(text="STATUS: Preview in Progress",font=("Arial", 25),bg='orange', fg='white')
        self.root.update_idletasks()
        self.mode = 1 # set mode to high res recording
        duration_str = self.record_seconds.get()
        ret = self.takeVideo(int(duration_str))
        time.sleep(2) # wait for camera closing
        self.status_label.config(text="STATUS: OK",font=("Arial", 25),bg='green', fg='white')
        return ret