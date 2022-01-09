# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 10:11:06 2021

@author: Cagatay Alici
"""

import os 
from xml.dom import minidom
import codecs
import subprocess,shlex
import numpy as np

# Combines .xyz files that are results of scanning
def combineXYZ (bridgeName:str, isSameEnvironment:bool, startIndex:int, classes:dict, shuffle:bool):
    

    basefilePath = os.getcwd()
    completePath =  os.path.join(basefilePath, "output\\Survey Playback\\")
    textFile = bridgeName + "_combined.txt"
    outputFilePath = os.path.join(basefilePath, "output\\combined",textFile)
    if not os.path.exists(os.path.join(basefilePath, "output\\combined")):
                os.makedirs(os.path.join(basefilePath, "output\\combined"))
    os.chdir(completePath)
    
    
    combinedData = np.array([], dtype=np.float64).reshape(0,4) # stores whole point cloud (x,y,z,label)
    
    for clas in classes:
    
        try:
            # If environment survey is going to be included and if the same environment is used for whole bridges, 
            # then environment of the 'startIndex'th bridge is included in point cloud
            if(clas == "environment" and isSameEnvironment):
                fileName = "bridge" + str(startIndex) + "_" + clas + "_survey"
            else:
                fileName = bridgeName + "_" + clas + "_survey"
                
            targetPath =  os.path.join(completePath, fileName)
            os.chdir(targetPath)
            
            label = classes[clas] # extracts label of the corresponding class 
            
            for file in os.listdir():
                
                readPath =  os.path.join(targetPath,file,"points\\")
                os.chdir(readPath)
             
                for file in os.listdir():
                    if file.endswith(".xyz"):
                        if os.path.getsize(file) > 0: # if the file is not empty
                            coordinates =  np.loadtxt(file)[:,:3]                   
                            labelArray = np.ones((coordinates.shape[0], 1))*label
                            pointCloud = np.hstack((coordinates,labelArray))
                            combinedData = np.vstack([combinedData, pointCloud])
  
        except  OSError as e:
            print(bridgeName +  "_" + clas + ".obj is not found!" )
            continue  
    
    if shuffle:
        np.random.shuffle(combinedData)      
        
    np.savetxt(outputFilePath, combinedData,fmt='%1.4f', delimiter=' ')
    os.chdir(basefilePath)
    

# runs the command from python
def autoRun (command:str, verbose:bool):

    
    basefilePath = os.getcwd()
    os.chdir(basefilePath)
    
    if verbose == True:    
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, text= True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print (output.strip())
                rc = process.poll()
    else:
        process = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, text= True)
        print(process.stdout)
        rc = 1

    return rc


# Creates commands that are going to be run for simulation in Helios
def runHelios(bridgeName:str, clas:str, verbose:bool, projectName:str, surveyList:list):
    
    bridgeNumber = bridgeName.replace("bridge","")
   
    for survey in surveyList:
        if (clas == "environment"):
            if( clas in survey.lower()):
                command = "helios.exe data/surveys/" + projectName + "/"+ bridgeNumber + "/" + survey
                if not verbose:
                    command = command + " --quiet"
                autoRun(command,verbose)
                                
        else: 
            if( "component" in survey.lower()):
                command = "helios.exe data/surveys/" + projectName + "/"+ bridgeNumber + "/" + survey
                if not verbose:
                    command = command + " --quiet"
                autoRun(command,verbose)
                 

# Edits XML file of corresponding classes for scene and survey:
def editXML (bridgeName:str, clas:str, projectName:str, pulseFreq_tripod:int = None, pulseFreq_airplane:int = None):
    
    
    basefilePath = os.getcwd()
    bridgeNumber = bridgeName.replace("bridge","") # extracts bridge number
    
    ### XML file of scene is edited: 
    sceneFile = "data\\scenes\\" + projectName # adress of the corresponding scene file
    completeFilePath = os.path.join(basefilePath, sceneFile)
    os.chdir(completeFilePath)
    
    for file in os.listdir():
        if file.endswith(".xml"):
            XMLFile = file
            
    # lists te XML file for scene in the folder (assumed only single scene xml file will be there)
    #file = minidom.parse('bridge_scene.xml') # opens 'bridge_scene.xml' file
    file = minidom.parse(XMLFile)
    parameters = file.getElementsByTagName('param')# gets elements of 'param' tag in the XML file
    
    # Sets the value of attribute 'value' of the first 'param' to corresponding obj file
    parameters[0].attributes["value"].value = "data/sceneparts/" + projectName + "/" + bridgeNumber + "/" + bridgeName + "_" + clas +".obj"
    
    # Saves the edited XML file
    f = codecs.open(XMLFile, mode='w', encoding='UTF-8')
    file.writexml(f, encoding="UTF-8")
    f.close()
    
    ### XML file of survey is edited: 
    surveyFile = "data\\surveys\\"  + projectName + "\\" + bridgeNumber # adress of the corresponding survey file
    completeFilePath = os.path.join(basefilePath, surveyFile)
    os.chdir(completeFilePath)
    
    surveyList = os.listdir()
    # Lists all xml files in the folder:
    for XMLFile in surveyList:
        file = minidom.parse(XMLFile)
        surveys = file.getElementsByTagName('survey')
        surveys[0].attributes["scene"].value = "data/scenes/" + projectName + "/bridge_scene.xml#bridge_scene"
        
        scannerSettings = file.getElementsByTagName('scannerSettings')
        # For the structural elements of the bridge and environment different survey files are used. For the bridge components, laser scanners are located along the bridge and closer.
        # Additionally, laser scanner placements are the same for all components belonging to the bridge. On the other hand, laser scanners for the environment are different than 
        # for those in components of the bridge.
       
        # If the name of xml file contains "component"
        if "component" in XMLFile.lower():
            surveys[0].attributes["name"].value = bridgeName + "_" + clas + "_survey"
      
        # If the name of xml file contains "environment"   
        elif "environment" in XMLFile.lower():
             surveys[0].attributes["name"].value = bridgeName + "_environment_survey"
           
        
        # if tripod pulse frequency is set automatically: 
        if("tripod" in XMLFile.lower() and pulseFreq_tripod is not None):
            scannerSettings[0].attributes["pulseFreq_hz"].value = str(pulseFreq_tripod)
        
        # if airplane pulse frequency is set automatically:  
        elif("airplane" in XMLFile.lower() and pulseFreq_airplane is not None):
            for i in range(len(scannerSettings)):
                scannerSettings[i].attributes["pulseFreq_hz"].value = str(pulseFreq_airplane)

        # creates a new XML file with the same name and saves it in the same directory
        f = codecs.open(XMLFile, mode='w', encoding='UTF-8')
        file.writexml(f, encoding="UTF-8")
        f.close()
            
    os.chdir(basefilePath)
    return surveyList
    
    
# def automaticScan (bridgeName,isSameEnvironment,startIndex,verbose,classes,projectName):
def automaticScan (bridgeName:str, isSameEnvironment:bool, startIndex:int, verbose:bool, classes:dict, projectName:str, pulseFreq_tripod:int = None, pulseFreq_airplane:int = None):
    
    # loops over all classes defined the dictionary 
    for clas in classes:
        
        try:
            
            print("\n     Scaning " + clas + "...")
             
            # If the class is 'environment', it is only scanned for the bridges that are not the "startIndex"th bridge and when the environment of bridges are different.
            # i.e suppose start index = 1, isSameEnvironment = 1 => compiler will not go into this if statement if bridgeName is 'bridge1'. 
            if( (clas == "environment") and (bridgeName != "bridge" + str(startIndex))):
                if (not isSameEnvironment):
                    surveyList = editXML(bridgeName,clas,projectName,pulseFreq_tripod,pulseFreq_airplane)
                    runHelios(bridgeName,clas,verbose,projectName,surveyList)
                    
            # For other classes and for the case where environment of each bridge is different
            else:
                surveyList = editXML(bridgeName,clas,projectName,pulseFreq_tripod,pulseFreq_airplane) # edits XML file of corresponding class for scene and survey
                runHelios(bridgeName,clas,verbose,projectName,surveyList) # runs helios 
        
        # If there is no obj file for the class, it continues with scaning other classes.
        except  OSError as e:
            print(".obj file for the " + clas + " of the " + bridgeName + " is not found!")
            continue
                



            
            
        