# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 24, 2017
# License: MIT License (see LICENSE file of this package for more information)

# reads data files from user and outputs a dataframe.
def readDataFile(inputSpecification,fileLocation='',fileType='csv',columnNames=None,useNames=None,componentUnits=None,componentAttributes=None):
    # inputSpecification points to a script to accept data from a certain input data format
    # fileLocation is the dir where the data files are stored. It is either absolute or relative to the GBS project InputData dir
    # fileType is the file type. default is csv. All files of this type will be read from the dir
    # columnNames, if specified, is a list of column names from the data file that will be returned in the dataframe.
    # otherwise all columns will be returned. Note indexing starts from 0.

    ####### general imports #######
    import pandas as pd
    from tkinter import filedialog
    import os
    from readAvecCsv import readAvecCsv
    import numpy as np
    from readXmlTag import readXmlTag

    ###### go to directory with time series data is located #######
    if fileLocation=='':
        print('Choose directory where input data files are located.')
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        fileLocation = filedialog.askdirectory()
    os.chdir(fileLocation)
    here = os.getcwd()
    # get just the filenames ending with fileType
    fileNames = [f for f in os.listdir(here) if os.path.isfile(f) & f.endswith(fileType)]

    ####### Parse the time series data files ############
    # depending on input specification, different procedure
    if inputSpecification=='AVEC':
    # In the case of AVEC, data files are broken into months. Append them.
        for i in range(len(fileNames)): # for each data file
            if i == 0: # read data file into a new dataframe if first iteration
                df = readAvecCsv(fileNames[i],fileLocation,columnNames,useNames,componentUnits)
            else: # otherwise append
                df2 = readAvecCsv(fileNames[i],fileLocation,columnNames,useNames,componentUnits) # the new file
                # get intersection of columns,
                df2Col = df2.columns
                dfCol = df.columns
                #TODO: this does not maintain the order. It needs to be modified to maintain order of columns
                #dfNewCol = list(set(df2Col).intersection(dfCol))
                dfNewCol = [val for val in dfCol if val in df2Col]
                # resize dataframes to only contain collumns contained in both dataframes
                df = df[dfNewCol]
                df2 = df2[dfNewCol]
                df = df.append(df2) # append

    # try to convert to numeric
    df = df.apply(pd.to_numeric,errors='ignore')

    # convert units
    if np.all(componentUnits!=None):
        for i in range(len(componentUnits))# for each channel
            #TODO: finish adding code to get unit conersion file and update and convert units to default internal units and values to intergers.
            # cd to unit conventions file
            here = os.getcwd()
            dir_path = os.path.dirname(os.path.realpath(__file__))
            fileDir = dir_path +'..\Resources\Conventions'
            # get the default unit for the data type
            units = readXmlTag('internalUnitDefault.xml', ['unitDefaults',componentAttributes[i]], 'units', fileDir)
            # if the units don't match, convert
            if units!=componentUnits[i]:


            dir_path = dir_path + '..\GBSAnalyzer\UnitConverters'
            os.chdir(dir_path)

    # ind = df.dtypes == 'object' # get instances of where did not convert to numeric
    # df_temp = df.iloc[:,ind.values]
    # df.iloc[:,ind.values] = df.iloc[:,ind.values].apply(str,errors='ignore')
    # df.loc[:, lambda df: df.dtypes == 'object'] = df.loc[:,lambda df: df.dtypes=='object'].astype(str)
    return df

