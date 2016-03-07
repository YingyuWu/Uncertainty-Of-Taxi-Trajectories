# TaxiVis product for analyzing trends in taxi trajectories.
# Copyright (C) 2012  David Sheets (dsheets4@kent.edu)
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -----------------------------------------------------------------------------
import time
import calendar
import tempfile
import os
import shutil
import codecs
import sys
import Utils
# import PageRank
import math
import datetime
import json

TEST = False

for frafra in range(3, 32):
    start_time = datetime.datetime.now()
    # Process the command line inputs
    roadFile = codecs.open("./road_distance_info/road_info", 'r', encoding="utf_8")

    distanceThreshold = 900  # * math.sqrt(tx * tx + ty * ty) * 1e4;
    timeThreshold = 90;  # second
    numberOfThreshold = 0;
    numberOfTimeThreshold = 0;

    road = {}
    for line in roadFile:
        line = line.strip()
        item = line.split(' ')
        road[item[0]] = [item[1], item[2], item[3]];

    roadFile.close()

    inputFile = "./data/Data2-" + str(frafra) + ".txt"
    duration = "3600"  # 7200 = 2 hours. 86400 = 24 hours;
    outputDir = "./output/" + str(frafra) + "/"
    bFilterRepeats = True
    bAugmentSpeed = False

    inFile = codecs.open(inputFile, 'r', encoding="utf_8")

    timeIncrement = int(duration)
    sOutDir = "%s" % (outputDir)
    print("Processing file with time duration of %s seconds" % (timeIncrement))
    print("Output directory is: %s" % (sOutDir))
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    nProgressInc = 50000  # number of records to process before print an indication
    nRecProcessed = 0  # Total number of records in the input file
    nRecKept = 0  # Total number of records used in the output
    data = {}  # Dictionary mapping time segment to taxi
    # Temp directory for intermediate files.
    sTmpDir = tempfile.mkdtemp(".taxivis")
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Read the input file line by line and write out temporary files for furhter
    # processing.
    for line in inFile:
        # Track the number of records that were processed from the file
        nRecProcessed += 1
        # Strip the whitespace from either side of the line
        line = line.strip()
        # Split the input CSV into individual fields
        csv = line.split(',')
        # Run the pre-process, which returns whether to process the record
        if not Utils.PreProcessData(csv):
            continue
        # Track the number of records that were kept
        nRecKept += 1
        # Determine if the output file has been created yet and, if not, create it.
        # One file is created to store all the valid points for a given time
        # duration
        timeStart = int(csv[Utils.iTime] / timeIncrement)
        if not timeStart in data:
            sTime = time.strftime(Utils.sTimeFormatOut, time.gmtime(timeStart * timeIncrement))
            data[timeStart] = open("%s/%s" % (sTmpDir, sTime), 'w')
            print("Starting new time slot: %s" % sTime)
        # If the option to only process points for a loaded taxi is set or if
        # the point corresponds to a loaded value then output the value to
        # the output file.
        # Append the new point to the end of the taxis list
        try:
            data[timeStart].write("%s,%s,%s,%s,%s\n" % \
                 (csv[Utils.iPlate], csv[Utils.iTime], csv[Utils.iRId], csv[Utils.iLoad], csv[Utils.iSpd]))
        except UnicodeEncodeError:
            print "----- UnicodeEncodeError Happend ---"
            data[timeStart].write("%s,%s,%s,%s,%s\n" % \
                 (csv[Utils.iPlate].encode("utf-8"), csv[Utils.iTime], 
                  csv[Utils.iRId].encode("utf-8"), 
                  csv[Utils.iLoad].encode("utf-8"), 
                  csv[Utils.iSpd].encode("utf-8")))
            
        # DEBUG: Process a subset of the total over all points.  Just makes
        #         it faster to test during development.
        if TEST and nRecProcessed > 500000:
            break

    # Close all the individual output files
    for tmpFile in data.values():
        tmpFile.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Print some status
    print("Records processed : %d" % (nRecProcessed))
    print("Records kept      : %d" % (nRecKept))
    print("Finished reading input file.  Processing output")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Sort the cached data.  At this point the data has been grouped into its
    # proper time category and now needs to be sorted by the plate ID.  The
    # sorted data is also output in the format for the TMT utility.
    sTmpFiles = os.listdir(sTmpDir)
    sTmpFiles.sort()
    
    for sTmpFile in sTmpFiles:
        # Create a new dictionary for this time segment.
        data = {}

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Open up the input file from the temporary location.
        inFile = open("%s/%s" % (sTmpDir, sTmpFile), 'r')

        # Parse out the input file
        for line in inFile:
            # Strip the whitespace from either side of the line
            line = line.strip()
            # Split the input CSV into individual fields
            csv = line.split(',')
            # If this is the first time the taxi has been seen, create a list for it
            if not csv[0] in data:
                data[csv[0]] = []
            # Add the point onto the end of the taxi's list
            data[csv[0]].append(csv)

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Open up the output file for this time slot.
        nSpdBucketRange = 30
        if not os.path.isdir(sOutDir):
            os.makedirs(sOutDir)

        outFile_node = open("%s/%s.graph.tarveltime.node.csv" % (sOutDir, sTmpFile), 'w')

        my_edges = {}
        my_node = {}

        # Within each time segment is a dictionary of the taxi's trajectory
        # keyed by the taxi's plate.
        nTaxiProcessed = 0
        nRecProcessed = 0
        
        for taxiKey, taxiVal in data.items():
            taxiVal = sorted(taxiVal, key=lambda item: item[1], reverse=False)
              
            tempTrajectory = []
            tempSpeed = []
            # Track the total number of taxis in this time period.
            nTaxiProcessed += 1

            # Iterate over all the taxis and write a list of the taxi's points to
            # the output file.
            lastRoadId = None
            for point in taxiVal:
                # Determine if the duplicate should be filtered.
                if (not bFilterRepeats) or (not (point[2] == lastRoadId)):
                    # delete the road of which distance is 0;
                    if point[2] not in road:
                        continue;
                    if float(road[point[2]][0]) == 0.0:
                        continue;
                    # if not bool(point[3]): # Filter the taix without customer.
                    #    continue;
                    lastRoadId = point[2]
                    # If weighting is to occur for faster points, then add the
                    # additional
                    # points to the output file.
                    nSpd = 0
                    try:
                        nSpd = int(point[4])
                    except ValueError:
                        nSpd = 0
                    
                    if bAugmentSpeed and nSpd > nSpdBucketRange:
                        nInsertions = int(nSpd / nSpdBucketRange) - 1
                        for i in range(nInsertions):
                            outFile.write("%s " % (point[2]))
                            # print( "Zoom-Zoom(%d)!  %d" % (i,nSpd) )
                    tempTrajectory.append(point)
                    tempSpeed.append(nSpd)
                    # Track how many records are processed in total
                    nRecProcessed += 1
            
            # TODO : Sum edges flow.
            if len(tempTrajectory) > 1:
                for i, item in enumerate(tempTrajectory[0:-1]):
                    sourceID = item[2]
                    targetID = tempTrajectory[i + 1][2]
                    
                    if (Utils.distance([[float(road[sourceID][1]), float(road[sourceID][1])], [float(road[targetID][1]), float(road[targetID][1])]]) > distanceThreshold):
                        numberOfThreshold += 1;
                        continue;
                    if int(tempTrajectory[i + 1][1]) - int(item[1]) > timeThreshold:
                        numberOfTimeThreshold += 1;
                        continue;
                    tempkey = str(sourceID) + "#" + str(targetID)
                    if tempkey not in my_edges:
                        my_edges[tempkey] = 1
                    else:
                        my_edges[tempkey] += 1
            else:
                pass

            # TODO : Sum node total speed;
            for i, item in enumerate(tempTrajectory):
                if item[2] not in my_node:
                    my_node[item[2]] = [float(item[4])]
                else:
                    my_node[item[2]].append(float(item[4]))

            # END of the content of one taxi trajactory
            pass

        # calculate average travel time of each node.
        for key, value in my_node.items():
            if key not in road:
                road[key] = [0.0, 0.0, 0.0]
                print(key + "is not in road")
            # CSV format: RoadKey RoadLen Speed1 Speed2 Speed3 ...
            outFile_node.write("%s %f " % (key, float(road[key][0]) ) )
            for eachSpeed in value:
                outFile_node.write("%f " % (eachSpeed))
            outFile_node.write("\n")
            
        outFile_node.close()

        # Print some statistics on the processed data
        print("Time slot: %s" % (sTmpFile))
        print " %s edges filtered by distance threshold." % (numberOfThreshold) ,
        print " %s edges filtered by time threshold." % (numberOfTimeThreshold)
        print "   Total taxis  : %d" % (nTaxiProcessed),
        print "   Total points : %d" % (nRecProcessed)

    end_time = datetime.datetime.now();
    print("DONE by %f s" % ((end_time - start_time).total_seconds()));
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Clean up the temp directory
    # print( "Temp directory at %s" % (sTmpDir) )
    shutil.rmtree(sTmpDir, True)

