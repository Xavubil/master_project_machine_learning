import pandas as pd
import ast
from datetime import datetime

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

def importMessDatasetCSV(path):
    return pd.read_csv(path, sep=',', header=6)

# für Tabelle values und values_actual
def importJSONExport(path):
    df = pd.read_json(path,orient="records", lines=True)
    df["_id"] = df["_id"].apply(lambda x: x["$oid"])
    df["timeStamp"] = df["timeStamp"].apply(lambda x: x["$date"]).apply(lambda x: x["$numberLong"])
    df["valueStatus"] = df["valueStatus"].apply(lambda x: x["$numberInt"])
    df["value_number"] = df["value_number"].apply(lambda x: list(x.values())[0])
    df["timeStampMqttClient"] = df["timeStampMqttClient"].apply(lambda x: x["$date"]).apply(lambda x: x["$numberLong"])
    return df

# für Tabelle values_ncprogram
def importJSONExportNCProg(path):
    return 0

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
    return joined