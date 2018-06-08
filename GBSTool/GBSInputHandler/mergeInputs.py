# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 16:59:08 2018

@author: tcmorgan2
"""

import numpy as np
from GBSInputHandler.readDataFile import readDataFile
# CONSTANTS
YEARSECONDS = 31536000 # seconds in a non-leap Year
#reads input files and merges them into a single dataframe
#input dictionary must contain a fileLocation attribute, fileType, headerNames, newHeaderNames, componentUnits,
#Dictionary->DataFrame, List
def mergeInputs(inputDictionary):

    # iterate through all sets of input files
    for idx in range(len(inputDictionary['fileLocation'])):
        df0, listOfComponents0 = readDataFile(inputDictionary['fileType'][idx],inputDictionary['fileLocation'][idx],inputDictionary['fileType'][idx],
                                             inputDictionary['headerNames'][idx],inputDictionary['newHeaderNames'][idx],inputDictionary['componentUnits'][idx],
                                             inputDictionary['componentAttributes'][idx], 
                                             inputDictionary['dateColumnName'][idx], inputDictionary['dateColumnFormat'][idx], 
                                             inputDictionary['timeColumnName'][idx], inputDictionary['timeColumnFormat'][idx], 
                                             inputDictionary['utcOffsetValue'][idx], inputDictionary['utcOffsetUnit'][0], 
                                             inputDictionary['dst'][idx]) # dataframe with time series information. replace header names with column names
        if idx == 0: # initiate data frames if first iteration, otherwise append
            df = df0
            listOfComponents = listOfComponents0
        else:
            # check if on average more than a year difference between new dataset and existing
            meanTimeNew = np.mean(df0.DATE)
            meanTimeOld = np.mean(df.DATE)
            # round to the nearest number of year difference
            yearDiff = np.round((meanTimeNew - meanTimeOld) / YEARSECONDS)
            # if the difference is greater than a year between datasets to be merged, see if can change the year on one
            if abs(yearDiff) >= 0:
                # if can change the year on the new data
                if inputDictionary['flexibleYear'][idx]:
                    # find the number of years to add or subtract
                    df0.DATE = df0.DATE - yearDiff*YEARSECONDS
                # otherwise, check if can adjust the existing dataframe
                elif all(inputDictionary['flexibleYear'][:idx]):
                    df.DATE = df.DATE + yearDiff*YEARSECONDS
    
            df = df.append(df0)
            listOfComponents.extend(listOfComponents0)
    
    # order by datetime
    df = df.sort_values(['DATE']).reset_index(drop=True)
    # find rows with identical dates and combine rows, keeping real data and discarding nans in columns
    dupDate = df.DATE[df.DATE.duplicated()]
    
    for date in dupDate: # for each duplicate row
        # find with same index
        sameIdx = df.index[df.DATE == date]
        # for each column, find first non-nan value, if one
        for col in df.columns:
            # first good value
            goodIdx = df.loc[sameIdx,col].first_valid_index()
            if goodIdx != None:
                df.loc[sameIdx[0], col]= df.loc[goodIdx, col]
        # remove duplicate columns
        df = df.drop(sameIdx[1:])
     # remove duplicates in list of components   
    #listOfComponents = list(set(listOfComponents)))
    return df, listOfComponents