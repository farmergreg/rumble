# Rumble de K9CTS

Rumble is a [mumble](https://www.mumble.info/) bot that streams audio from your microphone / line input.

# Using

Simple example:
````
./rumble.py --username test-bot --server mumble --port 64738 --password OneBadPassword
````

## Command Line Options:
````
usage: rumble [-h] [--cert-file [CERTFILE]] [--cert-key [CERTKEY]] [--channel [CHANNEL]] [--password [PASSWORD]] [--port [PORT]]
              [--server [SERVER]] [--username USERNAME] [--min-rms MINRMS]

rumble streams audio from your microphone input

optional arguments:
  -h, --help            show this help message and exit
  --cert-file [CERTFILE]
                        PEM encoded public key certificate
  --cert-key [CERTKEY]  PEM encoded private key certificate
  --channel [CHANNEL]   the channel to join
  --password [PASSWORD] the server password
  --port [PORT]         the server to connect to (default "64738")
  --server [SERVER]     the server to connect to (default "localhost")
  --username USERNAME   the username of the client (default "rumble-bot")
  --min-rms MINRMS      minimum rms level required to transmit audio (default 150)
  --webhook-connect     URL to GET on connect
  --webhook-disconnect  URL to GET on disconnect
````

## Environment Variables:
Command line parameters take precedence over environment variables.
The following environment variables are supported:

````
RUMBLE_CERTFILE=
RUMBLE_CERTKEY=
RUMBLE_CHANNEL=
RUMBLE_PASSWORD=
RUMBLE_PORT=64738
RUMBLE_SERVER=localhost
RUMBLE_USERNAME=rumble-bot
RUMBLE_MINRMS=150
RUMBLE_WEBHOOK_CONNECT=
RUMBLE_WEBHOOK_DISCONNECT=
````

# Installation

You can use any computer that runs linux to run mumble.
These instructions were tested with Raspberry PI OS Lite (Debian Bullseye with no desktop environment).
If you happen to use a Raspberry PI, you will need a usb sound card.

````
# Install
sudo apt update
sudo apt install git python3-pip python3-pyaudio opus-tools
pip install pymumble
git clone https://github.com/farmergreg/rumble

# Run the bot (change the parameters to suit your needs)
cd rumble
./rumble.py --username test-bot --server mumble --port 64738 --password OneBadPassword
````

# Audio Card Configuration

If rumble does not transmit any audio, it may be because your audio card isn't set to be the default card.
To check the cards on your system run:

````
cat /proc/asound/cards
````

Then edit /etc/asound.conf and add the text below.
In this example, we are using card number 1 as our default card:

````
defaults.pcm.card 1
defaults.ctl.card 1
````

# SSL Key Creation

If you want to authenticate using SSL, here is one way to create a self-signed key pair.

````
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout private-key.pem -out public-key.pem
````

# Starting Rumble Automatically

There are many ways to accomplish starting up rumble when your computer boots.
Here is one simple way:

## 1) Install tmux:
````
sudo apt install tmux
````

## 2) Edit crontab
Then edit your crontab and add this line (adjust the path to match where your copy of rumble is):

````
@reboot /usr/bin/tmux new-session -d -s rumble-bot '/home/pi/rumble/rumble.py --username test-bot --server mumble --port 64738 --password YourServerPasswordGoesHere' >/dev/null 2>&1
````

## 3) Reboot
Reboot your computer.
After rebooting, log in and check the output from your bot by running:

````
tmux attach
````

When you are done using tmux, press ctrl-b and then ctrl-d to detach from your bot (it will continue to run in the background).

