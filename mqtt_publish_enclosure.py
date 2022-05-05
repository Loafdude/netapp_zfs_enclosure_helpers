#!/usr/bin/env python3
import re
import json
import paho.mqtt.client as mqtt
import time
import subprocess

#message_frequency = 30 #seconds

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # client.subscribe("Home/Servers/DiskEnclosure/Set/#")

# The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))
#     index = s.split('/')[-1]
#     s = subprocess.check_output(['sg_ses', '--index='+index, msg.payload, '/dev/sg70']).decode("utf-8")

def getEnclosureStatus():
    s = subprocess.check_output(['sg_ses', '--all', '/dev/sg70']).decode("utf-8")
    data = {}
    es = re.split('\n\[|; \[', s)
    for e in es:
        if "]" not in e:
            index = "Header Data"
        else:
            index = re.sub(' +', ' ',e[0:e.find("]")])
            e = e[e.find("]")+1:9999]
        fs = re.split('\n|,', e)
        items = {}
        for f in fs:
            row = re.split('=|:', f)
            if len(row) == 2:
                items[re.sub(' +', ' ',row[0]).strip()] = re.sub(' +', ' ',row[1]).strip()
            elif len(row) == 1:
                items[re.sub(' +', ' ',row[0]).strip()] = ""
            elif len(row) == 0:
                continue
            else:
                items["String"] = re.sub(' +', ' ',f).strip()
            data[index] = items
    return json.dumps(data)

client = mqtt.Client()
client.on_connect = on_connect
#client.on_message = on_message
client.connect("10.9.8.184", 1883, 60)

json_output = getEnclosureStatus()
go = client.publish('Home/Servers/DiskEnclosure/Status', payload=json_output)

status = client.loop(timeout=5.0)

client.disconnect()

