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
        graph = json.load(infile)
        for key in graph:
            graph[int(key)] = graph.pop(key)
        return graph
    
                
def find_source_roads(roadNet):
    p = Point(120.14983713626863,30.275047006544927)
    c = p.buffer(0.0001).boundary
    result = []
    for key,value in roadNet.iteritems():
        l = LineString(value)
        if c.intersects(l):
            result.append(key)
    return result

def day_to_weekday(day, firstWeekDay):
    # return the weekday num (Sun-0, Mon-1 ...) from the day input
    # firstWeekDay is 1st day weekday num, e.g. Jan.1st is Saturday, firstWeekDay = 6
    return (day + firstWeekDay - 1) % 7

def load_speed(day, time):
    # loadData from one day one hour
    result = {}
    fileName = "%s/%s/%s.graph.tarveltime.node.csv" \
                % (outputDir,day,time)
    f = open(fileName,'r')
    count = 0
    for line in f:
        line = line.strip().split(' ')
        if line[0] not in data:
            result[line[0]] = {'distance':float(line[1]), 'speeds':[], 'speedsWeekdays':[]}
        tempSpeedsToAdd = [float(x) for x in line[2:] if float(x) >= minAcceptedSpeed]
        data[line[0]]['speeds'] += tempSpeedsToAdd
        data[line[0]]['speedsWeekdays'] += [dayToWeekday(day, 6)] * len(tempSpeedsToAdd)
        count += 1
        if count > 10 and TEST: break
    #print "Load %i Data From %s" % (count, fileName)
    
    
if __name__ == "__main__":
    graph = read_graph()
    vertexes = read_roadNet()
    sources = find_source_roads(roadNet)
    print("--- %.3f seconds ---" % (time.time() - start_time))
    
    
    





    