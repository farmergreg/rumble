#!/usr/bin/python3
# Copyright 2022 by Gregory L. Dietsche (K9CTS)
# License: MIT

import argparse
import pyaudio
import pymumble_py3
from pymumble_py3.constants import *
from threading import Thread, Event

parser = argparse.ArgumentParser(prog='rumble', description='rumble streams audio from your microphone input')
parser.add_argument('--cert-file', nargs='?',  dest='certfile', default=None, help='PEM encoded public key certificate')
parser.add_argument('--cert-key', nargs='?',  dest='certkey', default=None, help='PEM encoded private key certificate')
parser.add_argument('--channel', nargs='?',  dest='channel', default='', help='the channel to join')
parser.add_argument('--password', nargs='?',  dest='password', default='' ,help='mumble server password')
parser.add_argument('--port', nargs='?',  dest='port', default=64738, help='the server to connect to (default "64738")')
parser.add_argument('--reconnect',  dest='reconnect', action='store_true', help='reconnect if the connection is lost')
parser.add_argument('--server', nargs='?',  dest='server', default='localhost', help='the server to connect to (default "localhost")')
parser.add_argument('--username', dest='username', help='the username of the client')
args = parser.parse_args()

IsConnected = Event()
def OnConnected():
        IsConnected.set()
        print("Connected.")
        mumble.channels.find_by_name(args.channel).move_in()

def OnDisconnected():
    IsConnected.clear()
    print("Server Disconnected.")

    if args.reconnect:
        print("Attempting to reconnect...")

pyAudioBufferSize=1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, output=False, frames_per_buffer=pyAudioBufferSize)

mumble = pymumble_py3.Mumble(args.server, args.username, password=args.password, port=args.port, certfile=args.certfile, keyfile=args.certkey, reconnect=args.reconnect)
mumble.set_application_string("Rumble de K9CTS")
mumble.start()
mumble.callbacks.set_callback(PYMUMBLE_CLBK_CONNECTED, OnConnected)
mumble.callbacks.set_callback(PYMUMBLE_CLBK_DISCONNECTED, OnDisconnected)
mumble.is_ready()

# mumble.channels.find_by_name(args.channel).move_in()

while True:
    data = stream.read(pyAudioBufferSize, exception_on_overflow=False)
    if IsConnected.is_set():
        mumble.sound_output.add_sound(data)

stream.stop_stream()
stream.close()
p.terminate()

