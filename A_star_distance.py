import traci
import sumolib

import pandas as pd
import math
#TODO: bug some time it fetches the speed zero
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


class Route:

    
    def __init__(self,path):

        self.ds = pd.read_csv(path+'traffic.csv')
        self.df = pd.pivot_table(self.ds,index = 'dateandtime')
        self.net = sumolib.net.readNet('osm.net.xml')
        traci.start(["sumo", "-c", path+"osm.sumocfg"])

        

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
        
    def heuristic(self,node):
        # print("Node: ",node)
        # print("**************************")
        # print("**************************")
        # print("**************************")

        node_x, node_y = self.net.getNode(node).getCoord()
        goal_x, goal_y = self.net.getNode(self.goal_node).getCoord()
        # print("H: ",(((node_x - goal_x)**2 + (node_y - goal_y)**2)**0.5)/60)
        return (((node_x - goal_x)**2 + (node_y - goal_y)**2)**0.5)/45
        # return (((node_x - goal_x)**2 + (node_y - goal_y)**2)**0.5)

    def a_star(self,start_node, goal_node,time):
        self.goal_node = goal_node
        open_set = [start_node]
        came_from = {}
        g_score = {start_node: 0}
        f_score = {start_node: self.heuristic(start_node)}
        visited = set()  # Keep track of visited nodes
        
        while open_set:
            current_node = min(open_set, key=lambda node: f_score[node])
            if current_node == goal_node:
                path = [current_node]
                while current_node in came_from:
                    current_node = came_from[current_node]
                    path.append(current_node)
                path.reverse()
                return path
                
            open_set.remove(current_node)
            visited.add(current_node)
            
            for neighbor_str in self.net.getNode(current_node).getOutgoing():
                neighbor = neighbor_str.getID()
                neighbor_node = self.net.getEdge(neighbor).getToNode()
                

                tentative_g_score = g_score[current_node] + self.get_time(neighbor, time)
                # print('edge: ',neighbor)
                # print("g: ",self.get_time(neighbor,time) )
                
                if neighbor_node not in visited or tentative_g_score < g_score[neighbor_node]:
                    neighbor_node_id = neighbor_node.getID()
                    if neighbor_node_id not in visited:
                        came_from[neighbor_node_id] = current_node
                        g_score[neighbor_node_id] = tentative_g_score
                        f_score[neighbor_node_id] = tentative_g_score + self.heuristic(neighbor_node_id)
                        open_set.append(neighbor_node_id)
                        visited.add(neighbor_node_id)
                        
        return None
        # find the shortest path using A* algorithm
    def get_closest_node(self,lon, lat):
        
        
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
        
        closest_node = self.net.getEdge(closestEdge.getID()).getToNode()


        return closest_node

    def find_route(self,start_node,goal_node,time):
        shortest_path = self.a_star(start_node, goal_node,time)
        # print("Shortest path:", shortest_path)
        return shortest_path

        # stop the simulation
        # traci.close()

    
    def __del__(self):
        traci.close()






# time = '2022-12-07 08:48:00'

# start the simulation and connect to it

# define the start and goal nodes
# start_node = '287524294'
# goal_node = "6570524692"
# ds = pd.read_csv('traffic.csv')

# route=Route("traffic.csv")

# route.find_route(start_node,goal_node,time)
