# Cheng Zhang (czhang0328@gmail.com)
# 03/07/2016
# This file is used to combine one mouth data together for each hour

import json
from datetime import datetime
import os.path
from matplotlib import pyplot

jsonFileName = "./json/OneMonth_201101_1hour_PlotSD.json"
TEST = True
outputDir = "./output"
minAcceptedSpeed = 1

def dayToWeekday(day, firstWeekDay):
    # return the weekday num (Sun-0, Mon-1 ...) from the day input
    # firstWeekDay is 1st day weekday num, e.g. Jan.1st is Saturday, firstWeekDay = 6
    return (day + firstWeekDay - 1) % 7

def loadData(data, day, time):
    # loadData from one day one hour
    fileName = "%s/%s/%s.graph.tarveltime.node.csv" \
                % (outputDir,day,time)
    f = open(fileName,'r')
    count = 0
    for line in f:
        line = line.strip().split(' ')
        if line[0] not in data:
            data[line[0]] = {'distance':float(line[1]), 'speeds':[], 'speedsWeekdays':[]}
        tempSpeedsToAdd = [float(x) for x in line[2:] if float(x) >= minAcceptedSpeed]
        data[line[0]]['speeds'] += tempSpeedsToAdd
        data[line[0]]['speedsWeekdays'] += [dayToWeekday(day, 6)] * len(tempSpeedsToAdd)
        count += 1
        if count > 10 and TEST: break
    #print "Load %i Data From %s" % (count, fileName)
    
def standardDeviation(l,average = 0):
    # calculate the sample standard deviation
    if (len(l) <= 1): return 0
    if (average is 0): average = sum(l) / len(l)
    return ( sum([ (x-average)**2 for x in l ]) / (len(l) - 1) ) ** 0.5

def calculateWeekdaySpeeds(node):
    # return each weekday speeds
    speedsSum = [0] * 7
    speedsCount = [0] * 7
    for i, speed in enumerate(node['speeds']):
        speedsSum[ node['speedsWeekdays'][i] ] += speed
        speedsCount[ node['speedsWeekdays'][i] ] += 1
    node['weekdaySpeeds'] = []
    for weekday in range(0,7):
        node['weekdaySpeeds'].append(speedsSum[weekday]/speedsCount[weekday]
                                     if speedsCount[weekday] !=0 else 0)
            
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
        node['RSD'] = node['SD'] / node['speed'] if node['speed'] > 0.01 else 0
        calculateWeekdaySpeeds(node)
        del node['speeds']
        del node['speedsWeekdays']
        
def rescaleRSD(data, lowerBound = 1.0, upperBound = 10.0):
    # rescale RSD in data between lowBound and upperBound
    maxRSD = 0
    minRSD = 10000
    for key, node in data.items():
        if node['RSD'] > maxRSD: maxRSD = node['RSD']
        if node['RSD'] < minRSD: minRSD = node['RSD']
    
    if (maxRSD - minRSD) < 0.0001:
        a = 0.0
        b = lowerBound
    else:
        a = float(upperBound - lowerBound) / (maxRSD - minRSD)
        b = float(maxRSD * lowerBound - minRSD * upperBound) / (maxRSD - minRSD)
    for key, node in data.items():
        node['RSDwidth'] = a * node['RSD'] + b
        
def getGlobelMSpeeds(data):
    maxSpeed = 0
    minSpeed = 10000
    for key, node in data.items():
        if node['maxSpeed'] > maxSpeed: maxSpeed = node['maxSpeed']
        if node['minSpeed'] < minSpeed: minSpeed = node['minSpeed']
    return maxSpeed, minSpeed

def main():
    if (not TEST and os.path.isfile(jsonFileName)):
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
        rescaleRSD(nodesData)
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