#!/usr/bin/env python3
import subprocess
import re

s = subprocess.check_output(['zpool', 'list', '-PLv']).decode("utf-8")
ss = s.split('\n')
ss.pop(0) #drop header
data = {}
drives = []
index = "Unknown"
for l in ss:
    nl = re.sub(' +', ' ', l).strip() #strip whitespace throughout
    if len(l) < 4:
        continue
    elif l[0] != " ": #no spaces, new pool
        if len(drives) != 0:
            data[index] = {"health": pool_health, 'drives': drives}
            drives = []
        index = nl.split(" ")[0]
        pool_health = nl.split(" ")[9]
    elif "/dev/" in l:
        drive = nl.split(" ")[0].split('/')[2][0:-1]
        sd = subprocess.check_output(['realpath', "/sys/block/"+drive]).decode("utf-8").strip()
        if "expander" in sd:
            target = sd.split('/')[12].split(':')
            port = target[2]
            enc_path = sd+"/../../../"+target[0]+":"+target[1]+":"+target[2]+":0/enclosure_device:"+target[2]
            enc_path = subprocess.check_output(['realpath', enc_path]).decode("utf-8").strip()
            health = nl.split(" ")[9]
            drives.append({'drive': drive, 'path': sd, 'health': health, 'enc_path': enc_path.strip()})

data[index] = {'drives': drives, "health": pool_health}

actions = {}
for pool in data:
    if data[pool]['health'] != "ONLINE":
        print("Pool " + pool + " is not healthy.")
        for d in data[pool]['drives']:
            if d['health'] != "ONLINE": # If drive is not healthy set locate on, fault off
                print("Setting drive to ident on")
                if d['enc_path']+'/fault' in actions:
                    actions[d['enc_path']+'/fault'] = actions[d['enc_path']+'/fault'] or False
                else:
                    actions[d['enc_path'] + '/fault'] = False
                if d['enc_path']+'/locate' in actions:
                    actions[d['enc_path']+'/locate'] = actions[d['enc_path']+'/locate'] or True
                else:
                    actions[d['enc_path'] + '/locate'] = True
            else: # If drive is healthy only set fault
                print("Setting drive to fault on")
                if d['enc_path']+'/fault' in actions:
                    actions[d['enc_path']+'/fault'] = actions[d['enc_path']+'/fault'] or True
                else:
                    actions[d['enc_path'] + '/fault'] = True
                if d['enc_path']+'/locate' in actions:
                    actions[d['enc_path']+'/locate'] = actions[d['enc_path']+'/locate'] or False
                else:
                    actions[d['enc_path'] + '/locate'] = False
    else: # pool is OK
        if "scrub in progress" in subprocess.check_output(['zpool', 'status', pool]).decode("utf-8"):
            print("Pool " + pool + " is scrubbing")
            for d in data[pool]['drives']:
                print("Setting drive to locate on")
                if d['enc_path']+'/fault' in actions:
                    actions[d['enc_path']+'/fault'] = actions[d['enc_path']+'/fault'] or False
                else:
                    actions[d['enc_path'] + '/fault'] = False
                if d['enc_path']+'/locate' in actions:
                    actions[d['enc_path']+'/locate'] = actions[d['enc_path']+'/locate'] or True
                else:
                    actions[d['enc_path'] + '/locate'] = True
        else: # no scrub in progress, turn off all lights
            print("Pool " + pool + " is healthy and inactive")
            for d in data[pool]['drives']:
                #print("Setting drive LEDs off")
                if d['enc_path']+'/fault' in actions:
                    actions[d['enc_path']+'/fault'] = actions[d['enc_path']+'/fault'] or False
                else:
                    actions[d['enc_path'] + '/fault'] = False
                if d['enc_path']+'/locate' in actions:
                    actions[d['enc_path']+'/locate'] = actions[d['enc_path']+'/locate'] or False
                else:
                    actions[d['enc_path'] + '/locate'] = False

for action in actions:
    if actions[action] and subprocess.check_output(['cat', action]).decode("utf-8").strip() == "0":
        print('echo' + ' "1" ' + " > " + action)
        subprocess.check_output(['/usr/bin/echo "1" > ' + action], shell=True).decode("utf-8")
    elif not actions[action] and subprocess.check_output(['cat', action]).decode("utf-8").strip() != "0":
        print('echo' + ' "0" ' + " > " + action)
        subprocess.check_output(['/usr/bin/echo "0" > ' + action], shell=True).decode("utf-8")

