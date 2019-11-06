from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
import datetime
import spidev
from lib_nrf24 import NRF24
import requests

message_len = 16 # RF message length in bytes
pin_test_button = 26
pin_test_2 = 19
t_begin = datetime.time(hour=7) # initialize to a 7:00 alarm
t_end = datetime.time(hour=7, minute=30)

app = Flask(__name__)

@app.route("/tilt/up")
def tilt_up():
    print("tilt up")
    return "tilt manual"
    
@app.route("/tilt/down")
def tilt_down():
    print("tilt down")
    return "tilt manual"
    
@app.route("/tilt/stop")
def tilt_stop():
    print("tilt stop")
    return "tilt manual"
    
@app.route("/tilt/auto")
def tilt_auto():
    print("tilt auto")
    return "tilt auto"
    
@app.route("/begin/<hour>/<minute>")
def update_t_begin(hour, minute):
    t_begin = datetime.time(hour=hour, minute=minute)
    
@app.route("/end/<hour>/<minute>")
def update_t_end(hour, minute):
    t_end = datetime.time(hour=hour, minute=minute)
    
@app.route("/lamp/on")
def lamp_on():
    light_on()
    
@app.route("/lamp/off")
def lamp_off():
    light_off()

def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_test_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(pin_test_2, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def button_event(radio, n, high_msg, low_msg):
    if GPIO.input(n):
        rf_send(radio, high_msg)
    else:
        rf_send(radio, low_msg)

def rf_init():
    pipes = [[0xE0, 0xE0, 0xF1, 0xF1, 0xE0], [0xF1, 0xF1, 0xF0, 0xF0, 0xE0]]
    radio = NRF24(GPIO, spidev.SpiDev())
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
    return radio
    
def rf_send(radio, message):
    l_message = list(message)
    while len(l_message) < message_len:
        l_message.append(0)
    radio.write(l_message)
    print("sent " + message)
    
def light_on():
    r = requests.post('https://maker.ifttt.com/trigger/wakeup/with/key/MDu6JdUxxLRAy6GglSwmo', params={'value1':'none','value2':'none','value3':'none'})
    
def light_off():
    r = requests.post('https://maker.ifttt.com/trigger/turnoff/with/key/MDu6JdUxxLRAy6GglSwmo', params={'value1':'none','value2':'none','value3':'none'})

if __name__ == "__main__":
    gpio_init()
    radio = rf_init()
    GPIO.add_event_detect(pin_test_button, GPIO.BOTH, callback = lambda _:
        button_event(radio, pin_test_button, "test off", "test on"), bouncetime
        = 100)
    GPIO.add_event_detect(pin_test_2, GPIO.BOTH, callback = lambda _:
        button_event(radio, pin_test_2, "test2 off", "test2 on"), bouncetime =
        100)
    app.run(host="0.0.0.0", port=80, debug=False)
    
