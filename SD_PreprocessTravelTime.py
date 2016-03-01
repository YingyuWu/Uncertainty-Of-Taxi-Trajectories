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
from optparse import OptionParser
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
# Json Filename
JsonFileName = "20111206_1hour.json"


for frafra in range(6, 7):
    start_time = datetime.datetime.now()
    # -----------------------------------------------------------------------------
    # Main() start here

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Parse out the command line options for the script.
    parser = OptionParser()
    parser.add_option("-i", "--input",
          dest="inputFile",
          help="CSV format taxi input file",
          metavar="FILE")
    parser.add_option("-o", "--out-dir",
          dest="outputDir",
          help="Output directory containing the split files",
          metavar="DIR")
    parser.add_option("-d", "--duration",
          dest="duration",
          default=3600,
          help="Duration in seconds for each division",
          metavar="float")
    parser.add_option("-l", "--loaded",
          action="store_true",
          dest="bUseLoaded",
          default=False,
          help="Retain points when the taxi has a customer.")
    parser.add_option("-u", "--unloaded",
          action="store_true",
          dest="bUseUnloaded",
          default=False,
          help="Retain points when the taxi does not have a customer.")
    parser.add_option("-s", "--speed",
          action="store_true",
          dest="bAugmentSpeed",
          default=False,
          help="If speed is greater than 30 km/hr, introduce additional weight to the points.")
    parser.add_option("-f", "--filter-repeats",
          action="store_true",
          dest="bFilterRepeats",
          default=False,
          help="If the same road id is repeated the duplicates are filtered out.")

    (options, args) = parser.parse_args()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Process the command line inputs
    roadFile = codecs.open("./road_distance_info/road_info", 'r', encoding="utf_8")

    '''latitudeRange = [22.460384, 22.837626]
    longitudeRange = [113.769300, 114.578400]

    tx = latitudeRange[1] - latitudeRange[0]
    ty = longitudeRange[1] - longitudeRange[0]'''

    distanceThreshold = 900  # * math.sqrt(tx * tx + ty * ty) * 1e4;
    timeThreshold = 90;  # second
    numberOfThreshold = 0;
    numberOfTimeThreshold = 0;








    road = {}

    for line in roadFile:
        line = line.strip()
        item = line.split(' ')
        # the following condition added by farah
        '''if item[0] not in selectedroads:
            continue'''
        road[item[0]] = [item[1], item[2], item[3]];

    roadFile.close()


    # Verify the options are valid.
    # options.inputFile = "./smallInput"
    # options.inputFile = "c:/2012-06-27.good"
    # options.inputFile = "C://HangZhou_Work/Hnewformat/Data2-"+str()+".txt"

    options.inputFile = "./data/Data2-" + str(frafra) + ".txt"
    options.duration = "3600"  # 7200 = 2 hours. 86400 = 24 hours;
    # options.outputDir = "./rawGraph_24hours_90second _one_month/"+str(frafra)+"/"
    options.outputDir = "./outputTry/" + str(frafra) + "/"
    options.bFilterRepeats = True
    options.bAugmentSpeed = False

    inFile = codecs.open(options.inputFile, 'r', encoding="utf_8")

    timeIncrement = int(options.duration)
    sOutDir = "%s" % (options.outputDir)
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
       data[timeStart].write("%s,%s,%s,%s,%s\n" % \
             (csv[Utils.iPlate], csv[Utils.iTime], csv[Utils.iRId], csv[Utils.iLoad], csv[Utils.iSpd]))

       # DEBUG: Process a subset of the total over all points.  Just makes
       #        it faster to test during development.
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
    
    jsonFile = open(JsonFileName,'w')
    jsonData = []
    
    for sTmpFile in sTmpFiles:
       jsonData.append({"time": sTmpFile, "nodes":{} })
       # Create a new dictionary for this time segment.
       data = {}

       # Sort the data so that the taxis are sorted by plate.
       # Update: This isn't required.
       # timeVal = sorted( timeVal, key=lambda record: record[Utils.iPlate] )

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
       outFile_edge = open("%s/%s.graph.tarveltime.edge.csv" % (sOutDir, sTmpFile), 'w')

       my_edges = {}
       my_node = {}

       # Within each time segment is a dictionary of the taxi's trajectory
       # keyed by the taxi's plate.
       nTaxiProcessed = 0
       nRecProcessed = 0
       
       for taxiKey, taxiVal in data.items():

          # if not nTaxiProcessed % 10000:
          #    print("#", end='')
          # if not nTaxiProcessed % 200000:
          #    print("\n", end='')
          
          # taxiVal = [['B51C92', '1340755223', '42114', 'False', '0'], ['B51C92', '1340755254', '42114', 'False', '0']]
          # 0 : car plate; 1: time by second; 2 : roadID; 3: loaded; 4: speed
          # sort trajactory by time

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
             if (not options.bFilterRepeats) or (not (point[2] == lastRoadId)):

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

                if options.bAugmentSpeed and nSpd > nSpdBucketRange:
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
                  # Cheng modified
                  my_node[item[2]] = [1, float(item[4]), [float(item[4])] ]  # # 0 : car plate; 1: time by second; 2 : roadID; 3: loaded; 4: speed
                  
              else:
                  my_node[item[2]][0] += 1
                  my_node[item[2]][1] += float(item[4])
                  # Cheng modified
                  my_node[item[2]][2].append(float(item[4]))

          # END of the content of one taxi trajactory
          pass

       # calculate average travel time of each node.
       print("Outputing node with average travel time, speed ,and flow....")
       for key, value in my_node.items():
           if key not in road:
               road[key] = [0.0, 0.0, 0.0]
               print(key + "is not in road")

           tempSpeed = value[1];

           if value[0] == 0:
               tempSpeed = 0;
           else:
               tempSpeed = tempSpeed / value[0]
               # Cheng modified calculate standard deviation
               stdDev = (sum([(sp - tempSpeed) ** 2 for sp in value[2]]) / float(value[0])) ** 0.5

           
           tempTravelTime = float(road[key][0])
           if tempSpeed != 0:
               tempTravelTime /= tempSpeed

           outFile_node.write("%s %f %f %d %f\n" % (key, tempTravelTime, tempSpeed, value[0], stdDev))  # average travel time of "key" road segment, speed, flow;
           jsonData[-1]["nodes"][str(key)] = {"speed": tempSpeed,
                                              "flow": value[0],
                                              "travelTime": tempTravelTime,
                                              "distance": float(road[key][0]),
                                              "SD": stdDev
                                              }
       '''
       #for key, value in my_edges.items():
       print("Outputing edge with flow....")
       for key, value in sorted(my_edges.items(), key=lambda weight: weight[1], reverse=True):
            IDs = key.strip().split("#")
            sID = int(IDs[0])
            tID = int(IDs[1])
            flow = int(value)
            outFile_edge.write("%d %d %d\n" % (sID, tID, flow)) # average travel time of "key" road segment;
       '''

       outFile_node.close()
       outFile_edge.close()


       print("Betweenness centrolity graph generation done....")

       # Print some statistics on the processed data
       print("Time slot: %s" % (sTmpFile))
       print(" %s edges filtered by distance threshold." % (numberOfThreshold))
       print(" %s edges filtered by time threshold." % (numberOfTimeThreshold))
       print("   Total taxis  : %d" % (nTaxiProcessed))
       print("   Total points : %d" % (nRecProcessed))
       
    #Write to json file
    jsonFile.write(json.dumps(jsonData, indent=4, sort_keys=False))


    end_time = datetime.datetime.now();
    print("DONE by %f s" % ((end_time - start_time).total_seconds()));
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Clean up the temp directory
    # print( "Temp directory at %s" % (sTmpDir) )
    shutil.rmtree(sTmpDir, True)

