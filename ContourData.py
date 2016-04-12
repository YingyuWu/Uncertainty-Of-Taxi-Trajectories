# Cheng Zhang (czhang0328@gmail.com)
# 03/31/2016
# used to create contour data for traffic time from a center Point

import json
from sets import Set
from shapely.geometry import LineString
from shapely.geometry import Point
import time
import heapq
from curses.ascii import alt
import copy

roadNetGeojson = "road_distance_info/roadnetwork.geojson"
graphJson = "road_distance_info/roadGraph.json"
speedDataDir = "./speedData"
TEST = True
minAcceptedSpeed = 10.0
maxAcceptedTime = 2


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
        roadNet[key] = {'coordinates':road['geometry']['coordinates']}
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
    
                
def find_source_roads(roadNet, radius = 100):
    rDegree = 1.0 / 111111 * radius
    print "rDegree",rDegree
    p = Point(120.14983713626863,30.275047006544927)
    c = p.buffer(rDegree).boundary
    result = []
    for key,value in roadNet.iteritems():
        l = LineString(value['coordinates'])
        if c.intersects(l):
            result.append(key)
    print "Found %i sources: " % len(result), result
    return result

def day_to_weekday(day, firstWeekDay):
    # return the weekday num (Sun-0, Mon-1 ...) from the day input
    # firstWeekDay is 1st day weekday num, e.g. Jan.1st is Saturday, firstWeekDay = 6
    return (day + firstWeekDay - 1) % 7

def load_speeds(data, day, hour):
    # loadData from one day one hour
    timestring = "2011-12-%02iT%02i-00-00" % (day, hour)
    fileName = "%s/%s/%s.graph.tarveltime.node.csv" \
                % (speedDataDir,day,timestring)
    f = open(fileName,'r')
    count = 0
    for line in f:
        line = line.strip().split(' ')
        if line[0] not in data:
            data[int(line[0])] = {'distance':float(line[1]), 'speeds':[]}
        speedsToAdd = [float(x) for x in line[2:] if float(x) >= minAcceptedSpeed]
        data[int(line[0])]['speeds'] += speedsToAdd
        count += 1
    print "Done Load day %i hour %i" % (day, hour)
    return data

def standardDeviation(l,average = 0):
    # calculate the sample standard deviation
    if (len(l) <= 1): return 0
    if (average is 0): average = sum(l) / len(l)
    return ( sum([ (x-average)**2 for x in l ]) / (len(l) - 1) ) ** 0.5

def variance(l,average = 0):
    if (len(l) <= 1): return 0
    if (average is 0): average = sum(l) / len(l)
    return sum([ (x-average)**2 for x in l ]) / (len(l) )
    
def load_time_weekday(vs,weekday,hour):
    speeds = {}
    maxT = 0.0
    minT = maxAcceptedTime
    for day in range(1,32):
        if day_to_weekday(day,6) == weekday:
            load_speeds(speeds,day,hour)
    for key,value in speeds.items():
        dis = value['distance']
        sps = value['speeds']
        if not sps: continue
        times = [dis/x for x in sps]
        maxT = max(times + [maxT])
        minT = min(times + [minT])
        vs[key]['timeAverage'] = sum(times)/len(times) if len(times) is not 0 else maxAcceptedTime
        vs[key]['timeVar'] = variance(times,vs[key]['timeAverage'])  
    for key,value in vs.items():
        if 'timeAverage' not in value:
            value['timeAverage'] = maxAcceptedTime
            value['timeVar'] = 0
    print "Weekday:%i Hour:%i maxTime:%f minTime:%f" % (weekday,hour,maxT,minT)
    
def dijkstra(graph, vs, source,result, hourlimit = 1):
    minute = 1
    timeStep = 1
    # initialize
    dist = {}
    for v in vs:
        dist[v] = float('inf')
    dist[source] = vs[source]['timeAverage']
    Q = [(vs[source]['timeAverage'], source, vs[source]['timeVar'])]
    visited = set()
    
    while Q:
        (cost,u,var) = heapq.heappop(Q)
        if cost > hourlimit: break
        while (cost>float(minute)/60): minute += timeStep
        if minute not in result: result[minute] = []
        result[minute].append(u)
        
        if u not in visited:
            visited.add(u)
            for v in graph[u]:
                if v not in visited:
                    alt = dist[u] + vs[v]['timeAverage']
                    if alt < dist[v]:
                        dist[v] = alt
                        heapq.heappush(Q, (alt,v,var + vs[v]['timeVar']))

def c_to_dict(c):
    return {'lng':c[0], 'lat':c[1]}
    
def write_gradient(vs,gradient,weekday,hour):
    outFileName = "contourData/%i-%i.json" % (weekday,hour)
    contour = {}
    for key,value in gradient.items():
        if key% 10 != 0: continue
        contour[key] = []
        for a in value:
            contour[key].append(c_to_dict(vs[a]['coordinates'][0]))
            contour[key].append(c_to_dict(vs[a]['coordinates'][-1]))
    with open(outFileName,'w') as outfile:
        json.dump(contour,outfile,indent=2,sort_keys=True)

def main():
    graph = read_graph()
    roadNet = read_roadNet()
    sources = find_source_roads(roadNet,20)
    hour = 8
    for weekday in range(0,7):
        gradient = {}
        vs = copy.deepcopy(roadNet)
        load_time_weekday(vs,weekday,hour)
        for source in sources:
            dijkstra(graph, vs, source,gradient, 1)
        write_gradient(vs,gradient,weekday,hour)    
            
    
    
    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %.3f seconds ---" % (time.time() - start_time))
    
    
    





    