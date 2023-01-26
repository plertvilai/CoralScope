#!/usr/bin/python

# Library for CoralScope Hat
# P. Lertvilai
# Nov, 2022

import io
import os
import time
import numpy as np
import datetime as dt
import subprocess
import signal

# GPIO assigments
fan_pin = 27
led_en_pin = 10
push_pin_1 = 5
push_pin_2 = 6
trigger_pin = 13
strobe_en_pin = 26
dim_pin = 18
signal_led_pin = 21


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


class dIPAX():

	def __init__(self,outputDir,shutter=500,iso=100,awb=(1.0,2.4),fps=30,imDim=(4056,3040),vidDim=(1920,1080)):
		'''Initialize dIPAX object with camera parameters.
		INPUT:
			outputDir = (string) directory of output images and videos.
			shutter = (int) camera shutter speed in microseconds
			iso = (int) camera ISO value
			awb = (float,float) camera white balance tuple (red/green,blue/green)
			fps = (int) camera frame rate 
			imDim = (int,int) image dimension for still images in pixels
			vidDim = (int,int) image dimension for videos in pixels. Note that RPi uses H264 video
					encodind, so the dimension is constrained by the encoder.
		'''
		# camera parameters
		self.ss = shutter
		self.iso = iso
		self.awb = awb
		self.fps = fps
		self.imDim = imDim
		self.vidDim = vidDim

		# output file
		self.dir = outputDir

		#time keeping
		self.time = time.time()

		# error keeping
		self.error = 0

		#mode 0 = still image, 1 = video
		self.mode = 0

	def initialize(self):
		'''Initialize output folders.'''
		# check for images directory
		if os.path.isdir("%simages/"%self.dir):
			print("Found images folder")
		else:
			print("Images folder not found. Creating the folder")
			os.system("mkdir images")

		# check for videos directory
		if os.path.isdir("%svideos/"%self.dir):
			print("Found videos folder")
		else:
			print("Videos folder not found. Creating the folder")
			os.system("mkdir videos")
		print("Finished initialization.")

		# initialize GPIO
		GPIO.setmode(GPIO.BCM)
		# Input pins
		GPIO.setup(trigger_pin, GPIO.IN)
		GPIO.setup(dim_pin, GPIO.IN)
		GPIO.setup(push_pin_1, GPIO.IN)
		GPIO.setup(push_pin_2, GPIO.IN)
		# Output pins
		GPIO.setup(fan_pin, GPIO.OUT)
		GPIO.output(fan_pin,GPIO.LOW)
		GPIO.setup(led_en_pin, GPIO.OUT)
		GPIO.output(led_en_pin,GPIO.LOW)
		GPIO.setup(strobe_en_pin, GPIO.OUT)
		GPIO.output(strobe_en_pin,GPIO.HIGH) # strobe_en is default to high
		GPIO.setup(signal_led_pin, GPIO.OUT)
		GPIO.output(signal_led_pin,GPIO.LOW)

	def updateTime(self):
		'''Update timestamp of dIPAX.
		Return current unix timestamp in seconds'''
		self.time = time.time()
		return self.time

	def timePass(self):
		'''Return the elapsed time since previous timestamp.'''
		return time.time()-self.time

	def setMode(self,mode):
		'''Set image acquisition mode.
		INPUT: mode=0 -> still image
				mode=1 -> video.'''
		self.mode = mode
		return self.mode

	def addError(self,cond):
		'''Increment error count by 1 if the cond is met.
		Return new error count value.'''
		if cond:
			self.error = self.error+1
		return self.error

	def raspicamPipeline(self,tt=1000):
		'''Return bash script for executing raspistill or raspivid
		INPUT: 
				tt = duration of raspistill/raspivid execution in milliseconds
				mode=0 -> raspistill
			  	mode=1 -> raspivid
	  	OUTPUT:
	  		string of bash script for executing raspistill/raspivid command.'''
		if self.mode==0: # for raspistill
  			return ('raspistill -n -q 100 -w %d -h %d -awb off -awbg %.1f,%.1f -ISO %d -ss %d -t %d -o %simages/%d.jpg' %(self.imDim[0],self.imDim[1],self.awb[0],self.awb[1],self.iso, self.ss, tt, self.dir, self.time))
		else: # for raspivid
			return ('raspivid -n -w %d -h %d '
  				'-awb off -awbg %.1f,%.1f -ISO %d -fps %d '
  				'-ss %d -t %d -o %svideos/%d.h264 -pts %sframes/%d.pts' %(self.vidDim[0],self.vidDim[1],
  					self.awb[0],self.awb[1],self.iso, self.fps,self.ss, tt, self.dir, self.time, self.dir, self.time))

	
	def takePicture(self):
		'''Take one still image.
		OUTPUT:
			ret = (boolean) True if command is successfully executed. False if there is an error.
			'''
		self.setMode(0) # set to image mode
		command = self.raspicamPipeline(tt=500)
		print(command)
		ret = runCmdTimeout(command,timeout=15)
		return ret

	def takeVideo(self,t=60000):
		'''Take video of duration tt.
		INPUT: 
			tt = duration of raspistill/raspivid execution in milliseconds
		OUTPUT:
			ret = (boolean) True if command is successfully executed. False if there is an error
			'''
		self.setMode(1) # set to image mode
		command = self.raspicamPipeline(tt=t)
		print(command)
		ret = runCmdTimeout(command,timeout=t/1000+10) # timeout is set to video duration +10s
		return ret

	def checkOutput(self,expectedSize=10000):
		'''Check output file whether it is valid.
		INPUT: expectedSize = expected file size in Bytes
		OUTPUT: cond1 = (bool) file exist?
				cond2 = (bool) file size valid?'''

		# get current filename 
		if self.mode == 0:
			filename = "%simages/%d.jpg"%(self.dir,self.time)
		else:
			filename = "%svideos/%d.h264"%(self.dir,self.time)
		
		# check whether file exists first
		cond1 = os.path.isfile(filename)
		if not cond1:
			print("File not exist")
			cond2 = False
			return cond1, cond2

		# check whether file is larger than expected size
		fsize = os.path.getsize(filename)
		cond2 = fsize > expectedSize
		if not cond2:
			print("File size too small")

		return cond1, cond2

	def recordStat(self,dataStr,fname):
		''' Record dataStr to file fname.
		INPUT:
			dataStr = (string) data to be recorded
			fname = (string) name of the file
		'''
		filename = "%s%s"%(self.dir,fname)
		file = open(filename, 'a')
		file.write(dataStr)
		file.close()