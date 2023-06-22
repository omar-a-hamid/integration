""""

working version

ntes: 
multiprocessing for some reason is not working 
use threading instead

now make a way to use the other process here
maybe force input the routing or write to hostorical data
make a schadule to run the ML model
avoid it here


TODO: pass time from mqtt msg to routing 
TODO: check if time is in data A*


TODO: add collision
TODO: add tarffic predictiton model

TODO: extarct relvant traffic data, timed process? as tarffic prediction
TODO: make sure data id in the right format/type


TODO: make columns in df and remove cols from writing??

TODO: a task to act as a manger, pool or magner, that will call other tasks to handle other files
TODO: choose what threads and what process

TODO: approxmate time to time step, here or in (A*)
TODO: how and when to send routing instrusctions? maybe some sort of Queue that will be triggered when on way to this coord?? 


TODO: insert deaf nodes to collision algo (collisions), it will be in the same mqtt msg parse it there, 
        when to remove them is another question, maybe allocate them in the same branch as the active node so when it updates it
            updates too 


####################################################################

BUG: U-turn may appear as 'R' maybe followed by an 'l' (A*)


####################################################################

DONE: change processing message to dump in csv file? 
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



# multiprocessing.set_start_method(method="fork")


route=Route("map/")
# message_queue = multiprocessing.Manager().Queue()
message_queue = multiprocessing.Queue()
collision_message_queue = multiprocessing.Queue()


# multiprocessing.freeze_support()

mqtt=Mqtt_class(message_queue,TOPIC_RX)
# queue = multiprocessing.Queue()




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
        collision_message_queue.put(data)
    except json.JSONDecodeError as e:
        print("Error decoding message:", e)
    # TODO: change this to dump in csv file? 
    # print((routing_cmd in data),(data[routing_cmd]==1) )
    if ((routing_cmd in data) and (data[routing_cmd]==1)):
        route_processor(data)


process_message.df = pd.DataFrame()

def route_task(data):
    # print("routing command found")

    # if all([current_pos_lat, current_pos_lon , distination_pos_lat , distination_pos_lon]) in data:
    if all(s in data for s in (current_pos_lat,current_pos_lon , distination_pos_lat,distination_pos_lon)):
        print("start and destination found, Routing..")
        print("start: \n",data[current_pos_lat],", ",data[current_pos_lon],
                "\ndestination: \n",data[distination_pos_lat],", ",data[distination_pos_lon])
        
        route_found = route.find_route(data[current_pos_lat],data[current_pos_lon]
                                        ,data[distination_pos_lat],data[distination_pos_lon],current_time) #TODO: pass time from mqtt msg 
        
        print("\n\nfastest route: \n",route_found)
        # mqtt.mqtt_publish(str(route_found),TOPIC_TX)

def route_processor(data):
    route_procses=threading.Thread(target=route_task,args=(data,))
    # route_procses=  multiprocessing.Process(target=route_task,args=(data,))

    route_procses.daemon = True
    route_procses.start()   


def collisoins_task(queue):
    
    print("collision process started",flush=True)
    
    while True:
        data = queue.get()
        if data:
            try:
                
                data_df = pd.DataFrame(data,index = [data[time_stamp]])
                df = pd.concat([process_message.df,data_df ])


                # message_queue.put(data)  # Put the message into the queue for processing
            except json.JSONDecodeError as e:
                print("Error decoding message:", e)

            print(df.tail(1),flush=True)
            print("collision process",flush=True)
            # time.sleep(1)

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


def main():


    processes = []

    collision_process =  multiprocessing.Process(target=collisoins_task,args=(collision_message_queue,))

    collision_process.daemon = True
    collision_process.start()
    # multiprocessing.freeze_support()

    # collision_process.join()


    message_processor_process = threading.Thread(target=message_processor,args=(message_queue,))

    message_processor_process.daemon = True
    message_processor_process.start()
    # multiprocessing.freeze_support()

    
    mqtt_process =  threading.Thread(target=mqtt.mqtt_task,args=())
    mqtt_process.daemon = True
    mqtt_process.start()
    # multiprocessing.freeze_support()


    # collision_process =  threading.Thread(target=collisoins_task,args=())

    

    processes.append(mqtt_process)
    processes.append(collision_process)
    processes.append(message_processor_process)

    # for procses in processes:
        # procses.daemon = True


    
    try:
        while True:
            # print("main")
            time.sleep(1)

    except KeyboardInterrupt:

        
        # collision_process.terminate()

        # message_processor_process.join()

        # Terminate the MQTT listener processes
        for procses in processes:
            try:
                procses.terminate()
                procses.join()
                ...
            except:
                ...



if __name__ == '__main__':

    main()
