""""

working version

ntes: 
multiprocessing for some reason is not working 
use threading instead

now make a way to use the other process here
maybe force input the routing or write to hostorical data
make a schadule to run the ML model
avoid it here


TODO: add collision
TODO: add tarffic predictiton model

TODO: change processing message to dump in csv file? 
TODO: make sure data id in the right format/type

TODO: approxmate time to time step, here or in A*

TODO: a task to act as a manger, pool or magner, that will call other tasks to handle other files
TODO: make columns in df and remove cols from writing??

TODO: extarct relvant traffic data, timed process? as tarffic prediction
TODO: insert deaf nodes to collision algo (collisions)
TODO: how and when to send routing instrusctions? maybe some sort of Queue that will be triggered when on way to this coord?? 

TODO: choose what threads and what process


DONE: open a thread to save the df
DONE: goal node should detect closest previous node (A*)



"""
import time
import multiprocessing
import  json
import threading

from A_star_distance import Route
from MQTT import Mqtt_class
from config import *

import pandas as pd 




message_queue = multiprocessing.Queue()
mqtt=Mqtt_class(message_queue,TOPIC_RX)
route=Route("map/")



def process_message(message):
    # Process the received message
    # print("Processing message:", message)


    try:
        data = json.loads(str(message))
        data_df = pd.DataFrame(data,index = [data[time_stamp]])
        process_message.df = pd.concat([process_message.df,data_df ])
        # print(process_message.df) 

        write_csv_procses=threading.Thread(target=write_csv,args=(process_message.df,))
        write_csv_procses.daemon = True
        
        write_csv_procses.start()        


        # print(data)
        # print(df) 

        # message_queue.put(data)  # Put the message into the queue for processing
    except json.JSONDecodeError as e:
        print("Error decoding message:", e)
    # TODO: change this to dump in csv file? 
    print((routing_cmd in data),(data[routing_cmd]==1) )
    if ((routing_cmd in data) and (data[routing_cmd]==1)):
        route_processor(data)


process_message.df = pd.DataFrame()

def route_task(data):
    print("routing command found")

    # if all([current_pos_lat, current_pos_lon , distination_pos_lat , distination_pos_lon]) in data:
    if all(s in data for s in (current_pos_lat,current_pos_lon , distination_pos_lat,distination_pos_lon)):
        print("start and destination found, Routing..")
        print("start: \n",data[current_pos_lat],", ",data[current_pos_lon],
                "\ndestination: \n",data[distination_pos_lat],", ",data[distination_pos_lon])
        
        route_found = route.find_route(data[current_pos_lat],data[current_pos_lon]
                                        ,data[distination_pos_lat],data[distination_pos_lon],current_time)
        
        print("\n\nfastest route: \n",route_found)
        mqtt.mqtt_publish(str(route_found),TOPIC_TX)

def route_processor(data):
    route_procses=threading.Thread(target=route_task,args=(data,))
    # route_procses=  multiprocessing.Process(target=route_task,args=(data,))

    route_procses.daemon = True
    route_procses.start()   


def collisoins_task():
    while True:

        # print(process_message.df.tail(1))
        time.sleep(1)
        ...
    ...

def message_processor(queue_msg):

    while True:
        message = queue_msg.get()
        if message:            
            process_message(message)


def write_csv(df=None):

    df.to_csv (r'data.csv', index = False, header=True)

    # df.to_csv (r'data.csv', index = False, header=False, mode='a')



if __name__ == '__main__':

    processes = []

    message_processor_process = threading.Thread(target=message_processor,args=(message_queue,))
    message_processor_process.daemon = True
    message_processor_process.start()
    
    mqtt_process =  threading.Thread(target=mqtt.mqtt_task,args=())
    mqtt_process.daemon = True
    mqtt_process.start()

    collision_process =  threading.Thread(target=collisoins_task,args=())
    # collision_process =  multiprocessing.Process(target=collisoins_task,args=())

    collision_process.daemon = True
    collision_process.start()

    

    processes.append(mqtt_process)
    # processes.append(collision_process)
    processes.append(message_processor_process)

    # for procses in processes:
        # procses.daemon = True


    
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        
        # collision_process.terminate()

        # message_processor_process.join()

        # Terminate the MQTT listener processes
        for procses in processes:
            ...
            # p.terminate()
            # procses.join()
        