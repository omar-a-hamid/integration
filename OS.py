""""

working version

ntes: 
multiprocessing for some reason is not working 
use threading instead

now make a way to use the other process here
maybe force input the routing or write to hostorical data
make a schadule to run the ML model
avoid it here


#TODO: process each msg exatract street and time stamp and speed append it to a data frame, 
            save this to csv files on intervals/events right befor calling ML model 

TODO: pass time from mqtt msg to routing 
TODO: check if time is in data A*

TODO: pass routed coordinates and direction to vehicle, check loc and send when nearby



TODO: add tarffic predictiton model??

TODO: extarct relvant traffic data, timed process? as tarffic prediction
TODO: make sure data id in the right format/type when RX from mqtt 


TODO: make columns in df and remove cols from writing??


TODO: approxmate time to time step, here or in (A*)
TODO: how and when to send routing instrusctions? maybe some sort of Queue that will be triggered when on way to this coord?? 


TODO: insert deaf nodes to collision algo (collisions), it will be in the same mqtt msg parse it there, 
        when to remove them is another question, maybe allocate them in the same branch as the active node so when it updates it
            updates too 

TODO: a task to act as a manger, pool or magner, that will call other tasks to handle other files
TODO: choose what threads and what process




####################################################################

BUG: U-turn may appear as 'R' maybe followed by an 'l' (A*)


####################################################################

DONE: add collision
DONE: change processing message to dump in csv file? 
DONE: open a thread to save the df
DONE: send warning
DONE: goal node should detect closest previous node (A*)



"""
import time
import multiprocessing
import json
import threading

from A_star_distance import Route
from MQTT import Mqtt_class
from config import *
from Collision import Collision
import pandas as pd 



# multiprocessing.set_start_method(method="fork")


route=Route("map/")
# message_queue = multiprocessing.Manager().Queue()
message_queue = multiprocessing.Queue()
collision_message_queue = multiprocessing.Queue()
lock_data = multiprocessing.Lock() #a lock to mange racing condtions on csvm create another one for each file

# multiprocessing.freeze_support()

mqtt=Mqtt_class(message_queue,TOPIC_RX)
# queue = multiprocessing.Queue()




def process_message(message):
    # Process the received message
    # print("Processing message:", message)


    try:
        data = json.loads(str(message))
        data_df = pd.DataFrame(data,index = [data[TIME_STAMP]])
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
    # print((ROUTING_CMD in data),(data[ROUTING_CMD]==1) )
    if ((ROUTING_CMD in data) and (data[ROUTING_CMD]==1)):
        route_processor(data)


process_message.df = pd.DataFrame()

def route_task(data):
    # print("routing command found")

    # if all([CURRENT_POS_LAT, CURRENT_POS_LON , DISTINATION_POS_LAT , DISTINATION_POS_LON]) in data:
    if all(s in data for s in (CURRENT_POS_LAT,CURRENT_POS_LON , DISTINATION_POS_LAT,DISTINATION_POS_LON)):
        print("start and destination found, Routing..")
        print("start: \n",data[CURRENT_POS_LAT],", ",data[CURRENT_POS_LON],
                "\ndestination: \n",data[DISTINATION_POS_LAT],", ",data[DISTINATION_POS_LON])
        
        route_found = route.find_route(data[CURRENT_POS_LAT],data[CURRENT_POS_LON]
                                        ,data[DISTINATION_POS_LAT],data[DISTINATION_POS_LON],current_time) #TODO: pass time from mqtt msg 
        
        print("\n\nfastest route: \n",route_found)
        # mqtt.mqtt_publish(str(route_found),TOPIC_TX)
        mqtt_publish([ROUTE],[str(route_found)])

def route_processor(data):
    route_procses=threading.Thread(target=route_task,args=(data,))
    # route_procses=  multiprocessing.Process(target=route_task,args=(data,))

    route_procses.daemon = True
    route_procses.start()   


def collisoins_task(queue):
    collision = Collision("map/")

    # collision.mapV2N(data)
    print("collision process started",flush=True)
    
    while True:
        data = queue.get()
    
        if data: #this is  json data
            collision_v = collision.mapV2N(data)
            if len(collision_v)>1:
                for id in collision_v:
                    # mqtt_publish({COLLISION_WARNING: 1, V_ID: id})
                    mqtt_publish([COLLISION_WARNING, V_ID_TX], [1, id])

            # print(df.tail(1),flush=True)
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
    with lock_data:
        df.to_csv (r'data.csv', index = False, header=True)

    # df.to_csv (r'data.csv', index = False, header=False, mode='a')

def mqtt_publish(keys, values,topic_tx = TOPIC_TX):


    # key = "1"
    # value = "X12"
    data_dict =dict(zip(keys, values))
    json_msg = json.dumps(data_dict)

    # print(json_msg)
    mqtt.mqtt_publish(str(json_msg),topic_tx)

    ...

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
