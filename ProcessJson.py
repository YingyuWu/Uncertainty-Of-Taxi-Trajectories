# Cheng Zhang (czhang0328@gmail.com)
# 03/07/2016
# This file is used to combine one mouth data together for each hour

import json
from datetime import datetime
import os.path

jsonFileName = "OneMonth_201101_1hour_TestMaxSpeed.json"
TEST = False
outputDir = "./output"
minAcceptedSpeed = 1

def loadData(data, day, time):
    # loadData from one day one hour
    fileName = "%s/%s/%s.graph.tarveltime.node.csv" \
                % (outputDir,day,time)
    f = open(fileName,'r')
    count = 0
    for line in f:
        line = line.strip().split(' ')
        if line[0] not in data:
            data[line[0]] = {'distance':float(line[1]), 'speeds':[]}
        data[line[0]]['speeds'] += [float(x) for x in line[2:] if float(x) >= minAcceptedSpeed]   
        count += 1
        if count > 10 and TEST: break
    #print "Load %i Data From %s" % (count, fileName)
    
def standardDeviation(l,average = 0):
    # calculate the sample standard deviation
    if (len(l) <= 1): return 0
    if (average is 0): average = sum(l) / len(l)
    return ( sum([ (x-average)**2 for x in l ]) / (len(l) - 1) ) ** 0.5
        
def calculateInData(data):
    # According to format.txt, calculate data
    for key, node in data.items():
        if (len(node['speeds']) == 0):
            node['speed'] = 0.0
            node['maxSpeed'] = 0.0
            node['minSpeed'] = 0.0
        else:
            node['speed'] = sum(node['speeds']) / len(node['speeds']) 
            node['maxSpeed'] = max(node['speeds']) 
            node['minSpeed'] = min(node['speeds'])
        node['flow'] = len(node['speeds'])
        node['travelTime'] = (node['distance'] / node['speed']) if node['speed'] > 0.01 else 0
        node['SD'] = standardDeviation(node['speeds'], node['speed'])
        node['RSD'] = node['SD'] / node['speed']
        del node['speeds']
        
def rescaleRSD(data, lowerBound = 1.0, upperBound = 10.0):
    # rescale RSD in data between lowBound and upperBound
    maxSD = 0
    minSD = 100000
    for key, node in data.items():
        if node['SD'] > maxSD: maxSD = node['SD']
        if node['SD'] < minSD: minSD = node['SD']
    
    if (maxSD - minSD) < 0.1:
        a = 0.0
        b = lowerBound
    else:
        a = float(upperBound - lowerBound) / (maxSD - minSD)
        b = float(maxSD * lowerBound - minSD * upperBound) / (maxSD - minSD)
    for key, node in data.items():
        node['RSDwidth'] = a * node['SD'] + b
        
def getGlobelMSpeeds(data):
    maxSpeed = 0
    minSpeed = 10000
    for key, node in data.items():
        if node['maxSpeed'] > 200: 
            print "Abnormal Maxspeed!"
            print key, node
        if node['maxSpeed'] > maxSpeed: maxSpeed = node['maxSpeed']
        if node['minSpeed'] < minSpeed: minSpeed = node['minSpeed']
    return maxSpeed, minSpeed

def main():
    if (os.path.isfile(jsonFileName)):
        print jsonFileName, "exists. Quit for avoiding mistake"
        return
    start_time = datetime.now()
    jsonData = []
    for hour in range(0,24):
        nodesData = {}   # Nodes data in each hour through the whole month
        print "Doing day ",
        for day in range(1,32):
            print day,
            time = "2011-12-%02iT%02i-00-00" % (day, hour)
            loadData(nodesData,day,time)
        calculateInData(nodesData)
        rescaleSD(nodesData)
        maxSpeed, minSpeed = getGlobelMSpeeds(nodesData)
        jsonData.append({'time': "2011-01T%02i-00-00" % hour, 
                         'nodes': nodesData,
                         'maxSpeed': maxSpeed,
                         'minSpeed': minSpeed})
        print("\nFinish hour[%i] on %f s,   %i nodes" % \
              (hour, (datetime.now() - start_time).total_seconds(), len(nodesData)) )
        
    jsonFile = open(jsonFileName, 'w')
    jsonFile.write(json.dumps(jsonData, indent=4, sort_keys=False))
    
    
if __name__ == "__main__":
    main()