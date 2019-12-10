"""@package docstring
Join X/Y-Daten via TimeStamp

Führe X- und Y-Koordinaten aus dem values/values_actual-JSON-File über ihre Timestamp zusammen
"""
def joinByBinnedTimestampXY(dataframe, timeStampBin=2):
    dfX = dataframe.loc[lambda x: x["ValueID"]=="12430012063.X1_Axis.Actual_Position_MCS", ["ValueID","value","timeStamp"]].sort_values(by=["timeStamp"])
    dfY = dataframe.loc[lambda x: x["ValueID"]=="12430012063.Y1_Axis.Actual_Position_MCS", ["ValueID", "value","timeStamp"]].sort_values(by=["timeStamp"])
    #bin
    dfX['timeStamp'] = dfX['timeStamp'].apply(lambda x: int(x)-(int(x)%(10**timeStampBin)))
    dfY['timeStamp'] = dfY['timeStamp'].apply(lambda x: int(x)-(int(x)%(10**timeStampBin)))
    #group
    dfX = dfX.groupby(by="timeStamp").mean()
    dfX.rename(columns={"value":"X"}, inplace = True)
    dfY = dfY.groupby(by="timeStamp").mean()
    dfY.rename(columns={"value":"Y"}, inplace=True)
    #join
    joined = dfX.join(dfY, how='inner')
    joined.reset_index(inplace = True)
    return joined


"""@package docstring
Approximiere einen Zeitintervall, in dem die Z1-Werte des übergebenen 
DataFrames dfParent im Rahmen des minValue und maxValue bleiben.
Die Methode verwendet dabei deltaTime-große Schritte zur Annäherung; 
in dem zurückgegebenen Zeitabschnitt start bis end werden die Grenzwerte nicht über- / unterschritten
"""
def approxRange(dfParent,start,end,minValue,maxValue,deltaTime):
    valueID_Z1 = "12430012063.Z1_Axis.Actual_Position_MCS"
    newStart = copy.deepcopy(start)
    newEnd = copy.deepcopy(end)
    tempDF = dfParent.loc[lambda d: (d["ValueID"] == valueID_Z1) & (start < d["timeStamp"]) & (d["timeStamp"] < end)]
    
    #approx. start of frame
    runAtLeastOnce = False
    while minValue < tempDF.loc[:,"value"].min() and tempDF.loc[:,"value"].max() < maxValue:
        newStart = newStart - deltaTime
        tempDF = dfParent.loc[lambda l: (l["ValueID"] == valueID_Z1) & (newStart < l["timeStamp"]) & (l["timeStamp"] < newEnd)]
        runAtLeastOnce = True
    
    if runAtLeastOnce:
        newStart = newStart + deltaTime
    tempDF = dfParent.loc[lambda l: (l["ValueID"] == valueID_Z1) & (newStart < l["timeStamp"]) & (l["timeStamp"] < newEnd)]
    
    #approx. end of frame
    runAtLeastOnce = False
    while minValue < tempDF.loc[:,"value"].min() and tempDF.loc[:,"value"].max() < maxValue:
        newEnd = newEnd + deltaTime
        tempDF = dfParent.loc[lambda l: (l["ValueID"] == valueID_Z1) & (newStart < l["timeStamp"]) & (l["timeStamp"] < newEnd)]
        runAtLeastOnce = True
    
    if runAtLeastOnce:
        newEnd = newEnd - deltaTime
    
    return newStart, newEnd

"""@package docstring
Approximiert einen Zeitintervall, in dem die Z1-Werte des übergebenen DataFrames
dfParent im Rahmen der Werte des initialen Zeitabschnittes bleiben. Die Toleranz gibt den 
Puffer dieser Min- und Max-Werte an. deltaTimes gibt eine absteigend sortierte 
Liste an Schrittweiten an, die dabei verwendet wird.
"""
def approxRangeInSteps(dfParent,initialStart,initialEnd,deltaTimes=[timedelta(minutes=5),timedelta(seconds=30),timedelta(seconds=5),timedelta(seconds=1)],sampleTolerance=5):
    valueID_Z1 = "12430012063.Z1_Axis.Actual_Position_MCS"
    start = initialStart
    end = initialEnd
    tempDF = dfParent.loc[lambda d: (d["ValueID"] == valueID_Z1) & (start < d["timeStamp"]) & (d["timeStamp"] < end)]
    minValue = tempDF.loc[:,"value"].min() - sampleTolerance
    maxValue = tempDF.loc[:,"value"].max() + sampleTolerance
    print("Min. sampled value: "+str(minValue))
    print("Max. sampled value: "+str(maxValue))
    for dT in deltaTimes:
        start, end = approxRange(dfParent,start,end,minValue,maxValue,dT)
    return start,end 