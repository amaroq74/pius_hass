#!/usr/bin/env python3

import sys

from pypjlink import Projector, MUTE_VIDEO
import paho.mqtt.client as mqtt

import threading
import datetime
import time
import queue

ProjAddrs = {'StageRight' : 'ch-proj1.pius.org',
             'Center'     : 'ch-proj2.pius.org',
             'StageLeft'  : 'ch-proj3.pius.org'}

class ProjectorInterface(object):

    def __init__(self, name, addr):
        self.name   = name
        self.addr   = addr
        self.status = ""
        self.last   = ""
        self.queue  = queue.SimpleQueue()
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.runEnable = True
        self.thread.start()

    def stop(self):
        self.runEnable = False
        self.thread.join()

    def on_message(self, client, userdata, msg):
        if msg.payload == b"1":
            self.queue.put(True)
        elif msg.payload == b"0":
            self.queue.put(False)

    def run(self):
        proj = None
        client = None

        last = time.time()

        while self.runEnable:

            if client is None:
                print("Connecting to mqtt server")
                client = mqtt.Client(f"proj_{self.name}")
                client.connect('127.0.0.1')
                client.on_message = self.on_message
                client.subscribe(f"{self.name}/request")
                print("Connected to mqtt server")

            if time.time() - last > 1.0:
                try:
                    if proj is None:
                        print("Connecting to projector")
                        proj = Projector.from_address(self.addr)
                        proj.authenticate('admin')
                        print("Connected to projector")

                    if self.queue.empty() is False:
                        st = self.queue.get_nowait()

                        if st:
                            proj.set_power('on')
                        else:
                            proj.set_power('off')

                        continue

                    s = proj.get_power().strip()
                    l = str(datetime.datetime.now())

                    if s == 'off':
                        so = 0
                    else:
                        so = 1

                    #print(f"{self.name} |{s}| |{so}| |{l}|")
                    client.publish(f'{self.name}/state', so)
                    client.publish(f'{self.name}/status',s)
                    client.publish(f'{self.name}/last' , l)

                except Exception as e:
                    print(f"Got message error {e}")
                    proj = None
                    client = None
                    time.sleep(60)

                last = time.time()

            if client is not None:
                client.loop()
            time.sleep(.25)

projs = []

for k,v in ProjAddrs.items():
    projs.append(ProjectorInterface(k, v))

for p in projs:
    p.start()

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Got cntrl-c, exiting")

for p in projs:
    p.stop()

