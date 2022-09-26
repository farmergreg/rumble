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

Then edit /etc/asound.conf and change the number 1 to the card number that you want to use.
If the file is blank, it is ok to edit it and add new text:

````
defaults.pcm.card 1
defaults.ctl.card 1
````

## SSL Key Creation

Sample Key Creation:

````
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout private-key.pem -out public-key.pem
````

