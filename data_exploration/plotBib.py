import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters


"""@package docstring
Scatterplots the data for the Z1-Axis and the given ValueIDs over the timeframe.
Optionally, saves the plot under savePath.
The Dataframe dfData is expected to have a column 'timeStamp, which is used for the Y-Axis
"""
def plotSpecificIDs(idList, dfData, tsStart, tsEnd, savePath=None):
    register_matplotlib_converters()
    fig = plt.figure(figsize=(15, 5), dpi=80)
    plt.plot(dfData.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],dfData.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp']) & (l['timeStamp'] < tsEnd), 'value'], c='r')
    for id in idList:
        plt.scatter(dfData.loc[lambda l: (l['ValueID']==id) & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],dfData.loc[lambda l: (l['ValueID']==id) & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "value"], s=1)
    plt.legend(["12430012063.Z1_Axis.Actual_Position_MCS"]+idList)
    plt.show()
    if savePath is not None:
        fig.savefig(savePath, dpi=fig.dpi)


"""@package docstring
Plotte the data for the Z1-Axis over the timeframe.
Optionally, saves the plot under savepath.
"""
def plotActualZ1(df, tsStart, tsEnd, savePath=None):
    register_matplotlib_converters()
    fig = plt.figure(figsize=(15, 5), dpi=80)
    plt.plot(df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp']) & (l['timeStamp'] < tsEnd), 'value'], c='r')
    plt.scatter(df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp'])& (l['timeStamp'] < tsEnd), "timeStamp"],df.loc[lambda l: (l['ValueID']=="12430012063.Z1_Axis.Actual_Position_MCS") & (tsStart < l['timeStamp']) & (l['timeStamp'] < tsEnd), 'value'], c='b',s=1.0)
    plt.legend(["12430012063.Z1_Axis.Actual_Position_MCS","12430012063.Z1_Axis.Actual_Position_MCS"])
    plt.show()
    if savePath is not None:
        fig.savefig(savePath, dpi=fig.dpi)