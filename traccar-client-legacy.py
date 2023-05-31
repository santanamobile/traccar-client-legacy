#!/usr/bin/env python
#
# Traccar Client Protocol
# https://www.traccar.org/traccar-client-protocol/
#

from gps import *
import socket, urllib3
import math, operator
from functools import reduce
import json

with open("settings.json") as configFile:
    config = json.load(configFile)

TRACCAR_SERVER        = config["TRACCAR_SERVER"]
TRACCAR_PORT          = config["TRACCAR_PORT"]
TRACCAR_PROTOCOL_PORT = config["TRACCAR_PROTOCOL_PORT"]
DEVICE_ID             = config["DEVICE_ID"]
GPSD_HOST             = config["GPSD_HOST"]
GPSD_PORT             = config["GPSD_PORT"]
GPSD_INTERVAL         = config["GPSD_INTERVAL"]

extendedReport = True
battery = 80

def createLoginMessage(DEVICE_ID):
    strPGID = ("PGID," + DEVICE_ID)
    strPGID += (calcChecksum(strPGID))
    return strPGID

def createLocationMessage(gprmc_date,
                          gprmc_time,
                          lat,
                          lon,
                          speed,
                          bearing):

    strGPRMC = ("GPRMC,")
    strGPRMC += ("%s,A," % gprmc_time)
    strGPRMC += ("%02d%07.4f,%c," % (math.fabs(lat), (math.fabs(lat) % 1 * 60), 'S' if lat < 0 else 'N'))
    strGPRMC += ("%03d%07.4f,%c," % (math.fabs(lon), (math.fabs(lon) % 1 * 60), 'W' if lon < 0 else 'E'))

    if math.isnan(speed):
        strGPRMC += ("0.0,")
    else:
        strGPRMC += ("%03.1f," % (speed * 1.609344))

    if math.isnan(bearing):
        strGPRMC += ("0.0,")
    else:
        strGPRMC += ("%03.1f," % bearing)

    strGPRMC += ("%s,," % gprmc_date)
    strGPRMC += calcChecksum(strGPRMC)
    return strGPRMC

def createExtendedLocationMessage(utc,
                                  lat,
                                  lon,
                                  speed, 
                                  bearing,
                                  alt,
                                  battery):

    timestamp = (utc[0:4] + utc[5:7] + utc[8:10] + utc[11:13] + utc[14:16] + utc[17:19] + "." + utc[20:23])

    strTRCCR = ("TRCCR,")
    strTRCCR += ("%s,A," % timestamp)
    strTRCCR += ("%.6f," % lat)
    strTRCCR += ("%.6f," % lon)

    if math.isnan(speed):
        strTRCCR += ("0.00,")
    else:
        strTRCCR += ("%03.2f," % (speed * 1.609344))

    if math.isnan(bearing):
        strTRCCR += ("0.00,")
    else:
        strTRCCR += ("%03.2f," % bearing)

    strTRCCR += ("%s," % alt)
    strTRCCR += ("%s," % battery)
    strTRCCR += calcChecksum(strTRCCR)
    return strTRCCR

def calcChecksum(sentence):
    calc_cksum = reduce(operator.xor, (ord(s) for s in sentence), 0)
    return ("*%02X" % calc_cksum)

def dataSend(DATA):
    data = ("$" + DATA + "\r\n")
    data_to_bytes = str.encode(data)
    c.sendall (data_to_bytes)
    return True

def dataRecv():
    data = c.recv(1024)
    return data

def checkConnection(server, port):
    url = ("http://" + server + ":" + str(port))
    http = urllib3.PoolManager(num_pools=1)

    try:
        response = http.request ('GET', url)
        if response.status == 200:
            return True
        else:
            return False

    except urllib3.exceptions.HTTPError as e:
        return False

    except urllib3.exceptions.URLError as e:
        return False

if __name__ == "__main__":

    try:
        print ("Starting Traccar Client...")
        print ("Waiting GPS and Internet connection (60s)...")

        time.sleep (10)

        # TODO - Add Error handler
        gpsd = gps(host=GPSD_HOST, port=GPSD_PORT, mode=WATCH_ENABLE)
        print ("Connected to gpsd server on " + GPSD_HOST + ":" + str(GPSD_PORT))

        while not checkConnection(TRACCAR_SERVER, TRACCAR_PORT):
            print ("Waiting Internet connection...")
            time.sleep (30)

        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # TODO - Add Error handler
        c.connect((TRACCAR_SERVER, TRACCAR_PROTOCOL_PORT))
        print ('Connected to traccar server on ' + TRACCAR_SERVER + ':' + str(TRACCAR_PROTOCOL_PORT))
        dataSend(createLoginMessage(DEVICE_ID))

        while gpsd.utc == None and gpsd.utc == '':
            gpsd.next()

        print ("Starting tracker...")

        while True:

            if gpsd.utc != None and gpsd.utc != '':
                gprmc_date = gpsd.utc[8:10] + gpsd.utc[5:7] + gpsd.utc[2:4]
                gprmc_time = gpsd.utc[11:13] + gpsd.utc[14:16] + gpsd.utc[17:19]

                if checkConnection(TRACCAR_SERVER, TRACCAR_PORT):

                    if extendedReport == True:
                        print ("Sending extended...")
                        dataSend(createExtendedLocationMessage(gpsd.utc, float(gpsd.fix.latitude), float(gpsd.fix.longitude), float(gpsd.fix.speed), float(gpsd.fix.track), float(gpsd.fix.altitude), int(battery)))
                    else:
                        print ("Sending...")
                        dataSend(createLocationMessage(gprmc_date, gprmc_time, float(gpsd.fix.latitude), float(gpsd.fix.longitude), float(gpsd.fix.speed), float(gpsd.fix.track)))

            else:
                print ("No GPS Fix")

            counter = GPSD_INTERVAL

            while (counter > 0):
                counter -= 1 
                gpsd.next()
                time.sleep (1)

    except KeyboardInterrupt:
        print ("User Cancelled (Ctrl+C)")

    finally:
        gpsd.running = False
        print ("GPS - Stopped controller")
        c.close()
        print ("Stopping Tracker")
