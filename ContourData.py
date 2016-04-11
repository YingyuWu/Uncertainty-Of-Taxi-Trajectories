# Cheng Zhang (czhang0328@gmail.com)
# 03/31/2016
# used to create contour data for traffic time from a center Point

import json
from sets import Set
from shapely.geometry import LineString
from shapely.geometry import Point
import time

start_time = time.time()
roadNetGeojson = "road_distance_info/roadnetwork.geojson"
graphJson = "road_distance_info/roadGraph.json"
TEST = True

def read_roadNet():
    ''' 
        return: 
            { ID: [coordinates] }
            { 35: [ [120.114610700393,29.8610606627573], ...], ...}
    '''
    file = open(roadNetGeojson,'r')
    data = json.load(file)
    roadNet = {}
    maxRoad = 0
    for road in data['features']:
        key = int(road['properties']['partitionID'])
        if key > maxRoad: maxRoad = key 
        roadNet[key] = road['geometry']['coordinates']
    print "Read %i roads from \'%s\'" % (len(roadNet),roadNetGeojson)
    print "Max road ID: %i" % (maxRoad)
    return roadNet

def build_graph(roadNet):
    # LineString Dictionary
    l = {}
    for key,value in roadNet.iteritems():
        l[key] = LineString(value)
    # Create graph according to intersection
    g = {}
    maxRoad = len(roadNet)
    for i in range(1,maxRoad+1):
        print i
        for j in range(i+1,maxRoad+1):
            if l[i].intersects(l[j]):
                if i not in g: g[i] = [j]
                else: g[i].append(j)
                if j not in g: g[j] = [i]
                else: g[j].append(i)
    with open(graphJson,'w') as outfile:
        json.dump(g,outfile,indent=2)
        
def read_graph():
    with open(graphJson,'r') as infile:
        return json.load(infile)
                
def find_source_roads(roadNet):
    p = Point(120.14983713626863,30.275047006544927)
    c = p.buffer(0.0001).boundary
    for key,value in roadNet.iteritems():
        l = LineString(value)
        if c.intersects(l):
            print key,value
    
if __name__ == "__main__":
    roadNet = read_roadNet()
    find_source_roads(roadNet)
    print("--- %.3f seconds ---" % (time.time() - start_time))
    