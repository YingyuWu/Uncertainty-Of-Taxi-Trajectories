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

# This script will process the TMT summary.txt ouput file and generate
# a script that can be read in to the TaxiVis application.

import random
import time
import calendar
import math

iColor = 0
colors = [ \
      "#000000", "#986960", "#0892D0", "#0FC0FC", "#00FFFF", \
      "#808000", "#00A693", "#746CC0", "#FE4164", "#0000FF", \
      "#195905", "#CD5B45", "#39FF14", "#DF00FF", \
      "#66023C", "#0077BE", "#FF0000", "#FF0090", \
      "#80461B", "#8601AF", "#00CCCC", "#FF7E00",            \
      "#738276", "#9AB973", "#FB4F14", "#FFCC00",            \
      
      "#888888", "#000000", "#FF0000", "#CCCC00", "#008800", "#00FFFF", "#8888FF", "#CC33CC", "#A0A424", "#411BEA", \
      "#ED7651", "#FEF888", "#19CB97", "#369628", "#7E7EB8", "#5DFC0A", "#5F9EA0", "#668014", "#691F01", "#76EE00", \
      "#800000", "#820BBB", "#8B2500", "#8B5A00", "#9932CC", "#9AFF9A", "#CD3700", "#CFB53B", "#EE00EE", "#3B3178", \
      "#FBEC5D", "#3EA055", "#003F87", "#00FF00", "#05B8CC", "#213D30", "#2E37FE", "#32CD32", "#37BC61", "#3E6B4F", \
      "#435D36", "#45C3B8", "#4A7023", "#539DC2", "#5959AB", "#615E3F", "#683A5E", "#6F4242", "#7FFF00", "#8B4726", \
      "#93DB70", "#B452CD", "#C0D9D9", "#CD4F39", "#E6E6FA", "#333333", "#00868B", "#05E9FF", "#238E68", "#2E473B", \
      "#32CD99", "#474747", "#5D478B", "#87421F", "#FFFFF0", "#FFD700", "#FFBBFF", "#FF92BB", "#FF6EB4", "#FF00FF", \
      "#FBA16C", "#F6A4D5", "#F0F0F0", "#EEDD82", "#EE82EE", "#EE2C2C", "#EBEBEB", "#E3701A", "#DFFFA5", "#DCDCDC", \
      "#D9D9F3", "#D19275", "#CDCD00", "#CDAD00", "#CD3333", "#CC7F32", "#C76114", "#C3E4ED", "#C0FF3E", "#BF5FFF", \
      "#BCE937", "#B87333", "#B62084", "#B3C95A", "#AF4035", "#AAAAFF", "#A52A2A", "#A2BC13", "#9CCB19", "#9BC4E2", \
      "#993300", "#969696", "#92CCA6", "#912CEE", "#8CDD81", "#8B795E", "#8B4500", "#8968CD", "#86C67C", "#8470FF", \
      "#7CFC00", "#77896C", "#71C671", "#6B8E23", "#67E6EC", "#6600FF", "#629632", "#5F755E", "#5D478B", "#586949", \
      "#543948", "#4F2F4F", "#4AC948", "#458B00", "#42526C" ]


# -----------------------------------------------------------------------------
# Input file format:
#  Taxi Plate, ISO8601 time, loaded, speed, heading, lat, lon, road name, road id
#  ?¨¬??¨¬?B40P00,2012-06-27 00:01:46,1,0,0,22.541918,114.110046,n,19806
# The following are the indices into a CSV record
iPlate = 0
iTime  = 1
iLoad  = 2
iSpd   = 3
iHdg   = 4
iLat   = 5
iLon   = 6
iRoad  = 7
iRId   = 8


# -----------------------------------------------------------------------------
# Time formatting strings
sTimeFormatIn  = "%Y-%m-%d %H:%M:%S"
sTimeFormatOut = "%Y-%m-%dT%H-%M-%S"


# -----------------------------------------------------------------------------
# Prepare data for processing by cleaning up and transforming formats
def PreProcessData( fields ):

   # Strip the unicode characters so the LDA can accept the input.
   fields[iPlate] = fields[iPlate].strip()[2:]

   if len(fields) < 8:
       return False

   try:
      # Determine if the record has a valid road id, if not, it's not usable
      # Null road IDs are represented as 'n' and will fail the transform to int
      # causing the record to be ignored.
      fields[iRId] = int(fields[iRId])

      # Convert the loaded field to a boolean
      if int(fields[iLoad]) == 0:
         fields[iLoad] = False
      else:
         fields[iLoad] = True

      # Convert time to comparable form. (data form is 2012-06-26 23:59:56)
      fields[iTime] = calendar.timegm(time.strptime(fields[iTime], sTimeFormatIn))
   except ValueError:
      return False

   # Everything is good, use the record.
   return True


# -----------------------------------------------------------------------------
# Creates a random hex color string compatible with the Qt's 
# QColor::setNamedColor.
def randomColor():
   r = hex(int(random.random()*256))
   g = hex(int(random.random()*256))
   b = hex(int(random.random()*256))

   r = r.replace("0x","")
   g = g.replace("0x","")
   b = b.replace("0x","")

   if len(r) < 2:
      r = "0" + r
   if len(g) < 2:
      g = "0" + g
   if len(b) < 2:
      b = "0" + b

   return "#" + r + g + b


# -----------------------------------------------------------------------------
# Attemps to pull a color from the color table or grabs a random color if one
# does not already exist.
def stableRandomColor( nIdx ):

   # Check if the color already exists in the color table
   if nIdx > len(colors)-1:
      while len(colors)-1 < nIdx:
         colors.append( randomColor() )

   # Return the requested color
   return colors[nIdx]


def distance(array):
    result = 0;
    for i, point in enumerate(array[0:-1]):
          result +=  math.sqrt((point[0]-array[i+1][0])*(point[0]-array[i+1][0])+(point[1]-array[i+1][1])*(point[1]-array[i+1][1]))

    return result * 1e4;