HISTORICAL_DATA_FILE_PATH = "new_traffic_data.csv"
LSTM_FILE_PATH = 'LSTMS_7steps.h5'
SMOOTHING_FACTOR = 10
FREQ_GROUPER = '16T'
NEW_DATA_HISTORICAL = -100
FEATURES_COUNT = 634                    



# USER_NAME= "OmarA"
# PASS_WORD= "@A12345678"
# SERVER_URL= "efa5bbcfa6a14bce91cbbe7daf25a2b5.s2.eu.hivemq.cloud"

# PORT= 8883
# TOPIC_TX = "S2D"
# TOPIC_RX = "D2S"



# PASS_WORD= "No_123456789"
# USER_NAME= "bazenga"
# SERVER_URL=  "b3c7ef37fe6d4bdab60cc5c9d5166b9a.s1.eu.hivemq.cloud"
# TOPIC_TX = "outTopic"
# TOPIC_RX = "outTopic"
PORT= 8883




PASS_WORD= "TEST_GRAD_1p"
USER_NAME= "TEST_GRAD"
SERVER_URL=  "6acf025f42a74ff5b4b455a12145644c.s2.eu.hivemq.cloud"
TOPIC_TX = "C2V_topic"
# TOPIC_RX = "V2C_topic"

TOPIC_RX = "outTopic"
# TOPIC_TX = "outTopic"


# const char* mqtt_server = "6acf025f42a74ff5b4b455a12145644c.s2.eu.hivemq.cloud";
# const char* mqtt_username = "TEST_GRAD";
# const char* mqtt_password = "TEST_GRAD_1p";


# current_time = '2022-12-07 08:48:00'

##############################
#json keys


"""

{
"dateandtime": "2023-06-28 20:34:07.239076",
"id": "A94" ,
"r_cmd": 1,
"clon": 31.335898 ,
"clat":  30.060377,
"spdK/m": 16,
"1": 1,
"2": 198,
"3": 0,
"4" :4,
"5": 31.34990337023007,
"6": 30.060972260514543
}



"""




TIME_STAMP          = "dateandtime"

V_ID                = "id"
CURRENT_SPEED       = "spdK/m"
CURRENT_POS_LAT     = "clat"
CURRENT_POS_LON     = "clon"

ROUTING_CMD         = "r_cmd"
DISTINATION_POS_LON = "5"

DISTINATION_POS_LAT = "6"

OBSTACLE_FLAG       = "1"
OBSTACLE_SPEED      = "obstacle speed"
OBSTACLE_distance   = "2"



##############################

V_ID_TX             = "id"
COLLISION_WARNING   = "collision warning"
ROUTE               = "ROUTE"
 




"""


{
"dateandtime": "2022-12-07 08:48:00",
"2": "A12",
"3": 1,
"4": 4,
"CURRENT_POS_LAT": 30.06288510254581,
"CURRENT_POS_LON": 31.34526851298622,
"8": 30.060972260514543,
"9": 31.34990337023007,
"10": 1
}








{
"1": '2022-12-07 08:48:00'
"2": "A12",
"3": 1,
"4": 4,
"CURRENT_POS_LAT": 30.06288510254581,
"CURRENT_POS_LON": 31.34526851298622,
"8": 30.060972260514543,
"9": 31.34990337023007,
"10": 1
}
"2023-06-20 23:10:12.603995",




"""


# TIME_STAMP          = "time"

# V_ID                = "car_id"
# CURRENT_SPEED       = "4"
# CURRENT_POS_LAT     = "source_latitude"
# CURRENT_POS_LON     = "source_longitude"

# ROUTING_CMD         = "3"
# DISTINATION_POS_LAT = "8"
# DISTINATION_POS_LON = "9"

# OBSTACLE_FLAG       = ""
# OBSTACLE_SPEED      = ""
# OBSTACLE_distance      = ""

"""
{ 
"dateandtime": "25-6-2023 3:0:0",
"vehicle id": 2, 
"current lon": 31.3461227416992, 
"current lat": 30.0461227416992, 
"spdK/m": 30,
"obsflag": 0, 
"obsdistance": 80, 
"3": 58, 
"4" :25, 
"5" :0, 
"destlon": 31.3461227416992, 
"destlat": 30.0461227416992,
"routing command": 1
}

{
"1": '2022-12-07 08:48:00'
"2": "A12",
"3": 1,
"4": 4,
"CURRENT_POS_LAT": 30.06288510254581,
"CURRENT_POS_LON": 31.34526851298622,
"8": 30.060972260514543,
"9": 31.34990337023007,
"10": 1
}

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

{
"dateandtime": "2023-06-28 20:34:07.239076",
"id": "A94" ,
"r_cmd": 1,
"clon": 31.335898 ,
"clat":  30.060377,
"spdK/m": 16,
"1": 1,
"2": 198,
"3": 0,
"4" :4,
"5": 31.34990337023007,
"6": 30.060972260514543
}



"""

"""
{"time":"24/6/23 21:50:58 ","car_id":"1","source_longitude":"31.3462505340576","source_latitude":"30.06",
"speed":"30.06","front_obstacle":"30.06","front_distance":"30.06","left":"30.06","right":"30.06"}
"""

# TIME_STAMP          = "dateandtime"


# V_ID                = "2"
# CURRENT_SPEED       = "spdK/m"
# CURRENT_POS_LAT     = "current lat"
# CURRENT_POS_LON     = "current lon"

# ROUTING_CMD         = "routing command"
# DISTINATION_POS_LAT = "destinationn lat"
# DISTINATION_POS_LON = "destination lon"

# OBSTACLE_FLAG       = "obsatcle flag"
# OBSTACLE_SPEED      = "obstacle speed"
# OBSTACLE_distance   = "obstacle distance"
