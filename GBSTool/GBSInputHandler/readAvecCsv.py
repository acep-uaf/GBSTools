# TODO: File header here
# TODO: Use more comments throughout ;-)
# TODO: Bundle all `import' statements at the top
# Project: GBS Tool
# Author: Jeremy VanderMeer, jbvandermeer@alaska.edu
# Date: October 18, 2017
# License: MIT License (see LICENSE file of this package for more information)

# this function is for the reading of a CSV file of the type generated by AVEC
def readAvecCsv(fileName,fileLocation,columnNames,useNames,componentUnits, dateColumnName, dateColumnFormat, timeColumnName = '', timeColumnFormat = '', utcOffsetValue = None, utcOffsetUnit = None, dst = None):
    # general imports
    import numpy as np
    import os
    import tkinter as tk
    from tkinter import filedialog
    import pandas as pd
    import datetime
    from GBSInputHandler.processInputDataFrame import processInputDataFrame

    # process input variables
    # convert numpy arrays to lists
    if type(columnNames)== np.ndarray:
        columnNames = columnNames.tolist()
    if type(useNames)== np.ndarray:
        useNames = useNames.tolist()
    # -------------- cd to file location ------------------------
    # TODO: Set this up such that it can easily setup with an interactive interface later (either command line or GUI)
    # if no fileLocation is specified, request the user to input one.
    if fileLocation=='':
        print('Choose directory where input data files are located.')
        root = tk.Tk()
        root.withdraw()
        fileLocation = filedialog.askdirectory()
    os.chdir(fileLocation)


    #------------------- load the file -----------------------------
    df = pd.read_csv(fileName) # read as a data frame
    # TODO: REMOVE THIS, FOR TESTING ONLY
    df = df.drop(df.index[range(1000,len(df))])
    # check and see if the df column names match the input specification.
    # TODO: throw a catch in here in case it does not find the headers
    gotHeader = False
    columnNamesFromCSV = df.columns.str.replace('\s+', '_')
    if columnNames[0] not in columnNamesFromCSV:
        # if the first row is not the header, look for it further down in the file
        for col in df.columns:
            a = df[col]
            a = a.str.replace('\s+', '_')
            # get the matches for the column name
            idxMatch = a.index[a == columnNames[0]].tolist()
            if len(idxMatch) != 0:
                df.columns = df.loc[idxMatch[0]].str.replace('\s+', '_')
                gotHeader = True
                break
        if gotHeader is False:
            raise ValueError('Input column names were not found in the CSV file.')
    else:
        df.columns = columnNamesFromCSV
    '''
    # remove non numeric rows
    df[columnNames[0]] = df[columnNames[0]].apply(pd.to_numeric,errors='coerce') # convert to numeric, non numeric set to NaN
    # find all NaN values, remove rows
    idxNaN = df.index[df[columnNames[0]]==]
    '''
    '''
    x=np.array(df) # convert data frame to array (since every ~ 60th row is a header, which needs to be removed)
    # TODO: have you already found a good cheat sheet for regular expressions? Let me know if you need one.
    #import re
    #non_decimal = re.compile(r'[^\d.]+')
    #non_decimal.sub('', '12.345i5ii3')

    # convert to float. If not possible (headers), replace with the value 1000000 which will be eliminated
    gotHeader = False
    for i in range(x.shape[0]): # for all rows
        for j in range(x.shape[1]): # for all columns
            if isinstance(x[i,j],str): #if is string
                try: # try to convert to a float
                    x[i,j] = float(x[i, j])
                except: # if can't, replace with nan
                    if j==2: # for the third column(after DATE and TIME, which are strings).
                        if gotHeader==False:
                            header = list(x[i,:])
                            gotHeader = True
                        x[i, :] = np.nan

    ind = pd.isnull(x[:,0]) # find all rows with value nan
    x = x[~ind,:] # remove nan values
    dfNew = pd.DataFrame(x, columns=header) # create a temporary dataframe with all columns
    dfNew.columns = dfNew.columns.str.strip()  # remove white spaces at begining and end of headers
    dfNew.columns = dfNew.columns.str.replace('\s+', '_')  # replace spaces in between with underscores

    if columnNames!=None:
        if all(isinstance(n,str) for n in columnNames): # if columnNames are strings (header names)
            if isinstance(columnNames,(list,tuple,np.ndarray)): # check if multple collumns
                dfNew = dfNew[['DATE','TIME']+columnNames] # combine date and time with columns to keep
            else:
                dfNew = dfNew[['DATE', 'TIME'] + [columnNames]]  # combine date and time with columns to keep
        else: # otherwise, if the indices of the columnss
            if isinstance(columnNames, (list, tuple, np.ndarray)):  # check if multple collumns
                dfNew = dfNew[[1,2] + columnNames]
            else:
                dfNew = dfNew[[1, 2] + [columnNames]]

    if np.all(useNames!=None):
        if isinstance(useNames, (list, tuple, np.ndarray)):  # check if multple collumns
            dfNew.columns = [['DATE','TIME']+useNames] # add date and time to the column names
        else:
            dfNew.columns = [['DATE', 'TIME'] + [useNames]]  # add date and time to the column names
            '''
    df = processInputDataFrame(df, columnNames, useNames, dateColumnName, dateColumnFormat, timeColumnName, timeColumnFormat, utcOffsetValue, utcOffsetUnit, dst)
    '''
    from datetime import datetime
    dt = [datetime(1,1,1)]*x_df.shape[0]
    for i in  range(x_df.shape[0]):
        # convert the Date from csv to datetime
        dt[i] = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(x_df.DATE[i]) - 2)
        # calculate the time and add to datetime
        a, second = divmod(x_df.TIME[i]*86400,60) # 24*60*60 = 86400
        hour, minute = divmod(a, 60)
        #hour = (x_df.TIME[i]*24)//1
        #minute = (x_df.TIME[i]*24*60-hour*60)//1
        #second = abs(x_df.TIME[i]*24*3600-hour*3600-minute*60)//1
        dt[i] = dt[i].replace(hour=int(hour),minute=int(minute),second=int(second))
    '''

    return df

