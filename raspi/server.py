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

#states: lamp/time, tilt, lift, hour, minute, delay

message_len = 16 # RF message length in bytes
lbutton = 26
rbutton = 13
ubutton = 12
dbutton = 16
cbutton = 20
state = 0
t_begin = (7,0) # initialize to a 7:00 alarm
delay = 30 # delay in minutes
use_lamp = False

radio = NRF24(GPIO, spidev.SpiDev())

i2c = busio.I2C(board.SCL, board.SDA)
display = segments.Seg14x4(i2c)

app = Flask(__name__)

@app.route("/tilt/up")
def tilt_up():
    rf_send("tilt up")
    
@app.route("/tilt/down")
def tilt_down():
    rf_send("tilt down")
    
@app.route("/tilt/stop")
def tilt_stop():
    rf_send("tilt stop")
    
@app.route("/tilt/auto")
def tilt_auto():
    print("tilt auto")
    return "tilt auto"
    
@app.route("/lift/up")
def lift_up():
    rf_send("lift up")

@app.route("/lift/down")
def lift_down():
    rf_send("lift down")

@app.route("/lift/stop")
def lift_stop():
    rf_send("lift stop")

@app.route("/begin/<hour>/<minute>")
def update_t_begin(hour, minute):
    hour = int(hour)
    minute = int(minute)
    print("Start time set to {:02d}:{:02d}".format(hour, minute))
    global t_begin
    t_begin = (hour, minute)
    
@app.route("/end/<hour>/<minute>")
def update_t_end(hour, minute):
    t_end = (hour, minute)
    
@app.route("/lamp/on")
def lamp_on():
    light_on()
    
@app.route("/lamp/off")
def lamp_off():
    light_off()

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
    radio.setPayloadSize(message_len) # set payload size in bytes
    radio.setChannel(0x76)
    radio.setDataRate(NRF24.BR_1MBPS)
    radio.setPALevel(NRF24.PA_MIN)
    radio.setAutoAck(True)
    radio.enableDynamicPayloads()
    radio.enableAckPayload()
    radio.openWritingPipe(pipes[0])
    radio.printDetails()
    
def rf_send(message):
    l_message = list(message)
    while len(l_message) < message_len:
        l_message.append(0)
    radio.write(l_message)
    print("sent " + message)
    
def light_on():
    r = requests.post('https://maker.ifttt.com/trigger/wakeup/with/key/cgxZVCzSNTNg7aOrlUNmV2', params={'value1':'none','value2':'none','value3':'none'})
    
def light_off():
    r = requests.post('https://maker.ifttt.com/trigger/turnoff/with/key/cgxZVCzSNTNg7aOrlUNmV2', params={'value1':'none','value2':'none','value3':'none'})
    
def next_state(_):
    global state
    state = (state + 1) % 7
    
def prev_state(_):
    global state
    state = (state - 1) % 7
    
def up(_):
    global t_begin
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
        elif state == 4:
            h, m = t_begin
            t_begin = (h,(m+5)%60)
        elif state == 5:
            delay = delay + 5
    else:
        if state == 1:
            tilt_stop()
        elif state == 2:
            lift_stop()
    
def dn(_):
    global t_begin
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
        elif state == 4:
            h,m = t_begin
            t_begin = (h,(m-5)%60)
        elif state == 5:
            delay = max(delay-5,5)
    else:
        if state == 1:
            tilt_stop()
        elif state == 2:
            lift_stop()
    
def center():
    if state == 1:
        tilt_auto()
        
def change_val(n):
    if state == 0:
        if n == 1:
            light_on()
        else:
            light_off()
    if state == 1:
        tilt_up()
    
def main_loop():
    light_flag = False
    count = 0
    while True:
        if count == 0:
            t = list(time.localtime())
            cur_time = (t[3],t[4])
        if state == 0:
            display.print("{:02d}.{:02d}".format(t[3],t[4]))
        elif state == 1:
            display.print("TILT")
        elif state == 2:
            display.print("LIFT")
        elif state == 3 or state == 4:
            if count % 6 == 0:
                display.print("{:02d}.{:02d}".format(t_begin[0],t_begin[1]))
            if (count + 3) % 6 == 0:
                if state == 3:
                    display.print("  .{:02d}".format(t_begin[1]))
                else:
                    display.print("{:02d}.  ".format(t_begin[0]))
        elif state == 5:
            display.print("  .{:02d}".format(delay))
        if cur_time == t_begin and not light_flag:
            print("Activating lamp")
            light_on()
            light_flag = True
        if cur_time != t_begin and light_flag:
            light_flag = False
        time.sleep(0.1)
        count += 1
        if count == 12:
            count = 0

if __name__ == "__main__":
    gpio_init()
    rf_init()
    display.fill(0)
    display.brightness = 15
    GPIO.add_event_detect(rbutton, GPIO.RISING, callback = next_state, bouncetime = 100)
    GPIO.add_event_detect(lbutton, GPIO.RISING, callback = prev_state, bouncetime = 100)
    GPIO.add_event_detect(ubutton, GPIO.BOTH, callback = up, bouncetime = 100)
    GPIO.add_event_detect(dbutton, GPIO.BOTH, callback = dn, bouncetime = 100)
    GPIO.add_event_detect(cbutton, GPIO.RISING, callback = center, bouncetime = 100)
    timeThread = Thread(target=main_loop)
    timeThread.setDaemon(True)
    timeThread.start()
    app.run(host="0.0.0.0", port=80, debug=False)
    
