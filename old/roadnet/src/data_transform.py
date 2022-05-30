'''
Transform .csv files to traffic simulator OpenEngine/CityFlow/SUMO data format
Author: Zherui Huang

Dependent libraries:
    pandas,
    math,
    itertools,
    numpy,
    time,
    pickle

Input: node_path, edge_path, directed, output_path
    node_path: path of node.csv
        node.csv: with columns ['node_id', 'latitude', 'longitude']
    
    edge_path: path of edge.csv
        edge.csv: with columns ['edge_id', 'from_node_id', 'to_node_id']
        
    directed:
        True or False, represents whether edges are directed(True) or not(False)
        
    output_path: path of output file
        e.g. "D:/OpenEngine/data"
            "D:/OpenEngine/data" is the context and "roadnet.txt" will generator after programme running

Output: a roadnet file(.txt/.json/.xml) with OpenEngine/CityFlow/SUMO data format
    CityFlow and SUMO data transform is coming......
'''

import pandas as pd
import numpy as np
import math
import time
import pickle
from itertools import permutations


class Data_transform:
    
    class _angle_edgeT:
    
        def __init__(self, id, angle):
            self.edge_id = id
            self.angle = angle
    
    
    def __init__(self, node_path, edge_path, directed=False):
        self._read_csv_files(node_path, edge_path)
        self.isDirected = directed
        if self.isDirected == True:
            self._directed_get_roadnet_dict()
        else:
            self._undirected_to_directed_get_roadnet_dict()
    
    
    def _read_csv_files(self, node_path, edge_path):
        self.src_node_df = pd.read_csv(node_path)
        self.src_edge_df = pd.read_csv(edge_path)
    
    
    def _undirected_to_directed_get_roadnet_dict(self):
        # get roadnet_dict from node DataFrame and edge DataFrame
        # 本方法将所有边都看作无向边，每条无向边都将分裂成两条新有向边
        
        self.roadnet_dict = {'inter':{}, 'road':{}}
        
        for i in range(len(self.src_node_df)):
            node = self.src_node_df.loc[i]
            node_id = int(node['node_id'])
            lat = node['latitude']
            lon = node['longitude']
            self.roadnet_dict['inter'][node_id] = {'lat':lat, 'lon':lon, 'sign':1,
                                                   'start_roads':[], 'end_roads':[],
                                                   'dir_of_end_roads':{}}
        
        self.angle_of_edge_dict = {}
        
        for i in range(len(self.src_edge_df)):
            # 每条有向边都看作无向边，且分裂为两条新有向边
            edge = self.src_edge_df.loc[i]
            edge_id = i # rename edge_id
            fromNode = int(edge['from_node_id'])
            toNode = int(edge['to_node_id'])
            
            from_node_lat, from_node_lon = self.roadnet_dict['inter'][fromNode]['lat'], self.roadnet_dict['inter'][fromNode]['lon']
            to_node_lat, to_node_lon = self.roadnet_dict['inter'][toNode]['lat'], self.roadnet_dict['inter'][toNode]['lon']
            
            # get edge angle
            edge_angle = self._get_angle(from_node_lat, from_node_lon, to_node_lat, to_node_lon)
            e_1 = self._angle_edgeT(2*i, edge_angle[1])
            e_2 = self._angle_edgeT(2*i + 1, edge_angle[0])
            if fromNode not in self.angle_of_edge_dict:
                self.angle_of_edge_dict[fromNode] = [ e_2 ]
            else:
                self.angle_of_edge_dict[fromNode].append(e_2)
                
            if toNode not in self.angle_of_edge_dict:
                self.angle_of_edge_dict[toNode] = [ e_1 ]
            else:
                self.angle_of_edge_dict[toNode].append(e_1)
        
        # determine directions of edges of a node
        for inter in self.angle_of_edge_dict:
            angle_edge_list = self.angle_of_edge_dict[inter]
            
            [north_road, east_road, south_road, west_road] = self._determine_dir(angle_edge_list)
                
            self.roadnet_dict['inter'][inter]['dir_of_end_roads'] = {'north':int(north_road), 'east':int(east_road), 'south':int(south_road), 'west':int(west_road)}
        
        # get road
        for i in range(len(self.src_edge_df)):
            edge = self.src_edge_df.loc[i]
            edge_id = i
            fromNode = int(edge['from_node_id'])
            toNode = int(edge['to_node_id'])
            
            if (2*i) not in self.roadnet_dict['inter'][toNode]['dir_of_end_roads'].values() or (2*i + 1)not in self.roadnet_dict['inter'][fromNode]['dir_of_end_roads'].values():
                for direction in self.roadnet_dict['inter'][toNode]['dir_of_end_roads']:
                    if self.roadnet_dict['inter'][toNode]['dir_of_end_roads'][direction] == (2*i):
                        self.roadnet_dict['inter'][toNode]['dir_of_end_roads'][direction] = -1
                        
                for direction in self.roadnet_dict['inter'][fromNode]['dir_of_end_roads']:
                    if self.roadnet_dict['inter'][fromNode]['dir_of_end_roads'][direction] == (2*i + 1):
                        self.roadnet_dict['inter'][fromNode]['dir_of_end_roads'][direction] = -1
                        
                continue
            
            self.roadnet_dict['inter'][fromNode]['start_roads'].append(2*i)
            self.roadnet_dict['inter'][toNode]['end_roads'].append(2*i)
            self.roadnet_dict['inter'][toNode]['start_roads'].append(2*i + 1)
            self.roadnet_dict['inter'][fromNode]['end_roads'].append(2*i + 1)
            
            from_node_lat, from_node_lon = self.roadnet_dict['inter'][fromNode]['lat'], self.roadnet_dict['inter'][fromNode]['lon']
            to_node_lat, to_node_lon = self.roadnet_dict['inter'][toNode]['lat'], self.roadnet_dict['inter'][toNode]['lon']
            length = self._calc_road_length(from_node_lat, from_node_lon, to_node_lat, to_node_lon)
            
            self.roadnet_dict['road'][2*i] = {'start_inter':fromNode, 'end_inter':toNode, 'roadlen':length, 'lane_num':3, 'max_speed':16.67}
            self.roadnet_dict['road'][2*i + 1] = {'start_inter':toNode, 'end_inter':fromNode, 'roadlen':length, 'lane_num':3, 'max_speed':16.67}

        # drop nodes which do not connected to any edges
        for inter in self.roadnet_dict['inter']:
            if len(self.roadnet_dict['inter'][inter]['start_roads']) == 0 and len(self.roadnet_dict['inter'][inter]['end_roads']) == 0:
                del self.roadnet_dict['inter'][inter]
    
    
    def _directed_get_roadnet_dict(self):
        # get roadnet_dict from node DataFrame and edge DataFrame
        # 本方法将所有边都看作有向边
        
        self.roadnet_dict = {'inter':{}, 'road':{}}
        
        for i in range(len(self.src_node_df)):
            node = self.src_node_df.loc[i]
            node_id = int(node['node_id'])
            lat = node['latitude']
            lon = node['longitude']
            self.roadnet_dict['inter'][node_id] = {'lat':lat, 'lon':lon, 'sign':1,
                                                   'start_roads':[], 'end_roads':[],
                                                   'dir_of_end_roads':{}, 'dir_of_start_roads':{}}
        
        # rename road such that opposite roads have adjacent IDs
        self.rename_edge_df = self.src_edge_df
        adj_dict = {}
        
        for i in range(len(self.rename_edge_df)):
            edge = self.rename_edge_df.loc[i]
            fromNode = int(edge['from_node_id'])
            toNode = int(edge['to_node_id'])
            
            if toNode in adj_dict and fromNode in adj_dict[toNode] and len(adj_dict[toNode][fromNode]) > 0:
                self.rename_edge_df.loc[i, 'edge_id'] = adj_dict[toNode][fromNode][0] + 1
                del adj_dict[toNode][fromNode][0]
                continue
            
            if fromNode not in adj_dict:
                adj_dict[fromNode] = {}
                adj_dict[fromNode][toNode] = [2 * i]
            elif toNode not in adj_dict[fromNode]:
                adj_dict[fromNode][toNode] = [2 * i]
            else:
                adj_dict[fromNode][toNode].append(2 * i)
            self.rename_edge_df.loc[i, 'edge_id'] = 2 * i
        
        # gets angles of all end roads corresponding to its intersection
        self.angle_of_end_roads_dict = {}
        self.angle_of_start_roads_dict = {}
        
        for i in range(len(self.rename_edge_df)):
            edge = self.rename_edge_df.loc[i]
            edge_id = int(edge['edge_id'])
            fromNode = int(edge['from_node_id'])
            toNode = int(edge['to_node_id'])
            
            from_node_lat, from_node_lon = self.roadnet_dict['inter'][fromNode]['lat'], self.roadnet_dict['inter'][fromNode]['lon']
            to_node_lat, to_node_lon = self.roadnet_dict['inter'][toNode]['lat'], self.roadnet_dict['inter'][toNode]['lon']
            
            # get edge angle
            edge_angle = self._get_angle(from_node_lat, from_node_lon, to_node_lat, to_node_lon)
            e_1 = self._angle_edgeT(edge_id, edge_angle[1])
            if toNode not in self.angle_of_end_roads_dict:
                self.angle_of_end_roads_dict[toNode] = [ e_1 ]
            else:
                self.angle_of_end_roads_dict[toNode].append(e_1)

            e_2 = self._angle_edgeT(edge_id, edge_angle[0])
            if fromNode not in self.angle_of_start_roads_dict:
                self.angle_of_start_roads_dict[fromNode] = [ e_2 ]
            else:
                self.angle_of_start_roads_dict[fromNode].append(e_2)
        
        # determine directions of edges of a node
        for inter in self.angle_of_end_roads_dict:
            angle_end_road_list = self.angle_of_end_roads_dict[inter]
            [north_road, east_road, south_road, west_road] = self._determine_dir(angle_end_road_list)
            self.roadnet_dict['inter'][inter]['dir_of_end_roads'] = {'north':int(north_road), 'east':int(east_road), 'south':int(south_road), 'west':int(west_road)}

        for inter in self.angle_of_start_roads_dict:
            angle_start_road_list = self.angle_of_start_roads_dict[inter]
            [north_road, east_road, south_road, west_road] = self._determine_dir(angle_start_road_list)
            self.roadnet_dict['inter'][inter]['dir_of_start_roads'] = {'north':int(north_road), 'east':int(east_road), 'south':int(south_road), 'west':int(west_road)}
            
        # get road
        for i in range(len(self.rename_edge_df)):
            edge = self.rename_edge_df.loc[i]
            edge_id = int(edge['edge_id'])
            fromNode = int(edge['from_node_id'])
            toNode = int(edge['to_node_id'])
            
            if edge_id not in self.roadnet_dict['inter'][toNode]['dir_of_end_roads'].values() or edge_id not in self.roadnet_dict['inter'][fromNode]['dir_of_start_roads'].values():
                for direction in self.roadnet_dict['inter'][toNode]['dir_of_end_roads']:
                    if self.roadnet_dict['inter'][toNode]['dir_of_end_roads'][direction] == edge_id:
                        self.roadnet_dict['inter'][toNode]['dir_of_end_roads'][direction] = -1
                        
                for direction in self.roadnet_dict['inter'][fromNode]['dir_of_start_roads']:
                    if self.roadnet_dict['inter'][fromNode]['dir_of_start_roads'][direction] == edge_id:
                        self.roadnet_dict['inter'][fromNode]['dir_of_start_roads'][direction] = -1
                        
                continue
            
            self.roadnet_dict['inter'][fromNode]['start_roads'].append(edge_id)
            self.roadnet_dict['inter'][toNode]['end_roads'].append(edge_id)
            
            from_node_lat, from_node_lon = self.roadnet_dict['inter'][fromNode]['lat'], self.roadnet_dict['inter'][fromNode]['lon']
            to_node_lat, to_node_lon = self.roadnet_dict['inter'][toNode]['lat'], self.roadnet_dict['inter'][toNode]['lon']
            length = self._calc_road_length(from_node_lat, from_node_lon, to_node_lat, to_node_lon)
            
            self.roadnet_dict['road'][edge_id] = {'start_inter':fromNode, 'end_inter':toNode, 'roadlen':length, 'lane_num':3, 'max_speed':16.67}

        # drop nodes which do not connected to any edges
        for inter in self.roadnet_dict['inter']:
            if len(self.roadnet_dict['inter'][inter]['start_roads']) == 0 and len(self.roadnet_dict['inter'][inter]['end_roads']) == 0:
                del self.roadnet_dict['inter'][inter]
                continue
            
            if len(self.roadnet_dict['inter'][inter]['dir_of_end_roads']) == 0:
                self.roadnet_dict['inter'][inter]['dir_of_end_roads'] = {'north':-1, 'east':-1, 'south':-1, 'west':-1}
            
            if len(self.roadnet_dict['inter'][inter]['dir_of_start_roads']) == 0:
                self.roadnet_dict['inter'][inter]['dir_of_start_roads'] = {'north':-1, 'east':-1, 'south':-1, 'west':-1}
    
    
    def _get_edge_num(self):
        max_edge_id = -1
        vis_edge_set = set()
        edge_num = 0
        for road_id in self.roadnet_dict['road']:
            if road_id > max_edge_id:
                max_edge_id = road_id
                
            if road_id in vis_edge_set:
                continue
            
            edge_num += 1
            vis_edge_set.add(road_id)
            vis_edge_set.add(self._get_reversed_road(road_id))
            
        return edge_num, max_edge_id
            
    
    def _get_angle(self, lat_1, lon_1, lat_2, lon_2):
        # given (lat_1, lon_1) of from_node and (lat_2, lon_2) of to_node,
        # return the angle_1(rad in [0, 2*PI)) from from_node to to_node and the angle_2 from to_node to from_node
        pi = math.pi
        if lat_1 == lat_2:
            if lon_1 < lon_2:
                return [0.5 * pi, 1.5 * pi]
            else:
                return [1.5 * pi, 0.5 * pi]
        
        if lon_1 == lon_2:
            if lat_1 < lat_2:
                return [0, pi]
            else:
                return [pi, 0]
        
        angle_1 = math.atan( (lon_1 - lon_2) / (lat_1 - lat_2) )
        if angle_1 < 0:
            angle_1 = angle_1 + pi
        if lon_2 > lon_1:
            angle_2 = angle_1 + pi
            return [angle_1, angle_2]
        else:
            angle_2 = angle_1
            angle_1 = angle_1 + pi
            return [angle_1, angle_2]
    
    
    def _get_loss(self, angle_edge, dir_index):
        dir_list = ['north', 'east', 'south', 'west']
        direction = dir_list[dir_index]
        angle = angle_edge.angle
        
        pi = math.pi
        
        if direction == 'north':
            loss = abs(angle - 0.5*pi)
            if loss > pi:
                loss = 2*pi - loss
        
        elif direction == 'east':
            loss = abs(angle - 0)
            if loss > pi:
                loss = 2*pi - loss
        
        elif direction == 'south':
            loss = abs(angle - 1.5*pi)
            if loss > pi:
                loss = 2*pi - loss
        
        elif direction == 'west':
            loss = abs(angle - pi)
            if loss > pi:
                loss = 2*pi - loss
                
        return loss


    def _get_loss_sum(self, angle_edge_list, dirIndex_tuple):
        loss_sum = 0
        for i in range(len(dirIndex_tuple)):
            loss_sum = loss_sum + self._get_loss(angle_edge_list[i], dirIndex_tuple[i])
            
        return loss_sum


    def _determine_dir(self, angle_edge_list):
        dir_list = ['north', 'east', 'south', 'west']
        edge_num = len(angle_edge_list)
        if edge_num > 4: # no more than 4 approaches
            edge_num = 4
        dir_index = [0, 1, 2, 3]
        dirIndex_list = list(permutations(dir_index, edge_num))
        
        min_loss = 4*math.pi
        min_loss_tuple = ()
        for i in range(len(dirIndex_list)):
            loss = self._get_loss_sum(angle_edge_list, dirIndex_list[i])
            if loss < min_loss:
                min_loss = loss
                min_loss_tuple = dirIndex_list[i]
                
        dir_dict = {}
        for i in range(edge_num):
            dir_dict[dir_list[min_loss_tuple[i]]] = angle_edge_list[i].edge_id
                
        dir_list = []
        
        if 'north' in dir_dict:
            dir_list.append(dir_dict['north'])
        else:
            dir_list.append(-1)
            
        if 'east' in dir_dict:
            dir_list.append(dir_dict['east'])
        else:
            dir_list.append(-1)
            
        if 'south' in dir_dict:
            dir_list.append(dir_dict['south'])
        else:
            dir_list.append(-1)
            
        if 'west' in dir_dict:
            dir_list.append(dir_dict['west'])
        else:
            dir_list.append(-1)
            
        return dir_list


    def _get_reversed_road(self, road):
        road = int(road)
        if road == -1:
            return -1
        if road % 2 == 0:
            return road + 1
        else:
            return road - 1
    
    
    def _calc_road_length(self, lat_1, lon_1, lat_2, lon_2):
        #given latitude and longitude of two nodes, return distance between them
        earth_radius = 6371393 # meter
        PI = math.pi
        meter_per_lon = 2 * PI * earth_radius / 360
        lat_rad = lat_1 * PI / 180
        meter_per_lat = meter_per_lon * math.cos(lat_rad)
        lat_dist = (lat_1 - lat_2) * meter_per_lat
        lon_dist = (lon_1 - lon_2) * meter_per_lon
        length = math.sqrt(lat_dist*lat_dist + lon_dist*lon_dist)
        return length
    
    
    def Output_roadnet_dict(self, output_path):
        # output roadnet.pkl
        with open(output_path + '/roadnet_dict.pkl', 'wb') as pkl_f:
            pickle.dump(self.roadnet_dict, pkl_f)
    
    
    def OpenEngine_data_transform(self, output_path):
        # transform data to OpenEngine format using roadnet_dict
        print('Transform data to OpenEngine format......')
        with open(output_path + '/OpenEngine_roadnet.txt', 'w') as f:
            self._OpenEngine_write_inter_data(f)
            if self.isDirected == True:
                self._directed_OpenEngine_write_road_data(f)
                self._directed_OpenEngine_write_signal_data(f)
            else:
                self._undirected_OpenEngine_write_road_data(f)
                self._undirected_OpenEngine_write_signal_data(f)
        print('Done')

    
    def _OpenEngine_write_inter_data(self, f):
        # write intersection dataset
        inter_num = len(self.roadnet_dict['inter'])
        f.write('{}\n'.format(inter_num))
        
        inter_data_form = '{latitude} {longitude} {inter_id} {signalized}\n'
        for inter_id in self.roadnet_dict['inter']:
            inter_data = self.roadnet_dict['inter'][inter_id]
            inter_data_str = inter_data_form.format(latitude = inter_data['lat'],
                                                    longitude = inter_data['lon'],
                                                    inter_id = inter_id,
                                                    signalized = inter_data['sign'])
            f.write(inter_data_str)
    
    
    def _undirected_OpenEngine_write_road_data(self, f):
        # write road dataset
        edge_num, max_edge_id = self._get_edge_num()
        f.write('{}\n'.format(edge_num))
        
        road_data_form = '{from_inter_id} {to_inter_id} {length} {speed_limit} {dir1_num_lane} {dir2_num_lane} {dir1_id} {dir2_id}\n{dir1_mov}\n{dir2_mov}\n'
        for i in range(int(max_edge_id / 2) + 1):
            
            if (2 * i) not in self.roadnet_dict['road'] or (2*i + 1) not in self.roadnet_dict['road']:
                continue
            
            road_data = self.roadnet_dict['road'][2 * i]
            reversed_road_data = self.roadnet_dict['road'][2*i + 1]
            road_data_str = road_data_form.format(from_inter_id = road_data['start_inter'],
                                                  to_inter_id = road_data['end_inter'],
                                                  length = road_data['roadlen'],
                                                  speed_limit = road_data['max_speed'],
                                                  dir1_num_lane = road_data['lane_num'],
                                                  dir2_num_lane = reversed_road_data['lane_num'],
                                                  dir1_id = 2 * i,     
                                                  dir2_id = 2*i + 1,
                                                  dir1_mov = '1 0 0 0 1 0 0 0 1',
                                                  dir2_mov = '1 0 0 0 1 0 0 0 1')
            f.write(road_data_str)
    
    
    def _directed_OpenEngine_write_road_data(self, f):
        # write road dataset
        edge_num, max_edge_id = self._get_edge_num()
        f.write('{}\n'.format(edge_num))
        
        road_data_form = '{from_inter_id} {to_inter_id} {length} {speed_limit} {dir1_num_lane} {dir2_num_lane} {dir1_id} {dir2_id}\n{dir1_mov}\n{dir2_mov}\n'
        for i in range(int(max_edge_id / 2) + 1):
            
            if (2 * i) not in self.roadnet_dict['road'] and (2*i + 1) not in self.roadnet_dict['road']:
                continue
            
            if (2 * i) in self.roadnet_dict['road']:
                road_data = self.roadnet_dict['road'][2 * i]
                road_data_str = road_data_form.format(from_inter_id = road_data['start_inter'],
                                                      to_inter_id = road_data['end_inter'],
                                                      length = road_data['roadlen'],
                                                      speed_limit = road_data['max_speed'],
                                                      dir1_num_lane = road_data['lane_num'],
                                                      dir2_num_lane = road_data['lane_num'],
                                                      dir1_id = 2 * i,
                                                      dir2_id = ((2*i + 1) if (2*i + 1) in self.roadnet_dict['road'] else -1),
                                                      dir1_mov = '1 0 0 0 1 0 0 0 1',
                                                      dir2_mov = '1 0 0 0 1 0 0 0 1')
                f.write(road_data_str)
            else:
                road_data = self.roadnet_dict['road'][2*i + 1]
                road_data_str = road_data_form.format(from_inter_id = road_data['start_inter'],
                                                      to_inter_id = road_data['end_inter'],
                                                      length = road_data['roadlen'],
                                                      speed_limit = road_data['max_speed'],
                                                      dir1_num_lane = road_data['lane_num'],
                                                      dir2_num_lane = road_data['lane_num'],
                                                      dir1_id = -1,
                                                      dir2_id = 2*i + 1,
                                                      dir1_mov = '1 0 0 0 1 0 0 0 1',
                                                      dir2_mov = '1 0 0 0 1 0 0 0 1')
                f.write(road_data_str)
                
    
    def _undirected_OpenEngine_write_signal_data(self, f):
        # write traffic signal dataset
        inter_num = len(self.roadnet_dict['inter'])
        f.write('{}\n'.format(inter_num))
        
        TS_data_form = '{inter_id} {n_road} {e_road} {s_road} {w_road}\n'
        for inter_id in self.roadnet_dict['inter']:
            dir_of_roads = self.roadnet_dict['inter'][inter_id]['dir_of_end_roads']
            north_road = self._get_reversed_road(dir_of_roads['north'])
            east_road = self._get_reversed_road(dir_of_roads['east'])
            south_road = self._get_reversed_road(dir_of_roads['south'])
            west_road = self._get_reversed_road(dir_of_roads['west'])
            TS_data_str = TS_data_form.format(inter_id = inter_id,
                                              n_road = north_road,
                                              e_road = east_road,
                                              s_road = south_road,
                                              w_road = west_road)
            f.write(TS_data_str)
    
    
    def _directed_OpenEngine_write_signal_data(self, f):
        # write traffic signal dataset
        inter_num = len(self.roadnet_dict['inter'])
        f.write('{}\n'.format(inter_num))
        
        TS_data_form = '{inter_id} {n_road} {e_road} {s_road} {w_road}\n'
        for inter_id in self.roadnet_dict['inter']:
            dir_of_roads = self.roadnet_dict['inter'][inter_id]['dir_of_start_roads']
            north_road = dir_of_roads['north']
            east_road = dir_of_roads['east']
            south_road = dir_of_roads['south']
            west_road = dir_of_roads['west']
            TS_data_str = TS_data_form.format(inter_id = inter_id,
                                              n_road = north_road,
                                              e_road = east_road,
                                              s_road = south_road,
                                              w_road = west_road)
            f.write(TS_data_str)
        
        
    def _CityFlow_data_transform(self, output_path):
        # TODO: transform data to Cityflow format using roadnet_dict
        pass
    
    
    def _SUMO_data_transform(self, output_path):
        # TODO: transform data to SUMO format using roadnet_dict
        pass
        
    
    