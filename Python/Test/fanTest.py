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
fan_pin = 27 

GPIO.setmode(GPIO.BCM)
GPIO.setup(fan_pin, GPIO.OUT)

GPIO.output(fan_pin,GPIO.LOW) # active low
print("Turning fan ON.")
time.sleep(10)
print("Turning fan OFF.")
GPIO.cleanup()