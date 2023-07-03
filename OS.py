""""

working version

ntes: 
multiprocessing for some reason is not working 
use threading instead

now make a way to use the other process here
maybe force input the routing or write to hostorical data
make a schadule to run the ML model
avoid it here


             
TODO: standarize mqtt msgs between sw and hw 
TODO: request specific names in mqtt msgs for speed and time 
TODO: request specific formats in mqtt msgs for speed and time(unit) 



TODO: add tarffic predictiton model
TODO: make a csv for historical data and append to it? but how will we handel extending the model? 
TODO: you can overwrite old predictions they will never be used 



TODO: make sure data id in the right format/type when RX from mqtt (explicitly cast it)(postpone till integration)



TODO: insert deaf nodes to collision algo (collisions), it will be in the same mqtt msg parse it there, 
        when to remove them is another question, maybe allocate them in the same branch as the active node so when it updates it
            updates too 

TODO: make columns in df and remove cols from writing??
TODO: a task to act as a manger, pool or magner, that will call other tasks to handle other files
TODO: choose what threads and what process

####################################################################


TEST: pass routed coordinates and direction to vehicle, check loc and send when nearby
TEST: how and when to send routing instrusctions? maybe some sort of Queue that will be triggered when on way to this coord?? 

TEST: process each msg exatract street and time stamp and speed append it to a data frame,
         save this to csv files on intervals/events right befor calling ML model

TEST: U-turn may appear as 'R' maybe followed by an 'l' (A*)
         
####################################################################


BUG: corrupted data due to improper shifting 
BUG: lstm init 
BUG: future predictions count 
BUG: usses dataframe instead of csv file //will need further testing to see if it can be 
                                                handled using a thread



####################################################################
DONE: extarct relvant traffic data, timed process? as tarffic prediction

DONE: handle and save data for everything specially traffic

DONE: pass time from mqtt msg to routing 

DONE: remove "current_time" from config file
DONE: check if time is in data A*
DONE: approxmate time to time step, here or in (A*)
DONE: add collision
DONE: change processing message to dump in csv file? 
DONE: open a thread to save the df
DONE: send warning
DONE: goal node should detect closest previous node (A*)



"""


import time
from datetime import datetime
import multiprocessing
import json
import threading


from A_star_distance import Route
from MQTT import Mqtt_class
from config import *
from Collision import Collision
import pandas as pd 
from TrafficPrediction import *


# multiprocessing.set_start_method(method="fork")


# message_queue = multiprocessing.Manager().Queue()
message_queue = multiprocessing.Queue()
collision_message_queue = multiprocessing.Queue()
lock_data = multiprocessing.Lock() #a lock to mange racing condtions on csvm create another one for each file
taraffic_data_lock = multiprocessing.Lock()
MQTT_publish_lock = multiprocessing.Lock() #TEST

# multiprocessing.freeze_support()


route=Route("map/")

mqtt=Mqtt_class(message_queue,TOPIC_RX)
# queue = multiprocessing.Queue()

"""
{
"A12": {
"warning flag": 1
"ROUTE": "right"/left/straight
}


}

"""


def process_message(message,v_instructions=None):
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
        print("msg recived")
        collision_message_queue.put(data)
        # if ((ROUTING_CMD in data) and (data[ROUTING_CMD]==1)):
        #     route_processor(data,v_instructions)
        route_processor(data,v_instructions)

    except json.JSONDecodeError as e:
        print("Error decoding message:", e)
    # TODO: change this to dump in csv file? 
    # print((ROUTING_CMD in data),(data[ROUTING_CMD]==1) )




process_message.df = pd.DataFrame()

def route_task(data,v_instructions):
    # print("routing command found")

    # if all([CURRENT_POS_LAT, CURRENT_POS_LON , DISTINATION_POS_LAT , DISTINATION_POS_LON]) in data:
    if all(s in data for s in (CURRENT_POS_LAT,CURRENT_POS_LON , DISTINATION_POS_LAT,DISTINATION_POS_LON)):
        print("start and destination found, Routing..")
        print("start: \n",data[CURRENT_POS_LAT],", ",data[CURRENT_POS_LON],
                "\ndestination: \n",data[DISTINATION_POS_LAT],", ",data[DISTINATION_POS_LON])
        with taraffic_data_lock:
            route_found = route.find_route(data[CURRENT_POS_LAT],data[CURRENT_POS_LON]
                                        ,data[DISTINATION_POS_LAT],data[DISTINATION_POS_LON],data[TIME_STAMP]) #TODO: pass time from mqtt msg 
            route_found.append('f')
        print("\n\nfastest route: \n",route_found)

        # if data[V_ID+"_R"] not in v_instructions.keys():
        v_instructions[str(data[V_ID])+"_R"]=route_found
        # v_instructions[str(data[V_ID])+"_R"].appened('f')
        # print()
        # v_instructions.update({str(id+"_R"): 1})

            
        # v_instructions[data[V_ID]]["Route"] = str(route_found)
        # print(v_instructions,flush=True)
        # mqtt.mqtt_publish(str("Right"),TOPIC_TX)
        # mqtt.mqtt_publish(str("Right"),TOPIC_TX)

        # mqtt.mqtt_publish(str(route_found),TOPIC_TX)
        # mqtt_publish([ROUTE],[str(route_found)])
        # route_task.df.index = [data[V_ID]]
        # route_task.df.index = [data[V_ID]]

        # new_row = {'Name': 'Alex', 'Age': 28, 'City': 'Tokyo'}

        # Append the new row to the DataFrame using loc
        # df = df.append(new_row, ignore_index=True)




        # for index  in range(0,len(route_found),2):
        #     route_task.df[route_found[index]]  = route_found[index+1]
        # print( route_task.df)


route_task.df = pd.DataFrame()

def route_processor(data,v_instructions):
    if ((ROUTING_CMD in data) and (data[ROUTING_CMD]==1)):
                    
        route_procses=threading.Thread(target=route_task,args=(data,v_instructions))
        route_procses.daemon = True
        route_procses.start()   
    elif((data[V_ID]+"_R") in v_instructions and len(v_instructions[data[V_ID]+"_R"]) ): #BUG: if no routing command got first? 
        # print(v_instructions)
        if(len(v_instructions[data[V_ID]+"_R"])==1): #TEST
            print("destination reached")
            with MQTT_publish_lock:

                mqtt_publish([V_ID_TX,ROUTE ], [data[V_ID], "destination" ])
            v_instructions.update({
                    str(data[V_ID]+"_R"): "" })
            return

        next_direction_x,next_direction_y = v_instructions[data[V_ID]+"_R"][1][0],v_instructions[data[V_ID]+"_R"][1][1]
        current_x, current_y =data[CURRENT_POS_LAT] ,data[CURRENT_POS_LON]
        distance = route.get_distance(next_direction_x,next_direction_y,current_x,current_y) 
        print ("distance to next turn: ",distance)
        if(distance<75):#TODO
            with MQTT_publish_lock:

                mqtt_publish([V_ID_TX,ROUTE ], [data[V_ID], v_instructions[str(data[V_ID])+"_R"][0]])
            # v_instructions[str(data[V_ID])+"_R"].pop(0)
            if(distance<=15):
                # v_instructions.update({
                #     str(data[V_ID]+"_F"):1
                #     })
                v_instructions[str(data[V_ID])+"_F"] = 1

                # v_instructions.update({
                #     str(data[V_ID]+"_R"):v_instructions[data[V_ID]+"_R"][2:]
                #     })
            elif str(data[V_ID]+"_F") in v_instructions and v_instructions[str(data[V_ID])+"_F"] == 1: 
                v_instructions.update({
                    str(data[V_ID]+"_R"):v_instructions[data[V_ID]+"_R"][2:]
                    })
                v_instructions.update({
                    str(data[V_ID]+"_F"):0
                    })

                

            # del v_instructions[str(data[V_ID])+"_R"][0]
            # del v_instructions[str(data[V_ID])+"_R"][0]
        else:
                with MQTT_publish_lock:
                    mqtt_publish([V_ID_TX,ROUTE ], [data[V_ID],"s"])
            



        # if
        # return (((next_direction_x - data[])**2 + (next_direction_y - goal_y)**2)**0.5)<=10
        
        ...
        # v_instructions data[CURRENT_POS_LAT][CURRENT_POS_LON]
        # self.net.convertXY2LonLat(goal_x,goal_y)





def collisoins_task(queue,v_instructions):
    collision = Collision("map/")
    mqtt_publish=Mqtt_class(message_queue,TOPIC_RX)



    # collision.mapV2N(data)
    print("collision process started",flush=True)
    
    while True:
        data = queue.get()
    
        if data: #this is  json data
            # print("collision process",flush=True)

            collision_v = collision.mapV2N(data)
            # print(collision_v,flush=True)
            # if str(data[V_ID]) not in v_instructions.keys():
            #     sub_dict = {data[V_ID]: {}}
            #     v_instructions.update(sub_dict)

            #     v_instructions[data[V_ID]+"_W"]
                # v_instructions[data[V_ID]]= multiprocessing.Manager().dict()


                
            



            if len(collision_v)>1:
                for id in collision_v:
                    with MQTT_publish_lock:

                        # mqtt_publish(dict_data={COLLISION_WARNING: 1, V_ID_TX: id},channel = 2)
                        mqtt_publish.mqtt_publish(str({COLLISION_WARNING: 1, V_ID_TX: id}))
                    v_instructions[id+"_W"] = 1
                    # v_instructions.update({id:{} })

                    # mqtt_publish([V_ID_TX,COLLISION_WARNING ], [ id,1])
                    # mqtt_publish([COLLISION_WARNING, V_ID_TX], [1, id])
                    # mqtt.mqtt_publish(str("Warning"),TOPIC_TX)
                    # mqtt.mqtt_publish(str("Warning"),TOPIC_TX)


                    print("eminent collision!",flush=True)
            else: 
                v_instructions[str(data[V_ID])+"_W"] = 0
                # mqtt_publish(dict_data={COLLISION_WARNING: 1, V_ID: id})
                with MQTT_publish_lock:
                    # mqtt_publish(dict_data={V_ID_TX: data[V_ID],COLLISION_WARNING: 0},channel = 2)
                    mqtt_publish.mqtt_publish(str({V_ID_TX: data[V_ID],COLLISION_WARNING: 0}))


                # v_instructions[(data[V_ID])]["W"] = 0
                # sub_dict.update({"W": 0})
                # v_instructions[data[V_ID]].update(sub_dict)


            # print(df.tail(1),flush=True)
            # mqtt_publish(v_instructions[data[V_ID]]) #TEST
            # mqtt_publish(dict=(v_instructions[data[V_ID]]))
            # print(v_instructions)

            
            # time.sleep(1)

        ...
    ...

def message_processor(queue_msg,v_instructions=None):

    while True:
        message = queue_msg.get()
        
        if message:            
            process_message(message,v_instructions)


def write_csv(df=None):
    with lock_data:

        df.to_csv (r'data.csv', index = False, header=True)
        

    # df.to_csv (r'data.csv', index = False, header=False, mode='a')

def mqtt_publish(keys=None, values=None,dict_data = None,topic_tx = TOPIC_TX):


    # key = "1"
    # value = "X12"
    if dict_data == None:
        dict_data =dict(zip(keys, values))

    json_msg = json.dumps(dict_data)

    # print(json_msg)
        
    mqtt.mqtt_publish(str(json_msg),topic_tx)

    ...

def traffic_prediction_process():
    # @ Nourhan Shafik
    #add here things that will only happen once in the begining
    print("start model init")
    my_dataset = DataSet(file_path = HISTORICAL_DATA_FILE_PATH,box_pts = SMOOTHING_FACTOR ,freqGrouper= FREQ_GROUPER)
    lstm_object = LSTM_Model(my_dataset)
    lstm_object.load_model(path = LSTM_FILE_PATH)
    print("starting traffic process")

    while True: 
        time.sleep(1)
        if not datetime.utcnow().second: # this part activates once every hour         #TODO: seconds --> minutes 

            
            if not process_message.df.empty:
                new_data_df = process_traffic_data() #this data frame contains processed traffic data
                                                     #this may be need to be edited to match your input  
                # write_traffic_csv(new_data_df)     #save new data to new_traffic_data.csv
                            #extend model, predict traffi

                # predicted_traffic_df =  #add your function here instead of the none

                updated_data = lstm_object.class_dataset.add_new_data(new_data_df)

            
                write_traffic_csv(lstm_object.class_dataset.pd_DataFrame)     #save new data to new_traffic_data.csv

                #add part that will happen every hour
                #extend model, predict traffic

                lstm_object.fit_predict_new_data(new_data = updated_data)

                predicted_traffic_df = lstm_object.predict_df

            

                #predicted_traffic_df = None #add your function here instead of the none

            

                write_traffic_csv(df = predicted_traffic_df,name = "map/traffic.csv") #use this to save dataframe to csv 

                # write_traffic_csv(df = new_data_df,name = "traffic.csv") #use this to save dataframe to csv 


            

            #add part that will happen every hour

            #ignore the following 
            #this will need to be a process, the model will take so much power for a thread
            #call csv write in this  thread than launch the "process"

    ...

def process_traffic_data():

    traffic_df = process_message.df.copy()
    traffic_df['edge'] = traffic_df.apply(lambda row: route.get_closest_edge( row[CURRENT_POS_LON],row[CURRENT_POS_LAT]), axis=1)
    traffic_df = traffic_df[['dateandtime','edge', 'spdK/m']]
    traffic_df = pd.pivot_table(traffic_df ,index='dateandtime', values ='spdK/m' , columns ='edge')
    # temp = temp.fillna(60)
    traffic_df.index=pd.to_datetime(traffic_df.index)

    traffic_df = traffic_df.groupby([
            pd.Grouper(level=traffic_df.index.name
                       , freq = '1T'  
                      )]
          ).mean()
    return traffic_df


#dump csv traffic data: 
def write_traffic_csv(df, name = "new_traffic_data.csv"):
    #this will need to lock also the traffic data in routing algo 

    with taraffic_data_lock:
        
        df.to_csv(name,index=True,header=True)
        # route.get_closest_edge(lon=traffic_df["CURRENT_POS_LAT"])
        print("traffic process done")




        ...
    ...
def predict_tarffic(lock):
    #start process here call dirctly from file 
    #dont write in csv

    with lock:
        # ?? do i need a lock? what will I be opening? if all I need is new data, I already have the data frame I
        # will just pass it to the ml model 
        ...
    #accuire lock 
    #cache data
    #relase lock 
    #call traffic prediction and pass the dfs 
    
    ...



def main():


    processes = []


    manager = multiprocessing.Manager()

    # global v_instructions
    v_instructions = manager.dict()

    # v_instructions = {}

    collision_process =  multiprocessing.Process(target=collisoins_task,args=(collision_message_queue,v_instructions))

    collision_process.daemon = True
    collision_process.start()

    # collision_process.join()


    message_processor_process = threading.Thread(target=message_processor,args=(message_queue,v_instructions))

    message_processor_process.daemon = True
    message_processor_process.start()

    
    mqtt_process =  threading.Thread(target=mqtt.mqtt_task,args=())
    mqtt_process.daemon = True
    mqtt_process.start()

    trafic_thread = threading.Thread(target=traffic_prediction_process,args=())
    trafic_thread.daemon = True
    # trafic_thread.start()

    # trafic_process = multiprocessing.Process(target=traffic_prediction_process,args=())
    # trafic_process.daemon = True
    # trafic_process.start()


    # collision_process =  threading.Thread(target=collisoins_task,args=())

    

    processes.append(mqtt_process)
    processes.append(collision_process)
    processes.append(message_processor_process)
    processes.append(trafic_thread)

    # for procses in processes:
        # procses.daemon = True


    
    try:
        while True:
            # print("main")
            time.sleep(10)

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
