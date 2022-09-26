# Rumble de K9CTS

Rumble is a mumble client that streams audio from your microphone to a mumble server.

# Installation

## Prerequsites
````
sudo apt install pip
pip install pymumble
````

# Manual

## SSL Key Creation

Sample Key Creation:

````
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout private-key.pem -out public-key.pem
````

