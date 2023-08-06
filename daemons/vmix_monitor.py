#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
import socket
import datetime

VMIX_SERVER = "172.16.24.122"
VMIX_PORT   = 8099

while (1):
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((VMIX_SERVER, VMIX_PORT))
            s.recv(1024)
            s.sendall("XMLTEXT vmix/streaming\n".encode('UTF-8'))
            stream = s.recv(1024).decode('UTF-8')
            s.sendall("XMLTEXT vmix/recording\n".encode('UTF-8'))
            rec = s.recv(1024).decode('UTF-8')

            statStream = "OFF"
            statRec    = "OFF"
            statOnAir  = "OFF"

            if "True" in stream:
                statStream = "ON"
                statOnAir  = "ON"

            if "True" in rec:
                statRec    = "ON"
                statOnAir  = "ON"

            client = mqtt.Client("vmix")
            client.connect('127.0.0.1')
            client.publish('vmix/onair',statOnAir)
            client.publish('vmix/stream',statStream)
            client.publish('vmix/record',statRec)
            client.publish('vmix/last', str(datetime.datetime.now()))

    except Exception as e:
        print(f"Got error: {e}")

    time.sleep(1)

