import re

def toInt(val):
    if val == "":
        return 0
    try:
        return int(val)
    except:
        return 0


def inputToMinutes(inputString):
    # Pass in string in hours format, get integer minutes back.
    #
    # 1 = 60 minutes
    # 1:00 = 60 minutes
    # 1:15 = 75 minutes
    # 1.15 = 75 minutes
    # 1:30 = 90 minutes
    # 1.30 = 90 minutes
    # 0.15 = 15 minutes
    # 0:15 = 15 minutes
    # :15 = 15 minutes
    # .25 = 15 minutes    
    hours = 0
    minutes = 0
    # decimal = 0
    if (":" in inputString) or ("." in inputString):
        parts = re.split("[:.]",inputString) #inputString.split(":")
        hours = toInt(parts[0])
        minutes = toInt(parts[1])
    else:
        hours = toInt(inputString)
    return hours * 60 + minutes # + decimal * 60
