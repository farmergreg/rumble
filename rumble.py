#!/usr/bin/python3
# Copyright 2024 by Gregory L. Dietsche
# License: MIT
MyVersion = 'v1.0.3'

import os
import argparse
from datetime import datetime, timedelta
import pyaudio
import audioop
import pymumble_py3
from pymumble_py3.constants import *
from threading import Thread, Event
import signal
import requests
import time

argParser = argparse.ArgumentParser(prog='rumble',     description='rumble streams audio from your microphone input')
argParser.add_argument('--cert-file', nargs='?',      dest='certfile',                 default=os.getenv('RUMBLE_CERTFILE'),              help='PEM encoded public key certificate')
argParser.add_argument('--cert-key',  nargs='?',      dest='certkey',                  default=os.getenv('RUMBLE_CERTKEY'),               help='PEM encoded private key certificate')
argParser.add_argument('--channel',   nargs='?',      dest='channel',                  default=os.getenv('RUMBLE_CHANNEL'),               help='the channel to join')
argParser.add_argument('--password',  nargs='?',      dest='password',                 default=os.getenv('RUMBLE_PASSWORD', ''),          help='the server password')
argParser.add_argument('--port',      nargs='?',      dest='port',                     default=os.getenv('RUMBLE_PORT', 64738),           help='the server to connect to (default "64738")',                 type=int)
argParser.add_argument('--server',    nargs='?',      dest='server',                   default=os.getenv('RUMBLE_SERVER', 'localhost'),   help='the server to connect to (default "localhost")')
argParser.add_argument('--username',                  dest='username',                 default=os.getenv('RUMBLE_USERNAME', 'rumble-bot'),help='the username of the client (default "rumble-bot")')
argParser.add_argument('--min-rms',                   dest='minRMS',                   default=os.getenv('RUMBLE_MINRMS', 200),           help='minimum rms level required to transmit audio (default 200)', type=int)
argParser.add_argument('--webhook-watchdog-interval', dest='webhook_watchdog_interval',default=int(os.getenv('RUMBLE_WEBHOOK_WATCHDOG_INTERVAL', 61)), help='Interval in seconds for the watchdog to check the connection', type=int)
argParser.add_argument('--webhook-watchdog-up',       dest='webhook_watchdog_up',      default=os.getenv('RUMBLE_WEBHOOK_WATCHDOG_UP'),   help='URL to GET periodically when connected')
argParser.add_argument('--webhook-watchdog-down',     dest='webhook_watchdog_down',    default=os.getenv('RUMBLE_WEBHOOK_WATCHDOG_DOWN'), help='URL to GET periodically when disconnected')

###############################################################################
## Global Variables
###############################################################################
MyArgs = argParser.parse_args()
IsConnected = Event()
ExitNowPlease = Event()

###############################################################################
## Event Handlers & Functions
###############################################################################
def Log(message):
    print(datetime.now().strftime('[%Y-%m-%d %H:%M:%S]: ') + message)

def OnCtrlC(signum, frame):
    print()
    ExitNowPlease.set()

def OnConnected():
    IsConnected.set()
    Log(f'Connected to {MyArgs.server}:{MyArgs.port} as {MyArgs.username}')

    if MyArgs.channel != None:
        mumble.channels.find_by_name(MyArgs.channel).move_in()
        Log(f'Joined channel: {MyArgs.channel}')

    WatchdogHTTPUpdate()

def OnDisconnected():
    IsConnected.clear()
    Log(f'Disconnected from {MyArgs.server}:{MyArgs.port}')

    WatchdogHTTPUpdate()

    if not ExitNowPlease.is_set():
        Log('Attempting to reconnect...')

def Watchdog():
    while not ExitNowPlease.is_set():
        time.sleep(MyArgs.webhook_watchdog_interval)
        WatchdogHTTPUpdate()

def WatchdogHTTPUpdate():
    if IsConnected.is_set():
        if MyArgs.webhook_watchdog_up:
            try:
                response = requests.get(MyArgs.webhook_watchdog_up)
                Log(f'Webhook watchdog UP response: {response.status_code} {response.text}')
            except requests.RequestException as e:
                Log(f'Error calling watchdog UP webhook: {e}')
    else:
        if MyArgs.webhook_watchdog_down:
            try:
                response = requests.get(MyArgs.webhook_watchdog_down)
                Log(f'Webhook watchdog DOWN response: {response.status_code} {response.text}')
            except requests.RequestException as e:
                Log(f'Error calling watchdog DOWN webhook: {e}')

###############################################################################
## Main Program
###############################################################################
Log(" _______  _____  _____  ____    ____  ______   _____     ________  ")
Log("|_   __ \|_   _||_   _||_   \  /   _||_   _ \ |_   _|   |_   __  | ")
Log("  | |__) | | |    | |    |   \/   |    | |_) |  | |       | |_ \_| ")
Log("  |  __ /  | '    ' |    | |\  /| |    |  __'.  | |   _   |  _| _  ")
Log(" _| |  \ \_ \ \__/ /    _| |_\/_| |_  _| |__) |_| |__/ | _| |__/ | ")
Log("|____| |___| `.__.'    |_____||_____||_______/|________||________|")
Log('rumble ' + MyVersion)
Log('Copyright 2024 by Gregory L. Dietsche')
Log('License: MIT')
Log('')
Log('Parameters:')
for curArg in vars(MyArgs):
    Log(f'{curArg}\t: {getattr(MyArgs, curArg)}')
Log('')

Log('Initializing audio...')
pyAudioBufferSize=1024
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, frames_per_buffer=pyAudioBufferSize)

Log('Initializing mumble client...')
mumble = pymumble_py3.Mumble(MyArgs.server, MyArgs.username, password=MyArgs.password, port=MyArgs.port, certfile=MyArgs.certfile, keyfile=MyArgs.certkey, reconnect=True)
mumble.set_application_string('Rumble by Gregory L. Dietsche')
mumble.callbacks.set_callback(PYMUMBLE_CLBK_CONNECTED, OnConnected)
mumble.callbacks.set_callback(PYMUMBLE_CLBK_DISCONNECTED, OnDisconnected)

Log(f'Initializing connection to {MyArgs.server}:{MyArgs.port}...')
mumble.start()
mumble.is_ready()

Log(f'Minimum RMS required to transmit audio: {MyArgs.minRMS}')
peakRMS = 0
recordUntil = datetime.now()
isTransmitting = False
signal.signal(signal.SIGINT, OnCtrlC)
signal.signal(signal.SIGTERM, OnCtrlC)

watchdog_thread = Thread(target=Watchdog)
watchdog_thread.start()

while not ExitNowPlease.is_set():
    soundSample = stream.read(pyAudioBufferSize, exception_on_overflow=False)
    rms = audioop.rms(soundSample, 2) #paInt16 is 2 bytes wide

    if rms>peakRMS:
        peakRMS = rms
        Log(f'New audio RMS peak: {peakRMS}')

    if rms>MyArgs.minRMS:
        recordUntil=datetime.now()+timedelta(milliseconds=250)

    if IsConnected.is_set() and recordUntil > datetime.now():
        if isTransmitting == False:
            Log("Transmission Started")
            isTransmitting = True
        mumble.sound_output.add_sound(soundSample)
    elif isTransmitting:
        Log("Transmission Ended")
        isTransmitting = False

# pressing Ctrl-C will cause this code to execute...
Log("Shutting Down")
stream.stop_stream()
stream.close()
audio.terminate()
mumble.stop()
