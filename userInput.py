# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 14:58:58 2021

@author: Cagatay Alici
"""

# imports functions used for automation in helios
from automationHelper import automaticScan, combineXYZ


# modify input according to your data
####################################### INPUT ########################################

# Number of bridges that is going to be used:
noOfBridges = 3

# Index of the bridge that is going to be used first. e.g: If startIndex = 2 and noOfBridges = 3, the program will use bridge2, bridge3, and bridge4.
startIndex= 1

# Purpose of using the program: 
#   - If the program is used only for scanning bridges without combining the output, purpose = "scan"
#   - If the program is used only for combining already scanned bridges without scanning again, purpose = "combine"
#   - If the program is used for both, purpose = "scan&combine"
purpose = "scan&combine" # available options: "scan", "combine", and "scan&combine"

# If the bridges that are going to be used have the same environment (background), set it to True so that only the environment of bridge given by startIndex is going to be scanned. 
# Then it is going to be added to other bridges given by the interval [startIndex,startIndex+noOfBridges]
isSameEnvironment = False # If False, environment of each bridges will be scanned seperately

# If output of Helios is not desired to be seen during scanning, set it to False.
verbose = False

# Structural elements that are created in Revit and their labels in Point Cloud (can add more elements and labels): 
classes = {
  "abutments": 0,
  "piers": 1,
  "deck": 2,
  "railings": 3,
  "environment": 4
}

# Name of the project where different bridges will be stored:
projectName = "SoftwareLab"

shuffle = True # if True, the combined text file for point cloud is shuffled so that points are not ordered with respect to scanning order


# Pulse frequency of lidar that is simulated by Helios. If it is set manually, these two values can be left as None, otherwise 
# define a value that is going to be used in each scan. The higher the value the denser the point clouds will be. However simulation time 
# and memory consumption increases as well. 
pulseFreq_tripod = 15000 # pulse frequency (Hz) for tripod scanning
pulseFreq_airplane = 120000 # pulse frequency (Hz) for airplane scanning

#######################################      ########################################



# Repeats scanning and combining procedure for all bridges, starting from "startIndex"th bridge till "startIndex+noOfBridges"th bridge
for i in range (startIndex,startIndex+noOfBridges):

    bridgeName = "bridge" + str(i)

    print("\nProccessing bridge"+str(i)+"...\n")
    
    # Scans the bridge 
    if ( purpose == "scan&combine" or purpose == "scan" ):
        print("Scaning bridge"+str(i)+"...\n")
        automaticScan (bridgeName,isSameEnvironment,startIndex,verbose,classes,projectName,pulseFreq_tripod,pulseFreq_airplane)
        # automaticScan (bridgeName,isSameEnvironment,startIndex,verbose,classes,projectName)
        print("\nScaning of bridge"+str(i)+" is complete!\n")
        
    # Combines the xyz files of the scanned bridge    
    if ( purpose == "scan&combine" or purpose == "combine" ):
        print("Combining xyz files of bridge"+str(i)+"\n")
        combineXYZ(bridgeName,isSameEnvironment,startIndex,classes,shuffle)
        print("\nCombining xyz files of bridge"+str(i)+" is complete!\n")