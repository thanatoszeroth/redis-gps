import os
import time
import json
import serial
import logging

from dotenv import load_dotenv
from pathlib import Path

from module.oop4PubRedis import oop4PubRedis

def logChannel(logName):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(asctime)s %(levelname)s] <%(process)d> [%(module)s:%(lineno)d] %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S',)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    fh = logging.FileHandler(encoding='utf-8', mode='a', filename=logName)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)


if __name__ == "__main__":
    try:
        dotenv_path = Path('.env')
        load_dotenv(dotenv_path = dotenv_path)
        logName = f"save/service_gps_{time.strftime('%Y%m%d', time.localtime())}.log"
        logChannel(logName)
    except:
        print("No ENV File.")

    logging.info(f"{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}")
    try:
        RedisIP = os.getenv("RedisIP")
        RedisPort = os.getenv("RedisPort")
        RedisPassword = os.getenv("RedisPassword")
        RedisTopic = "DataGPS"
        PR = oop4PubRedis(RedisIP, RedisPort, RedisPassword)
    except Exception as error:
        logging.error(f"{error}")

    try:
        GPSUSBPort = os.getenv("GPSUSBPort")
        gps_serial = serial.Serial(GPSUSBPort, 9600, timeout = 0.5)
    except Exception as error:
        logging.error(f"{error}")
    time.sleep(0.5)

    gps_message = {
        "lat": 0,
        "lon": 0,
        "uuid": f"{time.strftime('%Y%m%d%H%M%S', time.localtime())}",
        "time": f"{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}",
        "heartbeat": False
    }

    while True:
        uuid = f"{time.strftime('%Y%m%d%H%M%S', time.localtime())}"
        gps_message['uuid'] = uuid
        try:
            data = gps_serial.readline()
            if data.decode('utf-8')[0:6] == "$GNRMC":
                message = str(data.decode('utf-8'))
                gpsList = message.split(',')
                lat = float(gpsList[3][:2])+float(gpsList[3][2:])/60.0
                lon = float(gpsList[5][:3])+float(gpsList[5][3:])/60.0
                gps_message['lat'] = round(lat, 6)
                gps_message['lon'] = round(lon, 6)
                gps_message['heartbeat'] = True
        except Exception as error:
            logging.error(f"{error}")
            gps_message['heartbeat'] = False
        
        gps_message['time'] = f"{time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())}"
        PR.postJsonData(RedisTopic, gps_message)
        logging.info(f"{gps_message['time']} : ({gps_message['lat']}, {gps_message['lon']})")
