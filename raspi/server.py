from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
import datetime
import spidev
from lib_nrf24 import NRF24
import requests
from threading import Thread
from adafruit_ht16k33 import segments
import board
import busio
import subprocess
import pygame as pg

# Pins
lbutton = 26
rbutton = 13
ubutton = 12
dbutton = 16
cbutton = 20

# Current state
state = 0       # Display mode: lamp/time, tilt, lift, hour, minute, delay
tiltStatus = 's'  # Current tilt motor action: s=Stop f=Forward r=Reverse
liftStatus = 's'  # Current lift motor action
tiltCurrent = 0 # Amount of tilt (time, x0.1s), 0 is fully closed
alarm_flag = False # is audible alarm playing?
wake = False    # Is any alarm active?
ip_mode = False # Whether IP address is displayed

# User set variables
t_begin = (7,0) # Time that gentle alarm triggers
t_end = (7,1)  # Time that hard alarm triggers
delay = 1      # Delay in minutes between hard and soft alarm
use_lamp = True    # Whether to use lamp instead of blinds
t_tilt = 35   # time to tilt up fully, tenths of a second
alarm_enable = True

# Initialize global objects
radio = NRF24(GPIO, spidev.SpiDev())
i2c = busio.I2C(board.SCL, board.SDA)
display = segments.Seg14x4(i2c)
app = Flask(__name__)

### Request-triggerable functions ###
@app.route("/tilt/up")
def tilt_up():
    global tiltStatus
    tiltStatus = 'f'
    
@app.route("/tilt/down")
def tilt_down():
    global tiltStatus
    tiltStatus = 'r'
    
@app.route("/tilt/stop")
def tilt_stop():
    global tiltStatus
    tiltStatus = 's'
    
@app.route("/tilt/auto")
def tilt_auto():
    tilt_close()
    
@app.route("/lift/up")
def lift_up():
    global liftStatus
    liftStatus = 'f'

@app.route("/lift/down")
def lift_down():
    global liftStatus
    liftStatus = 'r'

@app.route("/lift/stop")
def lift_stop():
    global liftStatus
    liftStatus = 's'

@app.route("/begin/<hour>/<minute>")
def update_t_begin(hour, minute):
    hour = int(hour)
    minute = int(minute)
    print("Start time set to {:02d}:{:02d}".format(hour, minute))
    global t_begin
    global delay
    t_begin = (hour, minute)
    update_delay(delay)
    
@app.route("/end/<hour>/<minute>")
def update_t_end(hour, minute):
    global t_end
    t_end = (hour, minute)
    
@app.route("/delay/<mins>")
def update_delay(mins):
    mins = int(mins)
    global delay
    global t_end
    delay = mins
    t_end = ((t_begin[0]+((t_begin[1]+delay)//60))%24,(t_begin[1]+delay)%60)
    print("end time: " + str(t_end))
    
@app.route("/lamp/on")
def lamp_on():
    light_on()
    
@app.route("/lamp/off")
def lamp_off():
    light_off()

@app.route("/alm/on")
def alarm_en():
    global alarm_enable
    alarm_enable = True
    print("Alarm enabled")

@app.route("/alm/off")
def alarm_disable():
    global alarm_enable
    alarm_enable = False
    print("Alarm disabled")

@app.route("/artificial")
def artificial():
    global use_lamp
    use_lamp = True
    print("Artificial light")

@app.route("/natural")
def natural():
    global use_lamp
    use_lamp = False
    print("Natural light")

def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(rbutton, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(lbutton, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(ubutton, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(dbutton, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(cbutton, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def rf_init():
    pipes = [[0xE0, 0xE0, 0xF1, 0xF1, 0xE0], [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]]
    radio.begin(0,25) # CSN = gpio 25
    radio.setPayloadSize(2) # set payload size in bytes
    radio.setChannel(0x76)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MIN)
    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()
    radio.openWritingPipe(pipes[0])
    radio.printDetails()
    
def light_on():
    r = requests.post('https://maker.ifttt.com/trigger/wakeup/with/key/cgxZVCzSNTNg7aOrlUNmV2', params={'value1':'none','value2':'none','value3':'none'})
    
def light_off():
    r = requests.post('https://maker.ifttt.com/trigger/turnoff/with/key/cgxZVCzSNTNg7aOrlUNmV2', params={'value1':'none','value2':'none','value3':'none'})
    
# Fully open blinds
def tilt_open():
    global tiltCurrent
    global tiltStatus
    while tiltCurrent < t_tilt:
        radio.write(['f','s'])
        tiltCurrent += 1
        time.sleep(0.1)
    radio.write(['s','s'])
    
def tilt_close():
    global tiltCurrent
    global tiltStatus
    while tiltCurrent > 0:
        radio.write(['r','s'])
        tiltCurrent -= 1
        time.sleep(0.1)
    radio.write(['s','s'])

# Handle right button
def next_state(_):
    global state
    state = (state + 1) % 6
    
# Handle left button
def prev_state(_):
    global state
    state = (state - 1) % 6
    
# Handle up button
def up(_):
    global t_begin
    global t_end
    global delay
    if not GPIO.input(ubutton):
        if state == 0:
            light_on()
        elif state == 1:
            tilt_up()
        elif state == 2:
            lift_up()
        elif state == 3:
            h, m = t_begin
            t_begin = ((h+1)%24,m)
            update_delay(delay)
        elif state == 4:
            h, m = t_begin
            t_begin = (h,(m+5)%60)
            update_delay(delay)
        elif state == 5:
            update_delay(delay + 1)
    else:
        if state == 1:
            tilt_stop()
        elif state == 2:
            lift_stop()

# Handle down button
def dn(_):
    global t_begin
    global t_end
    global delay
    if not GPIO.input(dbutton):
        if state == 0:
            light_off()
        elif state == 1:
            tilt_down()
        elif state == 2:
            lift_down()
        elif state == 3:
            h,m = t_begin
            t_begin = ((h-1)%24,m)
            update_delay(delay)
        elif state == 4:
            h,m = t_begin
            t_begin = (h,(m-5)%60)
            update_delay(delay)
        elif state == 5:
            update_delay(max(delay-1,1))
    else:
        if state == 1:
            tilt_stop()
        elif state == 2:
            lift_stop()
    
# Handle center button
def center(_):
    global ip_mode
    if wake:
        alarm_off()
    elif state == 0:
        ip_mode = not ip_mode
    elif state == 1:
        tilt_auto()
        
def alarm_on():
    pg.mixer.music.play(-1) # repeat indefinitely
    global alarm_flag
    alarm_flag = True
    
def alarm_off():
    global wake
    if alarm_flag:
        pg.mixer.music.stop()
    wake = False
    
def main_loop():
    light_flag = False
    count = 0
    global tiltCurrent
    global alarm_flag
    global wake
    while True:
        # Get time every 1.2 seconds
        if count % 12 == 0:
            t = list(time.localtime())
            cur_time = (t[3],t[4])
        # States
        if state == 0:
            if ip_mode:
                show_ip()
            elif wake:
                display.print("WAKE")
            else:
                display.print("{:02d}.{:02d}".format(t[3],t[4]))
        elif state == 1: # tilt control
            display.print("TILT")
        elif state == 2: # lift control
            display.print("LIFT")
        elif state == 3 or state == 4: # set clock
            if count % 6 == 0: # blink on
                display.print("{:02d}.{:02d}".format(t_begin[0],t_begin[1]))
            if (count + 3) % 6 == 0: # blink off
                if state == 3:
                    display.print("  .{:02d}".format(t_begin[1]))
                else:
                    display.print("{:02d}.  ".format(t_begin[0]))
        elif state == 5:
            display.print("  .{:02d}".format(delay))
        # Trigger alarms
        if alarm_enable:
            if cur_time == t_begin and not light_flag: # time for the light to turn on
                print("Activating lamp/blinds")
                wake = True
                if use_lamp:
                    print("Activating lamp")
                    light_on()
                else:
                    print("Activating blinds")
                    tilt_open()
                light_flag = True
            if cur_time != t_begin and light_flag: # reset light flag
                light_flag = False
            if cur_time == t_end and not alarm_flag:
                print("Activating alarm")
                alarm_on()
            if cur_time != t_end and alarm_flag:
                alarm_flag = False
        time.sleep(0.1)
        radio.write([tiltStatus, liftStatus])
        # increment or decrement tilt status accordingly
        if tiltStatus == 'f':
            tiltCurrent += 1
        elif tiltStatus == 'r':
            tiltCurrent -= 1
        count += 1
        if count == 6:
            print(tiltStatus, liftStatus)
        if count == 24:
            count = 0   # Reset count after 2.4 seconds

def show_ip():
    s = str(subprocess.check_output(['hostname','-I']))
    l = s.split()[0][2:].split('.')
    i = 0
    while ip_mode:
        display.print("{:>4}".format(l[i]))
        i += 1
        if i > 3: i = 0
        time.sleep(2)
        
# Set the time needed to open or close the blinds
def calibrate():
    display.print("OPEN")
    while GPIO.input(cbutton): # center button not pressed, wait
        if not GPIO.input(dbutton):
            radio.write(['r','s']) # reverse
        elif not GPIO.input(ubutton):
            radio.write(['f','s'])
        else:
            radio.write(['s','s'])
        time.sleep(0.1)
    time.sleep(0.1) # debounce
    display.print("CLOS")
    while not GPIO.input(cbutton): # center button pressed, wait
        pass
    time.sleep(0.1) # debounce
    tmp = 0
    while GPIO.input(cbutton):
        if not GPIO.input(dbutton):
            tmp += 1
            radio.write(['r','s'])
        else:
            radio.write(['s','s'])
        time.sleep(0.1)
    global t_tilt
    t_tilt = tmp
    print(t_tilt)
    time.sleep(1)

if __name__ == "__main__":
    gpio_init()
    rf_init()
    pg.mixer.init(44100, -16, 2, 2048)
    pg.mixer.music.load("/home/pi/Documents/python/alarm.mp3")
    display.fill(0)
    display.brightness = 15
    calibrate()
    GPIO.add_event_detect(rbutton, GPIO.RISING, callback = next_state, bouncetime = 100)
    GPIO.add_event_detect(lbutton, GPIO.RISING, callback = prev_state, bouncetime = 100)
    GPIO.add_event_detect(ubutton, GPIO.BOTH, callback = up, bouncetime = 100)
    GPIO.add_event_detect(dbutton, GPIO.BOTH, callback = dn, bouncetime = 100)
    GPIO.add_event_detect(cbutton, GPIO.RISING, callback = center, bouncetime = 100)
    timeThread = Thread(target=main_loop)
    timeThread.setDaemon(True)
    timeThread.start()
    light_off()
    app.run(host="0.0.0.0", port=80, debug=False)
    
