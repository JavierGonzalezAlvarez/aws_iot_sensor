import time
import datetime
from datetime import datetime
import RPi.GPIO as GPIO
from time import sleep
import paho.mqtt.client as mqtt
import ssl
import json

Sensor: int = 7
Led: int = 16

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)    #connect to RP
GPIO.setup(Sensor, GPIO.IN) #Read output pin
GPIO.setup(Led, GPIO.OUT)   #LED output pin
GPIO.output(Led, False)  #set LED to value 0 - Turn off LED

time.sleep(1)
print("ready to get movement and send it to AWS Iot")

def on_connect(client, userdata, flags, rc):
    '''
        Subscribing in on_connect() means that if we lose the connection and
        reconnect then subscriptions will be renewed.
    '''
    print(f"Connected to AWS IoT: {client} - {userdata} - {flags} - {rc}")

def motion_detected(sensor):
    '''detection function'''
    now = datetime.now()
    date_to_string: str = now.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Movement detected on pin sensor {sensor}, Led is on - {now}")
    #topic name: rpzero3-sensor-topic
    client.publish("rpzero3-sensor-topic", payload=json.dumps( \
        {"pin sensor": sensor, "movement": "movement on", "datetime": date_to_string}), \
        qos=0, retain=False)
    print("Data sent to AWS IOT")
    GPIO.output(Led, True)
    time.sleep(0.1)
    GPIO.output(Led,False)
 
 # constructor
client = mqtt.Client(client_id=None, clean_session=True, userdata=None, transport="tcp") 
client.on_connect = on_connect
client.tls_set( \
    ca_certs='./AmazonRootCA1.pem', \
    certfile='./device-certificate.pem.crt', \
    keyfile='./rp-private.pem.key', \
    tls_version=ssl.PROTOCOL_SSLv23)

client.tls_insecure_set(True)
#endpoint
client.connect("my_end_point.amazonaws.com", 8883, 60)

try:
    GPIO.add_event_detect(Sensor, GPIO.RISING, callback=motion_detected, bouncetime=1000)
    while True:
        client.loop_forever() #activates on_connect
except KeyboardInterrupt:
    GPIO.cleanup()
    print("bye")