#!/usr/bin/python

# CoralScope test script
# Test camera strobing
# P. Lertvilai
# Nov, 2022

import os
import time
import RPi.GPIO as GPIO
import datetime

# GPIO Setup
strobe_en_pin = 26 
trigger_pin = 13
led_en_pin = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(strobe_en_pin, GPIO.OUT)
GPIO.setup(trigger_pin, GPIO.OUT)
GPIO.setup(led_en_pin, GPIO.OUT)

GPIO.output(strobe_en_pin,GPIO.LOW) # active low
GPIO.output(trigger_pin,GPIO.LOW) # active high
GPIO.output(led_en_pin,GPIO.HIGH) # active high

for n in range(5):
	print(n)
	GPIO.output(trigger_pin,GPIO.HIGH)
	time.sleep(0.01)
	GPIO.output(trigger_pin,GPIO.LOW)
	time.sleep(1)

GPIO.output(trigger_pin,GPIO.LOW)
GPIO.cleanup()