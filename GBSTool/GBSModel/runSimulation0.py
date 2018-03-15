# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: February 28, 2018
# License: MIT License (see LICENSE file of this package for more information)

import cProfile
import numpy as np
import numpy as np
import os
import os
import pandas as pd
# add to sys path
import sys
import tkinter as tk
from shutil import copyfile
from tkinter import filedialog
import sqlite3

from SystemOperations import SystemOperations

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, '../'))
sys.path.append(here)
from GBSInputHandler.writeXmlTag import writeXmlTag
from GBSInputHandler.readXmlTag import readXmlTag
from GBSInputHandler.fillProjectData import fillProjectData
import glob
from GBSAnalyzer.DataWriters.writeNCFile import writeNCFile
from GBSInputHandler.writeXmlTag import writeXmlTag

def runSimulation(projectSetDir = ''):

    if projectSetDir == '':
        print('Choose the project directory')
        root = tk.Tk()
        root.withdraw()
        projectSetDir = filedialog.askdirectory()

    # get set number
    dir_path = os.path.basename(projectSetDir)
    setNum = int(dir_path[3:])
    # get the project name
    os.chdir(projectSetDir)
    os.chdir('../..')
    projectDir = os.getcwd()
    projectName = os.path.basename(projectDir)
    # timeseries directory
    timeSeriesDir = os.path.join(projectDir,'InputData','TimeSeriesData','ProcessedData')

    # get project name, from the directory name
    projectSetupFile = os.path.join(projectSetDir,'Setup',projectName+'Set'+str(setNum)+'Setup.xml')

    # get the time step
    timeStep = readXmlTag(projectSetupFile,'timeStep','value',returnDtype = 'int')[0]

    # get the time steps to run
    runTimeSteps = readXmlTag(projectSetupFile,'runTimeSteps','value')
    if len(runTimeSteps) == 1: # if only one value, take out of list. this prevents failures further down.
        runTimeSteps = runTimeSteps[0]
        if not runTimeSteps == 'all':
            runTimeSteps = int(runTimeSteps)
    else: # convert to int
        runTimeSteps = [int(x) for x in runTimeSteps]

    # get the load predicting function
    predictLoad = readXmlTag(projectSetupFile,'predictLoad','value')[0]

    # get the wind predicting function
    predictWind = readXmlTag(projectSetupFile,'predictWind','value')[0]

    # get the ees dispatch
    eesDispatch = readXmlTag(projectSetupFile,'eesDispatch','value')[0]

    # get the minimum required SRC calculation
    getMinSrcFile = readXmlTag(projectSetupFile, 'getMinSrc', 'value')[0]

    # get the components to run
    componentNames = readXmlTag(projectSetupFile, 'componentNames', 'value')

    # get the load profile to run
    loadProfileFile = readXmlTag(projectSetupFile, 'loadProfileFile', 'value')[0]
    loadProfileFile = os.path.join(timeSeriesDir,loadProfileFile)

    # TODO
    # get the gen dispatch
    genDispatch = []
    # get the wtg dispatch
    wtgDispatch = []

    while 1:
        # read the SQL table of runs in this set and look for the next run that has not been started yet.
        conn = sqlite3.connect(os.path.join(projectSetDir,'set' + str(setNum) + 'ComponentAttributes.db') )# create sql database
        df = pd.read_sql_query('select * from compAttributes',conn)
        # try to find the first 0 value in started column
        try:
            runNum = list(df['started']).index(0)
        except: # there are no more simulations left to run
            break
        # set started value to 1 to indicate starting the simulations
        df['started'][runNum] = 1
        df.to_sql('compAttributes', conn, if_exists="replace", index=False)  # write to table compAttributes in db
        conn.close()
        # Go to run directory and run
        runDir = os.path.join(projectSetDir,'Run'+ str(runNum))
        runCompDir = os.path.join(runDir,'Components') # component directory for this run
        # output data dir
        outputDataDir = os.path.join(runDir, 'OutputData')
        if not os.path.exists(outputDataDir): # if doesnt exist, create
            os.mkdir(outputDataDir)
        eesIDs = []
        eesSOC = []
        eesStates = []
        eesSRC = []
        eesDescriptors = []
        wtgIDs = []
        wtgStates = []
        wtgDescriptors = []
        windSpeed = []
        genIDs = []
        genStates = []
        genDescriptors = []

        for cpt in componentNames:  # for each component
            # check if component is a generator
            if 'gen' in cpt.lower():
                genDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Descriptor.xml')]
                genIDs += [cpt[3:]]
                genStates += [2]
            elif 'ees' in cpt.lower():  # or if energy storage
                eesDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Descriptor.xml')]
                eesIDs += [cpt[3:]]
                eesStates += [2]
                eesSRC += [0]
                eesSOC += [0]
            elif 'wtg' in cpt.lower():  # or if wind turbine
                wtgDescriptors += [os.path.join(runCompDir, cpt.lower() + 'Descriptor.xml')]
                wtgIDs += [cpt[3:]]
                wtgStates += [2]
                windSpeed += [os.path.join(timeSeriesDir, cpt.lower() + 'WS.nc')]

        # initiate the system operations
        # code profiler
        pr0 = cProfile.Profile()
        pr0.enable()
        SO = SystemOperations(timeStep = timeStep, runTimeSteps = runTimeSteps, loadRealFiles = loadProfileFile, loadReactiveFiles = [],
                              predictLoad = predictLoad, predictWind = predictWind, getMinSrcFile = getMinSrcFile,
                         genIDs = genIDs, genStates = genStates, genDescriptors = genDescriptors, genDispatch = genDispatch,
                         wtgIDs = wtgIDs, wtgStates = wtgStates, wtgDescriptors = wtgDescriptors, wtgSpeedFiles = windSpeed, wtgDispatch = wtgDispatch,
                         eesIDs = eesIDs, eesStates = eesStates, eesSOCs = eesSOC, eesDescriptors = eesDescriptors, eesDispatch = eesDispatch)
        # stop profiler
        pr0.disable()
        pr0.print_stats(sort="calls")

        # run the simulation
        # code profiler
        pr1 = cProfile.Profile()
        pr1.enable()
        # run sim
        SO.runSimulation()
        # stop profiler
        pr1.disable()
        pr1.print_stats(sort="calls")

        # save data
        os.chdir(outputDataDir)
        writeNCFile(SO.DM.realTime,SO.genP,1,0,'kW','genPRun'+str(runNum)+'.nc') # gen P
        writeNCFile(SO.DM.realTime, SO.rePlimit, 1, 0, 'kW', 'rePlimitRun' + str(runNum) + '.nc')  # rePlimit
        writeNCFile(SO.DM.realTime, SO.wtgPAvail, 1, 0, 'kW', 'wtgPAvailRun' + str(runNum) + '.nc')  # wtgPAvail
        writeNCFile(SO.DM.realTime, SO.wtgPImport, 1, 0, 'kW', 'wtgPImportRun' + str(runNum) + '.nc')  # wtgPImport
        writeNCFile(SO.DM.realTime, SO.wtgPch, 1, 0, 'kW', 'wtgPchRun' + str(runNum) + '.nc')  # wtgPch
        writeNCFile(SO.DM.realTime, SO.wtgPTot, 1, 0, 'kW', 'wtgPTotRun' + str(runNum) + '.nc')  # wtgPTot
        writeNCFile(SO.DM.realTime, SO.srcMin, 1, 0, 'kW', 'srcMinRun' + str(runNum) + '.nc')  # srcMin
        writeNCFile(SO.DM.realTime, SO.eesDis, 1, 0, 'kW', 'eesDisRun' + str(runNum) + '.nc')  # eesDis
        writeNCFile(SO.DM.realTime, SO.eessP, 1, 0, 'kW', 'eessPRun' + str(runNum) + '.nc')
        writeNCFile(SO.DM.realTime, SO.genPAvail, 1, 0, 'kW', 'genPAvailRun' + str(runNum) + '.nc')  # genPAvail
        writeNCFile(SO.DM.realTime, SO.onlineCombinationID, 1, 0, 'NA', 'onlineCombinationIDRun' + str(runNum) + '.nc')  # onlineCombinationID
        writeNCFile(SO.DM.realTime, SO.underSRC, 1, 0, 'kW', 'underSRCRun' + str(runNum) + '.nc')  # underSRC
        writeNCFile(SO.DM.realTime, SO.outOfNormalBounds, 1, 0, 'kW', 'outOfNormalBoundsRun' + str(runNum) + '.nc')  # outOfNormalBounds

        # start times for each generators
        for idx, genST in enumerate(zip(*SO.genStartTime)): # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genST, 1, 0, 's', 'gen' + str(SO.PH.genIDS[idx]) + 'StartTimeRun' + str(runNum) + '.nc')  # eessSoc

        # run times for each generators
        for idx, genRT in enumerate(zip(*SO.genRunTime)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, genRT, 1, 0, 's',
                        'gen' + str(SO.PH.genIDS[idx]) + 'RunTimeRun' + str(runNum) + '.nc')  #

        # SRC for each ees
        for idx, eesSRC in enumerate(zip(*SO.eessSrc)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, eesSRC, 1, 0, 'kW',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'SRCRun' + str(runNum) + '.nc')  #

        # SOC for each ees
        for idx, eesSOC in enumerate(zip(*SO.eessSoc)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, eesSOC, 1, 0, 'PU',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'SOCRun' + str(runNum) + '.nc')  # eessSoc

        # ees loss
        for idx, eesLoss in enumerate(zip(*SO.eesPLoss)):  # for each generator in the powerhouse
            writeNCFile(SO.DM.realTime, eesLoss, 1, 0, 'kW',
                        'ees' + str(SO.EESS.eesIDs[idx]) + 'LossRun' + str(runNum) + '.nc')