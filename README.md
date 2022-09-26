# Rumble de K9CTS

Rumble is a mumble client that streams audio from your microphone to a mumble server.

# Installation

## Prerequsites
````
sudo apt install pip
pip install pymumble
````

# Manual

## Configuring your audio card

If you hear no audio, it may be because your audio card isn't set to be the default card.
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

Sample Key Creation:

````
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout private-key.pem -out public-key.pem
````

