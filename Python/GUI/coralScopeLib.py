import tkinter as tk
import os
import time
from PIL import Image, ImageTk
from datetime import datetime
import RPi.GPIO as GPIO
import subprocess
# for sensors
import bme280
import ms5837
import Adafruit_ADS1x15

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

class coralScopeApp():

    def __init__(self,outputDir):

        self.dir = outputDir
        self.time = time.time()

        self.ms5837sensor = ms5837.MS5837_30BA()
        self.adc = Adafruit_ADS1x15.ADS1115()
        

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
                self.ms5837sensor.init()
                print("Successfully initialize MS5837")
                self.ms5837_stat = True
                self.ms5837data = [0,0]
                break
            except Exception:
                print("Fail to initialize MS5837: %d"%cnt)
                self.ms5837_stat = False
                self.ms5837data = [-1,-1]
                cnt = cnt+1

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

        cnt = 0
        while(cnt<n_try):
            try:
                self.adc.read_adc(0, gain=1)
                print("Successfully initialize ADC")
                self.adc_stat = True
                self.vbatt = 0
                break
            except Exception:
                print("Fail to initialize ADC: %d"%cnt)
                self.adc_stat = False
                self.vbatt = -1
                cnt = cnt+1


    def readBattery(self,read_adc=False):
        if read_adc:
            adc_val = self.adc.read_adc(0, gain=1)
            self.vbatt = 3.7*adc_val/32767*4.096
        else:
            self.vbatt = 0
        return self.vbatt

    def readSensors(self,read_ms5837=False,read_bme280=False):
        if read_ms5837:
            self.ms5837sensor.read()
            self.ms5837data = [self.ms5837sensor.depth(),self.ms5837sensor.temperature()]

        if read_bme280:
            self.bme280data = bme280.readBME280All()

    def logData(self):
        data_str = '%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n'%(time.time(),self.vbatt,self.ms5837data[0],self.ms5837data[1],
            self.bme280data[0],self.bme280data[1],self.bme280data[2],self.bme280data[3])
        f = open(self.data_log_file, "a")
        f.write(data_str)
        f.close()


    def runGUI(self,w=800,h=480,logo_dir=''):
        self.w = w # window width
        self.h = h # window height
        
        self.root = tk.Tk() # main GUI object
        
        # -- Microscope Parameters --
        self.setMode('highres')

        #---------- App Components ---------#
        self.root.title("coralScope")
        # create a full screen window
        self.root.geometry('%dx%d+%d+%d' % (self.w, self.h, 0, 0))
        # root.configure(bg='white')

        # display logo
        if not logo_dir == '':
            load = Image.open(self.dir+logo_dir)
            resize_image  = load.resize((100,100))
            render = ImageTk.PhotoImage(resize_image)
            img = tk.Label(image=render)
            img.image = render
            img.place(x=25, y=25)

        # Logo Text Label
        self.logo_label = tk.Label(text="CoralScope",font=("Arial", 35))
        self.logo_label.place(x=150, y=25)
        
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
        # water depth
        self.wdepth_label = tk.Label(text="Depth:",font=("Arial", parameter_font_size))
        self.wdepth_label.place(x=50, y=200)
        self.wdepth_value = tk.Label(text="50.00 m",font=("Arial", parameter_font_size))
        self.wdepth_value.place(x=200, y=200)
        
        # water temp
        self.wtemp_label = tk.Label(text="Temp:",font=("Arial", parameter_font_size))
        self.wtemp_label.place(x=50, y=300)
        self.wtemp_value = tk.Label(text="25.2 C",font=("Arial", parameter_font_size))
        self.wtemp_value.place(x=200, y=300)
        
        # Internal temp
        self.itemp_label = tk.Label(text="iTemp:",font=("Arial", parameter_font_size))
        self.itemp_label.place(x=400, y=200)
        self.itemp_value = tk.Label(text="25.2 C",font=("Arial", parameter_font_size))
        self.itemp_value.place(x=550, y=200)
        
        # Internal pressure
        self.ipress_label = tk.Label(text="iPress:",font=("Arial", parameter_font_size))
        self.ipress_label.place(x=400, y=300)
        self.ipress_value = tk.Label(text="25.2 kPa",font=("Arial", parameter_font_size))
        self.ipress_value.place(x=550, y=300)

        # Battery label
        self.vbatt_label = tk.Label(text="Vbatt",font=("Arial", parameter_font_size))
        self.vbatt_label.place(x=500, y=100)
        self.vbatt_value = tk.Label(text="0.00V",font=("Arial", parameter_font_size))
        self.vbatt_value.place(x=630, y=100)
        
        
        
        self.updateApp()
        self.root.mainloop()
    
    def updateApp(self):
        now_string = time.strftime("%H:%M:%S")
        self.time_label.configure(text=now_string)

        # read sensor data
        try:
            self.readSensors(read_ms5837 = self.ms5837_stat,read_bme280 = self.bme280_stat)
            self.readBattery(read_adc=self.adc_stat)
            self.wdepth_value.configure(text="%.2f m"%self.ms5837data[0])
            self.wtemp_value.configure(text="%.2f C"%self.ms5837data[1])
            self.ipress_value.configure(text="%.2f bar"%self.bme280data[2])
            self.itemp_value.configure(text="%.2f C"%self.bme280data[0])
            self.vbatt_value.configure(text="%.2f V"%self.vbatt)
        except Exception:
            self.status_label.configure(text="STATUS: I2C Error",font=("Arial", 25),bg='red', fg='white')

        # read GPIO pin
        # self.updateMode()
        # Take video if the button is pushed
        try:
            if self.checkPush(0):
                self.updateTime()
                self.takeVideo(t = 60000)
                time.sleep(10)
        except Exception:
            self.status_label.configure(text="STATUS: CAM Error",font=("Arial", 25),bg='red', fg='white')


        # log data
        self.logData()

        self.root.after(1000,self.updateApp)

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

    def takeVideo(self,t=60000):
        '''Take video of duration tt.
        INPUT: 
            tt = duration of raspistill/raspivid execution in milliseconds
        OUTPUT:
            ret = (boolean) True if command is successfully executed. False if there is an error
            '''
        command = self.raspicamPipeline(tt=t)
        print(command)
        ret = runCmdTimeout(command,timeout=t/1000+10) # timeout is set to video duration +10s
        return ret

    def raspicamPipeline(self,tt=1000):
        '''Return bash script for executing raspistill or raspivid
        INPUT: 
                tt = duration of raspistill/raspivid execution in milliseconds
                mode=0 -> raspistill
                mode=1 -> raspivid
        OUTPUT:
            string of bash script for executing raspistill/raspivid command.'''
        if self.mode==0: # for raspistill
            return ('raspivid -w 1280 -h 720 '
                '-awb off -awbg 0.6,1.5 -ISO 100 -fps 65 '
                '-ss 16500 -t %d -o %svideos/%d.h264 -pts %sframes/%d.pts' %(tt,self.dir,self.time,self.dir,self.time))
        else: # for raspivid
            return ('raspivid -w 1920 -h 1080 '
                '-awb off -awbg 0.6,1.5 -ISO 100 -fps 30 '
                '-ss 16500 -t %d -o %svideos/%d.h264 -pts %sframes/%d.pts' %(tt,self.dir,self.time,self.dir,self.time))

        
        