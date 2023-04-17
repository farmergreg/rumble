FROM ubuntu:jammy

RUN apt-get update && apt-get install -y \
  python3-pip \
  python3-pyaudio \
  opus-tools \
  && rm -rf /var/lib/apt/lists/*

RUN pip install pymumble

WORKDIR /rumble
COPY LICENSE.txt .
COPY README.md .
COPY rumble.py .

CMD cd /rumble && ./rumble.py
