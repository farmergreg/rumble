#!/usr/bin/python3
# Copyright 2022 by Gregory L. Dietsche (K9CTS)
# License: MIT

import argparse
import datetime
import pyaudio
import pymumble_py3
from pymumble_py3.constants import *
from threading import Thread, Event
import signal

argParser = argparse.ArgumentParser(prog='rumble', description='rumble streams audio from your microphone input')
argParser.add_argument('--cert-file', nargs='?',  dest='certfile', default=None, help='PEM encoded public key certificate')
argParser.add_argument('--cert-key', nargs='?',  dest='certkey', default=None, help='PEM encoded private key certificate')
argParser.add_argument('--channel', nargs='?',  dest='channel', default='', help='the channel to join')
argParser.add_argument('--password', nargs='?',  dest='password', default='' ,help='mumble server password')
argParser.add_argument('--port', nargs='?',  dest='port', default=64738, help='the server to connect to (default "64738")')
argParser.add_argument('--server', nargs='?',  dest='server', default='localhost', help='the server to connect to (default "localhost")')
argParser.add_argument('--username', dest='username', help='the username of the client')

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
    print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S]: ') + message)

def OnCtrlC(signum, frame):
    ExitNowPlease.set()

def OnConnected():
        IsConnected.set()
        Log(f"Connected to: {MyArgs.server}:{MyArgs.port} as {MyArgs.username}")
        mumble.channels.find_by_name(MyArgs.channel).move_in()
        Log(f"Joined channel: {MyArgs.channel}")

def OnDisconnected():
    IsConnected.clear()
    Log(f"Disconnected from: {MyArgs.server}:{MyArgs.port}")

    if not ExitNowPlease.is_set():
        Log("Attempting to reconnect...")

###############################################################################
## Main Program
###############################################################################
Log("rumble is starting up...")
pyAudioBufferSize=1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, output=False, frames_per_buffer=pyAudioBufferSize)
signal.signal(signal.SIGINT, OnCtrlC)

mumble = pymumble_py3.Mumble(MyArgs.server, MyArgs.username, password=MyArgs.password, port=MyArgs.port, certfile=MyArgs.certfile, keyfile=MyArgs.certkey, reconnect=True)
mumble.set_application_string("Rumble de K9CTS")
mumble.start()
mumble.callbacks.set_callback(PYMUMBLE_CLBK_CONNECTED, OnConnected)
mumble.callbacks.set_callback(PYMUMBLE_CLBK_DISCONNECTED, OnDisconnected)
mumble.is_ready()
Log("ready to rumble")

while not ExitNowPlease.is_set():
    data = stream.read(pyAudioBufferSize, exception_on_overflow=False)
    if IsConnected.is_set():
        mumble.sound_output.add_sound(data)

stream.stop_stream()
stream.close()
p.terminate()
