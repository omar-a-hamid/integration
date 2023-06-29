import paho.mqtt.client as paho
from paho import mqtt
from config import *

from random import randint
# from Queue import 
from queue import Queue
from time import sleep
from datetime import datetime
class Mqtt_class:


    

    def __init__(self,message_queue=None, topic=TOPIC_RX) -> None:

        self.USER_NAME= USER_NAME
        self.PASS_WORD= PASS_WORD
        self.SERVER_URL= SERVER_URL
        self.PORT= 8883
        self.TOPIC = topic

        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_connect = self.on_connect
        self.message_queue=message_queue
        self.topic=topic

        # enable TLS for secure connection
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        self.client.username_pw_set(self.USER_NAME, self.PASS_WORD)
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        self.client.connect(self.SERVER_URL, self.PORT,keepalive=6000)

        # setting callbacks, use separate functions like above for better visibility
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish


    # with this callback you can see if your publish was successful
    def on_publish(client, userdata, mid, properties=None):
        
        # print(("mid: " + str(mid)))
        print("published" ,flush=True)
        # Q.append((str("mid: " + str(mid))))
        # Q1.append(1)

        # child_conn.send("mid: " + str(mid))
        # return ("mid: " + str(mid))
        ...

    # setting callbacks for different events to see if it works, print the message etc.
    def on_connect(self,client, userdata, flags, rc, properties=None):
        
        print("CONNACK received with code %s." % rc)
        # Q.append(str("CONNACK received with code %s." % rc))
        ...

    # print which topic was subscribed to
    def on_subscribe(self,client, userdata, mid, granted_qos, properties=None):
        # print("Subscribed: " + str(mid) + " " + str(granted_qos))
        
        print("subscribtion successfull")

        ...

    # print message, useful for checking if it was successful
    def on_message(self,client, userdata, msg):
        # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload.decode("utf-8")))
        try:
            self.message_queue.put(str(msg.payload.decode("utf-8")))  # Put the message into the queue for processing
        except:
            print("error decoding to utf-8",flush=True)

    def mqtt_subscribe(self, topic):
        self.client.subscribe(topic, qos=0)

    def  listen(self):
        self.client.loop_forever()


    def mqtt_publish(self,payload="test paylaod",topic=TOPIC_TX,qos=0):
        self.client.publish(topic, payload=payload, qos=qos)

    def mqtt_start(self):

        # print('here')
        self.client.subscribe(self.topic, qos=0)
        # self.client.publish("test1", payload="test1_py", qos=0)
        self.client.loop_forever()
        # client.loop_start()
        

    def mqtt_loop(self):
        self.client.loop(0.01)

    def mqtt_task(self):
        self.mqtt_start()
        # while(True):
            # mqtt_loop()
    def test(self):


        """
                {
        "dateandtime": "2022-12-07 08:48:00",
        "id": 1,
        "r_cmd": 0,
        "clon": 31.3461741,
        "clat": 31.3461741,
        "spdK/m": 0,
        "1": 1,
        "2": 222,
        "3": 11,
        "4" :38,
        "5": 31.34617424,
        "6": 30.0461235
        }

        """

        loc = "30.071337, 31.354695"
        loc = "30.052832, 31.326813"
        
        msg =   '''{
                "dateandtime": "'''+str(datetime.utcnow()) +'''",
                "id": "A'''+str(randint(10,99))+'''" ,
                "r_cmd": 0,
                "clon": 31.3'''+str(randint(26813,54695))+''' ,
                "clat":  30.0'''+str(randint(52832,71337))+''',
                "spdK/m": '''+str(randint(0,60))+''',
                "1": 1,
                "2": 198,
                "3": 0,
                "4" :4,
                "5": 31.34990337023007,
                "6": 30.060972260514543
                }'''
        
        self.mqtt_publish(msg,self.topic)
        ...




def test():

    message_queue = Queue()
    mqtt=Mqtt_class(message_queue,TOPIC_RX)
    while True:
        sleep(0.5)
        mqtt.test()




if __name__=='__main__':


    while True:
        test()
        
        