import os
import time
import RPi.GPIO as GPIO
import subprocess

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

def raspicamPipeline(tt=1000):
	return ('raspivid -w 1920 -h 1080 '
		'-awb off -awbg 0.6,1.5 -ISO 100 -fps 30 '
		'-ss 16500 -t %d -o test.h264' %(tt))
	    

# GPIO Setup
strobe_en_pin = 26 
trigger_pin = 13
led_en_pin = 10
dim_pin = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(strobe_en_pin, GPIO.OUT)
GPIO.setup(trigger_pin, GPIO.IN)
GPIO.setup(led_en_pin, GPIO.OUT)
# GPIO.setup(dim_pin, GPIO.IN)

GPIO.output(strobe_en_pin,GPIO.LOW) # active low
# GPIO.output(trigger_pin,GPIO.LOW) # active high
GPIO.output(led_en_pin,GPIO.HIGH) # active high
vid_time = 20000

command = raspicamPipeline(tt=vid_time)
print(command)
ret = runCmdTimeout(command,timeout=vid_time/1000+10) # timeout is set to video duration +10s