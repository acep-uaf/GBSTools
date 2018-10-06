# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 18, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is for the reading of a CSV file of the type generated by AVEC
def readAvecCsv(inputDict):
    '''
    Reads a single csv file formatted in the AVEC style
    :param inputDict:  fileName,fileLocation,columnNames,useNames,componentUnits, dateColumnName, dateColumnFormat, timeColumnName, dst
    :return: pandas.DataFrame of the csv data.
    '''

    # general imports
    import numpy as np
    import os
    import tkinter as tk
    from tkinter import filedialog
    import pandas as pd
    
    from GBSInputHandler.processInputDataFrame import processInputDataFrame

    # process input variables
    # convert numpy arrays to lists
    if type(inputDict['columnNames'])== np.ndarray:
        inputDict['columnNames'] = inputDict['columnNames'].tolist()
    if type(inputDict['useNames'])== np.ndarray:
        inputDict['useNames'] = inputDict['useNames'].tolist()
    # -------------- cd to file location ------------------------
    # TODO: Set this up such that it can easily setup with an interactive interface later (either command line or GUI)
    # if no fileLocation is specified, request the user to input one.
    if inputDict['fileLocation']=='':
        print('Choose directory where input data files are located.')
        root = tk.Tk()
        root.withdraw()
        inputDict['fileLocation'] = filedialog.askdirectory()
    os.chdir(inputDict['fileLocation'])


    #------------------- load the file -----------------------------
    df = pd.read_csv(inputDict['fileName']) # read as a data frame
    
    # check and see if the df column names match the input specification.
    # TODO: throw a catch in here in case it does not find the headers
    gotHeader = False
    columnNamesFromCSV = df.columns.str.replace('\s+', '_')
    if inputDict['columnNames'][0] not in columnNamesFromCSV:
        # if the first row is not the header, look for it further down in the file
        for col in df.columns:
            a = df[col]
            a = a.str.replace('\s+', '_')
            # get the matches for the column name
            idxMatch = a.index[a == inputDict['columnNames'][0]].tolist()
            if len(idxMatch) != 0:
                df.columns = df.loc[idxMatch[0]].str.replace('\s+', '_')
                gotHeader = True
                break
        if gotHeader is False:
            raise ValueError('Input column names were not found in the CSV file.')
    inputDict['df'] = df
    df = processInputDataFrame(inputDict)
    

    return df

