# Rumble de K9CTS

Rumble is a mumble client that streams audio from your microphone to a mumble server.

# Installation

Tested with Raspberry PI OS Lite (Debian Bullseye with no desktop environment)

````
sudo apt update
sudo apt install git python3-pip python3-pyaudio opus-tools
pip install pyaudio
pip install pymumble
````

# Configuring your audio card

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

## SSL Key Creation

If you want to authenticate using SSL, here is one way to create a self-signed key pair.

````
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout private-key.pem -out public-key.pem
````
