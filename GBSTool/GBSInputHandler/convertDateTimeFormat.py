def convertDateTimeFormat(f):
    '''converts a string date or time format to a python date or time format to be used in to_datetime
    :param f [string] string date or time format'''

    sep = ' '
    if len(f.split('/')) >1:
        sep = '/'
    elif len(f.split('-'))>1:
        sep = '-'
    elif len(f.split(':'))>1:
        sep = ':'
    # f = f.replace('mmm','b').replace('mm','m')\
    #     .replace('dd','d').replace('yyyy','Y')\
    #     .replace('yy','y')\
    #     .replace('hh','H')\
    #     .replace('ss','s')\
    #     .replace('MM','M')\
    #     .split(sep)

    f = list(map(doubleToSingle,f.split(sep)))
    return sep.join(map('%{0}'.format, f))

def doubleToSingle(d):
    return d[0]
