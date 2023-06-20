""""

working version

ntes: 
multiprocessing for some reason is not working 
use threading instead

now make a way to use the other process here
maybe force input the routing or write to hostorical data
make a schadule to run the ML model
avoid it here


TODO: add the collision and the tarffic predictiton model
TODO: change processing message to dump in csv file? 


TODO: a task to act as a manger, maybe pool, that will call other tasks to handle other files

"""


import time



import time
import multiprocessing
import  json

import threading
import re


from A_star_distance import Route
from MQTT import Mqtt_class

from config import *

message_queue = multiprocessing.Queue()


mqtt=Mqtt_class(message_queue)
route=Route("map/")

###############################################



###############################################




def process_message(message):
    # Process the received message
    # print("Processing message:", message)
    # print(str(message))
    try:
        data = json.loads(str(message))
        # print(data)

        # message_queue.put(data)  # Put the message into the queue for processing
    except json.JSONDecodeError as e:
        print("Error decoding message:", e)
    # TODO: change this to dump in csv file? 
    if data[routing_cmd]:
        print("routing command found")
        # match_6 = re.search(pattern_6, message)
        # match_7 = re.search(pattern_7, message)
        if (current_pos_lat and current_pos_lon and distination_pos_lat and distination_pos_lon) in data:
            print("start and destination found, Routing..")
            # value_6 = str(match_6.group(1))
            # value_7 = str(match_7.group(1))
            print("start: ",data[current_pos_lat],", ",data[current_pos_lon],
                   ", destination: ",data[distination_pos_lat],", ",data[distination_pos_lon])
            route_found = route.find_route(data[current_pos_lat],data[current_pos_lon]
                                           ,data[distination_pos_lat],data[distination_pos_lon],current_time)
            print("fastest route: ",route_found)
            mqtt.mqtt_publish(str(route_found),TOPIC_TX)




def message_processor(queue_msg):
    while True:

        message = queue_msg.get()
        if message:
            
            process_message(message)


if __name__ == '__main__':

    
    message_processor_process = threading.Thread(target=message_processor,args=(message_queue,))

    message_processor_process.start()

    mqtt_listener_processes = []

    mqtt_process =  threading.Thread(target=mqtt.mqtt_task,args=())

    mqtt_process.start()

    mqtt_listener_processes.append(mqtt_process)

    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:

        message_processor_process.join()

        # Terminate the MQTT listener processes
        for procses in mqtt_listener_processes:
            # p.terminate()
            procses.join()