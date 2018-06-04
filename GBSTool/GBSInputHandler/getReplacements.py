
# TODO PERFORMANCE  slowest part of module because iterates through every missing interval
# dataframe, list of indices, string -> Boolean
# returns true if a replacement was made, false if it was not
def getReplacement(df, indices, component=None):
    import logging
    import pandas as pd
    from fixBadData import linearFix, dataReplace

    # index,range in same units as index, dataframe, dataframe, index
    def getReplacementStart(dtStart, timeRange, entiredf, missingdf, directMatch=None):
        # if there is a match then stop looking,
        # otherwise increment the search window by a year and look again
        # start is the index of our first missing record
        start = min(missingdf.index)
        # searchBlock is the portion of the dataframe that we will search for a match in
        searchBlock = entiredf.loc[dtStart: dtStart + timeRange]
        # restrict the search to only matching days of the week and time of day
        searchBlock = searchBlock[(searchBlock.index.to_datetime().dayofweek == start.dayofweek)]
        searchBlock = searchBlock.between_time((start + pd.Timedelta(hours=3)).time(),
                                               (start - pd.Timedelta(hours=3)).time())

        # find the match in the searchBlock as long as it isn't empty
        if not searchBlock.empty:
            # order by proximity

            searchBlock['newtime'] = pd.Series(searchBlock.index.to_datetime(), searchBlock.index).apply(
                lambda dt: dt.replace(year=start.year))

            searchBlock['timeapart'] = searchBlock['newtime'] - start
            sortedSearchBlock = searchBlock.sort_values('timeapart')
            # if replacment is long enough return indices, otherwise move on
            blockLength = entiredf[min(sortedSearchBlock.index):max(sortedSearchBlock.index)][::-1].rolling(
                len(missingdf)).count()[::-1]

            # a matching record is one that is the same day of the week, similar time of day and has enough
            # valid records following it to fill the empty block

            directMatch = blockLength[blockLength == len(missingdf)].first_valid_index()
        # move the search window to the following year
        dtStart = dtStart + pd.DateOffset(years=1)
        searchBlock = entiredf[dtStart: dtStart + timeRange]
        # if we found a match return its index otherwise look again
        if directMatch is not None:
            return directMatch
        elif searchBlock.empty:
            # if theere is no where left to search return false
            return False
        else:
            # keep looking on the remainder of the list
            return getReplacementStart(dtStart, timeRange, entiredf[component], missingdf[component], directMatch)

    # dataframe, index, dataframe, string -> null
    # replaces a block of data and logs the indeces as bad records
    def replaceRecords(entiredf, dtStart, missingdf, strcomponent):
        window = len(missingdf)
        # TODO what is the shape of replacement if component is a list?
        replacement = entiredf[dtStart:][0:window]
        addin = " scaled values from "
        dataReplace(entiredf, missingdf, replacement, strcomponent)

        logging.info("replaced inline values %s through %s with %s %s through %s."
                     % (str(min(missingdf.index)), str(max(missingdf.index)), addin, str(min(replacement.index)),
                        str(max(replacement.index))))
        return

    # dataframe -> index, timedelta
    # returns the a window of time that should be searched for replacement values depending on the
    # amount of time covered in the missing block
    def getMoveAndSearch(missingdf):

        # for large missing blocks of data we use a larger possible search range
        if (missingdf.index.max(0) - missingdf.index.min(0)) >= pd.Timedelta('1 days'):
            initialMonths = 2
            timeRange = pd.DateOffset(months=4)
        else:
            initialMonths = 1
            timeRange = pd.DateOffset(weeks=8)
        # start is the missingblock minus a year and the searchrange
        dtStart = missingdf.index[0] - pd.DateOffset(years=1, months=initialMonths, days=14)
        return dtStart, timeRange

    # get the block of missing data
    missingBlock = df.loc[indices]
    # search start is datetime indicating the start of the block of data to be searched
    # searchRange indicates how big of a block of time to search
    searchStart, searchRange = getMoveAndSearch(missingBlock)

    # replacementStart is a datetime indicating the first record in the block of replacementvalues
    replacementStart = getReplacementStart(searchStart, searchRange, df, missingBlock)
    if replacementStart:
        # replace the bad records
        replaceRecords(df, replacementStart, missingBlock, component)
        return True
    elif len(missingBlock) <= 15:
        # if we didn't find a replacement and its only a few missing records us linear estimation
        index_list = missingBlock.index.tolist()
        linearFix(index_list, df, component)
        logging.info("No similar data subsets found. Using linear interpolation to replace inline values %s through %s."
                     % (str(min(missingBlock.index)), str(max(missingBlock.index))))
        return True
    else:
        logging.info(
            "could not replace values %s through %s." % (str(min(missingBlock.index)), str(max(missingBlock.index))))
        return False




