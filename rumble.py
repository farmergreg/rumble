#!/usr/bin/python3
# Copyright 2022 by Gregory L. Dietsche (K9CTS)
# License: MIT

import pymumble_py3
from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED as PCS
import pyaudio

import argparse

parser = argparse.ArgumentParser(prog='rumble', description='rumble streams audio from your microphone input')

parser.add_argument('--cert-key', nargs='?',  dest='certkey', default=None, help='PEM encoded private key certificate')
parser.add_argument('--cert-file', nargs='?',  dest='certfile', default=None, help='PEM encoded public key certificate')
parser.add_argument('--channel', nargs='?',  dest='channel', default='', help='the channel to join')
parser.add_argument('--insecure',  dest='insecure', action='store_true', help='skip server certificate verification')
parser.add_argument('--password', nargs='?',  dest='password', default=None ,help='mumble server password')
parser.add_argument('--server', nargs='?',  dest='server', default='localhost', help='the server to connect to (default "localhost")')
parser.add_argument('--port', nargs='?',  dest='port', default=64738, help='the server to connect to (default "64738")')
parser.add_argument('--username', dest='username', help='the username of the client')

args = parser.parse_args()

pyaudoBufferSize=1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=48000, input=True, output=False, frames_per_buffer=pyaudoBufferSize)

mumble = pymumble_py3.Mumble(args.server, args.username, password=args.password, port=args.port, certfile=args.certfile, keyfile=args.certkey)
mumble.set_application_string("Rumble de K9CTS")
mumble.start()
mumble.is_ready()

mumble.channels.find_by_name(args.channel).move_in()

while True:
    data = stream.read(pyaudoBufferSize, exception_on_overflow=False)
    mumble.sound_output.add_sound(data)

stream.stop_stream()
stream.close()
p.terminate()
