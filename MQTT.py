import paho.mqtt.client as paho
from paho import mqtt


class Mqtt_class:

    USER_NAME= "OmarA"
    PASS_WORD= "@A12345678"
    SERVER_URL= "efa5bbcfa6a14bce91cbbe7daf25a2b5.s2.eu.hivemq.cloud"
    PORT= 8883
    TOPIC = "test1"
    

    def __init__(self,message_queue) -> None:

        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        self.client.on_connect = self.on_connect
        self.message_queue=message_queue

        # enable TLS for secure connection
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        # set username and password
        self.client.username_pw_set(self.USER_NAME, self.PASS_WORD)
        # connect to HiveMQ Cloud on port 8883 (default for MQTT)
        self.client.connect(self.SERVER_URL, self.PORT)

        # setting callbacks, use separate functions like above for better visibility
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish


    # with this callback you can see if your publish was successful
    def on_publish(client, userdata, mid, properties=None):
        
        print(("mid: " + str(mid)))
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
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

        ...

    # print message, useful for checking if it was successful
    def on_message(self,client, userdata, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload.decode("utf-8")))
        self.message_queue.put(str(msg.payload.decode("utf-8")))  # Put the message into the queue for processing



    def  listen(self):
        self.client.loop_forever()


    def mqtt_publish(self,payload="test paylaod",topic=TOPIC,qos=0):
        self.client.publish(topic, payload=payload, qos=qos)

    def mqtt_start(self):

        # print('here')
        self.client.subscribe("test1", qos=0)
        # self.client.publish("test1", payload="test1_py", qos=0)
        self.client.loop_forever()
        # client.loop_start()
        

    def mqtt_loop(self):
        self.client.loop(0.01)

    def mqtt_task(self):
        self.mqtt_start()
        # while(True):
            # mqtt_loop()

