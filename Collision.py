# import traci
import sumolib

import pandas as pd
import math
from config import *
import json
#TODO: bug some time it fetches the speed zero
#TODO: time incrmenting
"""
TODO: 

import traffic data, csv? 

csv --> 
    
                edge        E0        E2      E3        E4      E5      E6      E6      ...
     
        time     

        12:00             60KM/Hr  60KM/Hr  60KM/Hr  60KM/Hr  60KM/Hr 
        12:01             60KM/Hr  60KM/Hr  60KM/Hr  60KM/Hr  60KM/Hr
        12:02             60KM/Hr  60KM/Hr  60KM/Hr  60KM/Hr  60KM/Hr
          .
          .
          .



"""




class Collision:

    # nodes_df = pd.dataframe(
    #     [],index=self.net.getNodes()
    # )

    def __init__(self,path):

        # self.ds = pd.read_csv(path+'traffic.csv')
        # self.df = pd.pivot_table(self.ds,index = 'dateandtime')
        self.net = sumolib.net.readNet(path+'osm.net.xml')
        nodes_obj = self.net.getNodes()
        self.nodes_id = [x.getID() for x in nodes_obj]
        # nodes_id = [x for x in nodes_obj]
        # print(self.nodes_id)

        self.nodes_df = pd.DataFrame(
        [],index=self.nodes_id
        )
        # print(self.nodes_df)
        

    

    def get_traffic(self,edge,time): 

        try: 
            return self.df.loc[str(time), str(edge)]
        except:
            return 60

    def get_time(self,edge,time):
        try:
            return self.net.getEdge(edge).getLength() / self.get_traffic( edge,time)
        except:
            return self.net.getEdge(edge).getLength() / 50

    def get_closest_node(self,lon, lat, from_node=0):
        
        
        # lon,lat =  31.347218, 30.058983
        # 7154.87,8425.21
        # 30.058983, 31.347218
        # net = sumolib.net.readNet('myNet.net.xml')
        radius = 0.1

        x, y = self.net.convertLonLat2XY(lon, lat)
        # x,y = 7154.87,8425.21
        while(True):
            edges = self.net.getNeighboringEdges(x, y, radius)
            
        # pick the closest edge
            if len(edges) > 0:

                distancesAndEdges = min(edges, key=lambda x: x[1])

                closestEdge,dist = distancesAndEdges
                # print(closestEdge)
                break
            radius *= 10
        if not from_node:
            closest_node = self.net.getEdge(closestEdge.getID()).getToNode()
        else: 
            closest_node = self.net.getEdge(closestEdge.getID()).getFromNode()

        return closest_node
    def get_eta(self,node,lon,lat):
        # print(node.getCoord())
        node_x, node_y = node.getCoord()
        # node_x, node_y = self.net.getNode(node).getCoord()


        node_lon,node_lat =  self.net.convertXY2LonLat(node_x,node_y)
        

        return (((node_lon - lon)**2 + (node_lat - lat)**2)**0.5)/45 #TODO: speed?
    #TODO: check if distance in km

    
    def mapV2N(self,data):

        """
            V ID    a1   a2   a3   ... a97  a98  a99
        Nodes
           n1        a1
           n2        0   p2
           n3        0   a2
           n4        0        a3
           .
           .
           .
           n97
           n98
           n99
        
        
        
        
        
        
        """
        v_ID = data[V_ID]
        node = self.get_closest_node(data[CURRENT_POS_LON],data[CURRENT_POS_LAT])
        eta = self.get_eta(node,data[CURRENT_POS_LON],data[CURRENT_POS_LAT])
        node_id = node.getID()
        # print(v_)
        # print("node: ",node_id)
        if(eta< (10/60/60)):
            v_df = pd.DataFrame([v_ID],index = [node_id],columns=[v_ID])


            if v_ID in self.nodes_df.columns:
                self.nodes_df = self.nodes_df.drop(columns=[v_ID])
            self.nodes_df = pd.merge(self.nodes_df, v_df, how='left', left_index=True, right_index=True)
            print(self.nodes_df,flush=True)
            
            # if v_ID in self.nodes_df.columns:
            #     # self.nodes_df[v_ID] = v_df[v_ID]  # Overwrite the existing column
            #     self.nodes_df.update(v_df)  # Overwrite the specific column
            # else:
            #     self.nodes_df = pd.merge(self.nodes_df, v_df, how='right', left_index=True, right_index=True)

            # print(self.nodes_df.tail())
            # print(self.nodes_df.loc)
            # print(self.nodes_df.loc[node_id, v_ID])
            # print(self.nodes_df.loc[node_id].count())
            V_counter = self.nodes_df.loc[node_id].count()
            # print(self.nodes_df.loc[node_id])
            v_ids = self.nodes_df.loc[node_id].dropna().values
            # print("V id: ",v_ID)
            # print("V ids: ",v_ids)

            if (V_counter > 1):
                # print("warning")
                return v_ids
            return []


            # self.nodes_df

            ...
            # v = pd.DataFrame(v_ID,index = node)
                    # data_df = pd.DataFrame(data,index = [data[TIME_STAMP]])
        # process_message.df = pd.concat([process_message.df,data_df ])
        return []



        ...
        
    def get_df(self):
        return  self.nodes_df



    def __del__(self):
        ...
        # traci.close()








# start the simulation and connect to it

# define the start and goal nodes
# start_node = '287524294'
# goal_node = "6570524692"
# ds = pd.read_csv('traffic.csv')


def test():

    time = '2022-12-07 08:48:00'
    collision=Collision("map/")
    msg = """{
    "1": 1,
    "2": "A12",
    "3": 3,
    "4": 4,
    "6": 30.061577056964843, 
    "7": 31.341088547903396,
    "8": 30.060972260514543,
    "9": 31.34990337023007

    }"""
    msg2 = """{
    "1": 1,
    "2": "A22",
    "3": 3,
    "4": 4,
    "6": 30.06092705766663, 
    "7": 31.349628700908944,
    "8": 30.060972260514543,
    "9": 31.34990337023007

    }"""
    msg3 = """{
    "1": 1,
    "2": "A12",
    "3": 3,
    "4": 4,
    "6": 30.06092705766663, 
    "7": 31.349628700908944,
    "8": 30.060972260514543,
    "9": 31.34990337023007

    }"""
    msg4 = """{
    "1": 1,
    "2": "A32",
    "3": 3,
    "4": 4,
    "6": 30.061577056964843, 
    "7": 31.341088547903396,
    "8": 30.060972260514543,
    "9": 31.34990337023007

    }"""

    data = json.loads(str(msg))
    data2 = json.loads(str(msg2))
    data3 = json.loads(str(msg3))
    data4 = json.loads(str(msg4))



    res1 = collision.mapV2N(data)
    res2 = collision.mapV2N(data2)
    res3 = collision.mapV2N(data3)
    res4 = collision.mapV2N(data4)

    print(res1)
    print(res2)
    print(res3)
    print(res4)



    df = collision.get_df()
    df.to_csv (r'data.csv', index = True, header=True)


    # s_lat,s_lon = 30.065080, 31.349080
    # g_lat,g_lon = 30.062221, 31.349503

    s_lat,s_lon = 30.06288510254581 ,  31.34526851298622 
    g_lat,g_lon =  30.060972260514543 ,  31.34990337023007


    # shortest_path = route.find_route(s_lat,s_lon, g_lat,g_lon ,time)
    # print(shortest_path)

if __name__=='__main__':
    test()