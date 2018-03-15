#Project: GBS Tool
# Author: Dr. Marc Mueller-Stoffels, marc@denamics.com, denamics GmbH
# Date: January 16, 2018
# License: MIT License (see LICENSE file of this package for more information)

# Contains the main flow of the optimization as it is to be called from the GBSController.

from GBSAnalyzer.DataRetrievers.getDataSubsets import getDataSubsets

class optimize:
    '''
    TODO: document this
    '''

    def __init__(self, projectName, searchArgs):
        '''
        Constructor
        TODO: implement

        :param projectName: [String] name of the project, used to locate project folder tree within the GBSProject
            folder structure
        :param searchArgs: [Array of strings] parameters defining the search objectives and methods to be used.
            searchArgs[0]: searchMethod used to determine which search algorithm to dispatch. Currently implemented is
            'simulatedAnnealing'.
            searchArgs[1]: optimizationObjective TODO define this. It should allow blending of objectives.
        '''

        # Setup key parameters
        self.projectName = projectName
        self.searchMethod = searchArgs[0]

        # Retrieve data from base case
        # TODO: implement retrieving data from base case
        self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP = self.getBasecase()

        # Calculate boundaries for optimization search
        self.minESSPPa, self.maxESSPPa, self.minESSEPa, self.maxESSEPa = \
            self.getOptimizationBoundaries('variableSRC', self.time, self.firmLoadP, self.varLoadP, self.firmGenP, self.varGenP, otherConstraints=None)

        # Get the short test time-series
        # assemble input dataframe
        df = []
        self.abbrevDatasets, self.abbrevDatasetWeights = getDataSubsets(df, method=[])

        # Setup optimization runs
        # Branch based on input from 'searchArgs'
        # NOTE: we need to get the KPI for the base case somewhere here to compare results against
        if self.searchMethod == 'simulatedAnnealing':
            # call simualtedAnnealing functions
            a = 0
        # FUTUREFEATURE: add further optimization methods here
        else:
            raise ValueError('Unknown optimization method, %s, selected.' % searchArgs[0])






    def getBasecase(self):
        '''
        Retrieve base case data and meta data required for initial estimate.
        :return time: [Series] time vector
        :return firmLoadP: [Series] firm load vector
        :return varLoadP: [Series] variable (switchable, manageable, dispatchable) load vector
        :return firmGenP: [Series] firm generation vector
        :return varGenP: [Series] variable generation vector
        '''
        # Empty bins
        time = []
        firmLoadP = []
        varLoadP = []
        firmGenP = []
        varGenP = []
        
        # Read project meta data to get (a) all loads, (b) all generation, and their firm and variable subsets.

        # Retrieve data channels

        return time, firmLoadP, varLoadP, firmGenP, varGenP


    def getOptimizationBoundaries(self, SRCMethod, time, firmLoadP, varLoadP, firmGenP, varGenP, otherConstraints):
        '''
        Determines the search space for the optimization using methods contained in initEstimate

        :param SRCMethod: [String] sets the SRC calculation method used from initEstimate.
        :param otherConstraints:
        :return:
        '''

        minESSPPa = 0
        maxESSPPa = 0
        minESSEPa = 0
        maxESSEPa = 0

        return minESSPPa, maxESSPPa, minESSEPa, maxESSEPa