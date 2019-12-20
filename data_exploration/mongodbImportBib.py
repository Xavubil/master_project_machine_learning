import pandas as pd
from datetime import datetime, timedelta
import mongodb_connection
from pymongo import MongoClient


def countInValues(tsStart, tsEnd, ValueIDFilter=None):
    client = MongoClient(mongodb_connection.connectionstring)
    db = client.DMG_CELOS_MOBILE_V3_CA
    collection = db["values"]
    if ValueIDFilter is not None:
        mdbQuery = {'timeStamp' : {'$gt' : tsStart, '$lt' : tsEnd}, "ValueID" : {"$in" : ValueIDFilter } }
    else:
        mdbQuery = {'timeStamp' : {'$gt' : tsStart, '$lt' : tsEnd}}
    return collection.count_documents(mdbQuery)
    

def countInNCProgram(tsStart, tsEnd):
    client = MongoClient(mongodb_connection.connectionstring)
    db = client.DMG_CELOS_MOBILE_V3_CA
    collection = db["values_ncprogram"]
    mdbQuery = {'timeStamp' : {'$gt' : tsStart, '$lt' : tsEnd}, 'toolNo' : 'RA_12H7'}
    return collection.count_documents(mdbQuery)

"""@package docstring
Load Reibdaten of the specified timeframe from Mongo-DB into a dataframe, with columns [_id, ValueID, value, timeStamp, progrName, toolNo]

Hole dir via MongoDB-Client den Datensatz der Reibe im übergebenen Zeitrahmen (tsStart, tsEnd (beides datetime)) und spiele diese in ein Panda-Dataframe und geb dieses Dataframe 
zurück
"""
def loadReibdaten_ncprogram(tsStart,tsEnd, verbose=False):
    client = MongoClient(mongodb_connection.connectionstring)
    db = client.DMG_CELOS_MOBILE_V3_CA
    collection = db["values_ncprogram"]

    mdbQuery = {'timeStamp' : {'$gt' : tsStart, '$lt' : tsEnd}, 'toolNo' : 'RA_12H7'}
    totalDocNumber = collection.count_documents(mdbQuery)

    cursor = collection.find(mdbQuery).batch_size(10000)
    df = pd.DataFrame(columns=['_id','ValueID','value','timeStamp','progName','toolNo'])
    i = 0
    for item in cursor:
        df.loc[i] = [item['_id'],item['ValueID'],item['value_number'],item['timeStamp'], item['progName'],item['toolNo']]
        if verbose and i%1000 == 0:
            print(str(i)+"/"+str(totalDocNumber),end='; ')
        i=i+1
        
    return df


"""@package docstring
Load all Data of the specified timeframe from values into a dataframe, with columns [_id, ValueID, value, timeStamp]
Takes optionally a list of ValueIDs, that should be loaded, while ignoring other ValueIDs

Hole dir via MongoDB-Client alle Daten der Maschine im übergebenen Zeitrahmen (tsStart, tsEnd (beides datetime)) und spiele diese in ein Panda-Dataframe 
und geb dieses Dataframe zurück
"""
def loadAll_values(tsStart, tsEnd, ValueIDFilter=None, verbose=False):
    client = MongoClient(mongodb_connection.connectionstring)
    db = client.DMG_CELOS_MOBILE_V3_CA
    collection = db["values"]

    mdbQuery = {}
    if ValueIDFilter is not None:
        mdbQuery = {'timeStamp' : {'$gt' : tsStart, '$lt' : tsEnd}, "ValueID" : {"$in" : ValueIDFilter } }
    else:
        mdbQuery = {'timeStamp' : {'$gt' : tsStart, '$lt' : tsEnd}}
    
    totalDocCount = collection.count_documents(mdbQuery)

    cursor = collection.find(mdbQuery)
    df = pd.DataFrame(columns=['_id','ValueID','value','timeStamp'])
    i = 0
    for item in cursor:
        df.loc[i] = [item['_id'],item['ValueID'],item['value_number'],item['timeStamp']]
        if verbose and i%1000 == 0:
            print(str(i)+"/"+str(totalDocCount),end=";")
        i+=1
        
    return df