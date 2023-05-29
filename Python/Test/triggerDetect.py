#!/usr/bin/python

# CoralScope test script
# Test camera strobing
# P. Lertvilai
# Feb, 2021

import os
import time
import RPi.GPIO as GPIO
import datetime

# GPIO Setup
strobe_en_pin = 26 # input pin from switch; only take images if this pin is HIGH
trigger_pin = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(strobe_en_pin, GPIO.OUT)
GPIO.setup(trigger_pin, GPIO.IN)
GPIO.output(strobe_en_pin,GPIO.LOW)

while True:
        GPIO.wait_for_edge(trigger_pin, GPIO.RISING)
        #t0 = time.time()
        #GPIO.wait_for_edge(trigger_pin, GPIO.FALLING)
        #t1 = time.time()
        print("Trigger Received!")
        #print("Pulse width = %.2f ms"%(t1-t0)*1000)
