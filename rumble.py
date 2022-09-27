#!/usr/bin/python3
# Copyright 2022 by Gregory L. Dietsche (K9CTS)
# License: MIT

import argparse
from datetime import datetime, timedelta
import pyaudio
import audioop
import pymumble_py3
from pymumble_py3.constants import *
from threading import Thread, Event
import signal

argParser = argparse.ArgumentParser(prog='rumble', description='rumble streams audio from your microphone input')
argParser.add_argument('--cert-file', nargs='?',  dest='certfile', default=None, help='PEM encoded public key certificate')
argParser.add_argument('--cert-key', nargs='?',  dest='certkey', default=None, help='PEM encoded private key certificate')
argParser.add_argument('--channel', nargs='?',  dest='channel', default=None, help='the channel to join')
argParser.add_argument('--password', nargs='?',  dest='password', default='' ,help='mumble server password')
argParser.add_argument('--port', nargs='?',  dest='port', default=64738, help='the server to connect to (default "64738")')
argParser.add_argument('--server', nargs='?',  dest='server', default='localhost', help='the server to connect to (default "localhost")')
argParser.add_argument('--username', dest='username', help='the username of the client')
argParser.add_argument('--min-rms', dest='minRMS', default=20, help='minimum rms level required to transmit audio (default 20)')

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

def OnDisconnected():
    IsConnected.clear()
    Log(f'Disconnected from {MyArgs.server}:{MyArgs.port}')

    if not ExitNowPlease.is_set():
        Log('Attempting to reconnect...')

###############################################################################
## Main Program
###############################################################################
Log(" _______  _____  _____  ____    ____  ______   _____     ________  ")
Log("|_   __ \|_   _||_   _||_   \  /   _||_   _ \ |_   _|   |_   __  | ")
Log("  | |__) | | |    | |    |   \/   |    | |_) |  | |       | |_ \_| ")
Log("  |  __ /  | '    ' |    | |\  /| |    |  __'.  | |   _   |  _| _  ")
Log(" _| |  \ \_ \ \__/ /    _| |_\/_| |_  _| |__) |_| |__/ | _| |__/ | ")
Log("|____| |___| `.__.'    |_____||_____||_______/|________||________|")
Log('rumble v1.0.0')
Log('Copyright 2022 by Gregory L. Dietsche (K9CTS)')
Log('License: MIT')

Log('Initializing audio...')
pyAudioBufferSize=1024
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, output=False, frames_per_buffer=pyAudioBufferSize)
signal.signal(signal.SIGINT, OnCtrlC)

Log('Initializing mumble client...')
mumble = pymumble_py3.Mumble(MyArgs.server, MyArgs.username, password=MyArgs.password, port=MyArgs.port, certfile=MyArgs.certfile, keyfile=MyArgs.certkey, reconnect=True)
mumble.set_application_string('Rumble de K9CTS')
mumble.callbacks.set_callback(PYMUMBLE_CLBK_CONNECTED, OnConnected)
mumble.callbacks.set_callback(PYMUMBLE_CLBK_DISCONNECTED, OnDisconnected)

Log(f'Initializing connection to {MyArgs.server}:{MyArgs.port}...')
mumble.start()
mumble.is_ready()

Log(f'Minimum RMS required to trigger audio transmission: {MyArgs.minRMS}')
peakRMS = 0
recordUntil = datetime.now()
while not ExitNowPlease.is_set():
    soundSample = stream.read(pyAudioBufferSize, exception_on_overflow=False)
    rms = audioop.rms(soundSample, 2) #paInt16 is 2 bytes wide

    if rms>peakRMS:
        peakRMS = rms
        Log(f'New audio RMS peak: {peakRMS}')

    if rms>MyArgs.minRMS:
        recordUntil=datetime.now()+timedelta(milliseconds=250)

    if IsConnected.is_set() and recordUntil > datetime.now():
        mumble.sound_output.add_sound(soundSample)

stream.stop_stream()
stream.close()
audio.terminate()
mumble.stop()
