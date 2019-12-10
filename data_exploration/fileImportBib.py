import pandas as pd

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
Lade Measurement-Daten aus csv-Datei und baue daraus ein Pandas-Dataframe
"""
def importMeasurementData(path='csv_Files/MEAS_PROTOCOL_CSV_E1.CSV'):
    df = pd.read_csv(path, sep=';')
    return df
    
"""@package docstring
Lade Achsleistungs-Daten aus csv-Datei und baue daraus ein Pandas-Dataframe
"""
def importAchsleistungsData(path='csv_Files/Achsleistung-2019-11-20T10-27-03_E1.csv'):
    df = pd.read_csv(path, sep=';')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df