import pandas as pd
import ast
from datetime import datetime, timedelta
from pymongo import MongoClient
import mongodb_connection
import matplotlib.pyplot as plt
import copy
from pandas.plotting import register_matplotlib_converters

"""@package docstring
Import Messprotokoll

Importiere Messprotokolle aus übergebenen Pfad, bereite die Daten auf und speichere sie in einem Panda-Dataframe 
"""
def importMessprotokoll(path):
    df = pd.read_csv(path, sep=';')
    df.rename(columns=lambda x: x.strip(), inplace=True)
    df["Measured"] = df["Measured"].apply(lambda x: float(str(x).replace(',','.')))
    df["Setpoint"] = df["Setpoint"].apply(lambda x: float(str(x).replace(',','.')))
    df["Difference"] = df["Difference"].apply(lambda x: float(str(x).replace(',','.')))
    columnsToStrip = ["Program", "Plane", "Measuring variant","Results:", "Unit"]
    for curColumn in columnsToStrip:
        df[curColumn] = df[curColumn].apply(lambda x: x.strip())
    return df

"""@package docstring
Import Achsleistungen/Messdaten

Importiere Achsleistungen, Messdaten aus übergebenen Pfad, bereite die Daten auf und speichere sie in einem Panda-Dataframe 
"""
def importAchsleistungCSV(path):
    return pd.read_csv(path, sep=';')

def importMessDatasetCSV(path):
    return pd.read_csv(path, sep=',', header=6)

"""@package docstring
Import JSONExport

Importiere die zuvor exportieren JSON-Dateien und speichere die Spalten "_id", "timeStamp", "valuesStatus", "values_number", und "timeStampMqttClient" in einem Panda-Dataframe
für Tabelle values und values_actual.
"""
def importJSONExport(path):
    df = pd.read_json(path,orient="records", lines=True)
    df["_id"] = df["_id"].apply(lambda x: x["$oid"])
    df["timeStamp"] = df["timeStamp"].apply(lambda x: x["$date"]).apply(lambda x: x["$numberLong"]).apply(int)
    df["valueStatus"] = df["valueStatus"].apply(lambda x: x["$numberInt"])
    if "value_number" in df.columns:
        df["value_number"] = df["value_number"].apply(lambda x: list(x.values())[0])
    df["timeStampMqttClient"] = df["timeStampMqttClient"].apply(lambda x: x["$date"]).apply(lambda x: x["$numberLong"])
    return df

"""@package docstring
Import JSONExport

Importiere die zuvor exportieren JSON-Dateien und speichere die Spalten "_id", "timeStamp", "valuesStatus", "values_number", und "timeStampMqttClient" in einem Panda-Dataframe
für Tabelle values_ncprogram
"""
def importJSONExportNCProg(path):
    return 0

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
Load Reibdaten from Mongo-DB

Hole dir via MongoDB-Client den Datensatz der Reibe im übergebenen Zeitrahmen (tsStart, tsEnd (beides datetime)) und spiele diese in ein Panda-Dataframe und geb dieses Dataframe 
zurück
"""
def loadReibdatenFromMongoDB(tsStart,tsEnd):
    client = MongoClient(mongodb_connection.connectionstring)
    db = client.DMG_CELOS_MOBILE_V3_CA
    collection = db["values_ncprogram"]
    cursor = collection.find({
        'timeStamp' : {'$gt':tsStart, '$lt':tsEnd},
        'toolNo' : 'RA_12H7' # $gt: greater than, $lt: less than
    }).batch_size(10000)
    df = pd.DataFrame(columns=['_id','ValueID','value','timeStamp','progName','toolNo'])
    i = 0
    for item in cursor:
        df.loc[i] = [item['_id'],item['ValueID'],item['value_number'],item['timeStamp'], item['progName'],item['toolNo']]
        if i%10000 == 0:
            print(i,end=', ')
        i=i+1
        
    return df

"""@package docstring
Load all Data for a specified from Mongo-DB

Hole dir via MongoDB-Client alle Daten der Maschine im übergebenen Zeitrahmen (tsStart, tsEnd (beides datetime)) und spiele diese in ein Panda-Dataframe 
und geb dieses Dataframe zurück
"""
def loadTimeframeFromMongoDB(tsStart = datetime(2019,11,26,12,15), tsEnd = datetime(2019,11,26,13,10)):
    client = MongoClient(mongodb_connection.connectionstring)
    db = client.DMG_CELOS_MOBILE_V3_CA
    collection = db["values"]
    cursor = collection.find({
            'timeStamp' : {'$gt':tsStart, '$lt':tsEnd} # $gt: greater than, $lt: less than
            })
    df = pd.DataFrame(columns=['_id','ValueID','value','timeStamp'])
    i = 0
    for item in cursor:
        df.loc[i] = [item['_id'],item['ValueID'],item['value_number'],item['timeStamp']]
        i+=1
        
    return df

"""@package docstring
Plotte die Daten der Z-Achse

Plotte via Matplotlib einen zeitlichen Verlauf der Z-Achse der Maschine in Abhängigkeit der ID
"""
def plotSpecificIDs(idList, df, tsStart = datetime(2019,11,26,12,0), tsEnd = datetime(2019,11,26,23,35)):
    fig = plt.figure(figsize=(15, 5), dpi=80)
    plt.plot(df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp']) & (l['timeStamp'] < tsEnd), 'value'], c='r')
    for id in idList:
        plt.scatter(df.loc[lambda l: (l['ValueID']==id) & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],df.loc[lambda l: (l['ValueID']==id) & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "value"], s=1)
    plt.legend(["12430012063.Z1_Axis.Actual_Position_MCS"]+idList)
    plt.show()
    fig.savefig('Plot_Bilder/plotSpecificIDs.png', dpi=fig.dpi)
    
"""@package docstring
Plotte die Daten der Z-Achse

Plotte via Matplotlib einen zeitlichen Verlauf der Z-Achse der Maschine
"""
def plotActualZ1(df, tsStart = datetime(2019,11,26,12,0), tsEnd = datetime(2019,11,26,23,35), saveFile=True):
    register_matplotlib_converters()
    fig = plt.figure(figsize=(15, 5), dpi=80)
    plt.plot(df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp']) & (l['timeStamp'] < tsEnd), 'value'], c='r')
    plt.scatter(df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp']) & (l['timeStamp'] < tsEnd), 'value'], c='b',s=1.0)
    plt.legend(["12430012063.Z1_Axis.Actual_Position_MCS","12430012063.Z1_Axis.Actual_Position_MCS"])
    plt.show()
    if saveFile:
        fig.savefig('Plot_Bilder/plotActualZ1.png', dpi=fig.dpi)

"""@package docstring
Approximiere Values zwischen minValue und maxValue in bestimmten Zeitintervallen
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
Approximiere Values zwischen minValue und maxValue in bestimmten Zeitintervallen in unterschiedlichen Schritten
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

"""@package docstring
Lade Measurement-Daten aus csv-Datei und baue daraus ein Pandas-Dataframe
"""
def importMeasurementData(path='csv_Files/MEAS_PROTOCOL_CSV_E1.CSV'):
    df = pd.read_csv(path, sep=';')
    df.rename(columns={'      Date': 'Date', 
                       '    Time': 'Time', 
                       '                         Program': 'Program',
                       ' Workpiece no.': 'Workpiece no.', 
                       '     Testpoint': 'Testpoint', 
                       '     Probe no.': 'Probe no.',
                       '         Cycle': 'Cycle', 
                       '        S_MVAR': 'S_MVAR', 
                       '               Measuring variant': 'Measuring variant',
                       'Results:    ': 'Results', 
                       '      Setpoint': 'Setpoint', 
                       '      Measured': 'Measured', 
                       '    Difference': 'Difference'}, inplace=True)
    return df
    
"""@package docstring
Lade Achsleistungs-Daten aus csv-Datei und baue daraus ein Pandas-Dataframe
"""
def importAchsleistungsData(path='csv_Files/Achsleistung-2019-11-20T10-27-03_E1.csv'):
    df = pd.read_csv(path, sep=';')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df

"""@package docstring
Nehme ein Pandas-Dataframe und den Namen einer Spalte, ersetzte die Inhalte der Spalte und gebe das DataFrame zurück
"""
def transformStringListToFloatList(df, columnName):
    list = df[columnName].tolist()
    list = [float(i.strip().strip("'").replace(',', '.')) for i in list]
    df[columnName] = list
    return df
    