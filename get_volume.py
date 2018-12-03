import pandas as pd
import numpy as np
import utils

def get_volume(dict_tradingParam, df_buyVolume, df_sellVolume, df_execPriceReturn, lotSize):
    if utils.getParameter(dict_tradingParam, 'canTradeOnSuspend', 0) > 0:
        df_buyVolume[df_buyVolume < 1] = np.inf
        df_sellVolume[df_sellVolume < 1] = np.inf
    riseLimitThreshold = utils.getParameter(dict_tradingParam, 'RiseLimitThres', 0)
    if riseLimitThreshold > 0:
        riseLimit = df_execPriceReturn > riseLimitThreshold
        df_buyVolume[riseLimit] = 0
        df_sellVolume[riseLimit & (df_sellVolume > 0)] = np.inf
    fallLimitThreshold = utils.getParameter(dict_tradingParam, 'FallLimitThres', 0)
    if fallLimitThreshold < 0:
        fallLimit = df_execPriceReturn < fallLimitThreshold
        df_buyVolume[fallLimit & (df_buyVolume > 0)] = np.inf
        df_sellVolume[fallLimit] = 0
    volumeLimitPct = utils.getParameter(dict_tradingParam, 'VolumeLimitPct', 0)
    if volumeLimitPct > 0:
        df_buyVolume = df_buyVolume * volumeLimitPct
        df_sellVolume = df_sellVolume * volumeLimitPct
    else:
        df_buyVolume[df_buyVolume > 0] = np.inf
        df_sellVolume[df_sellVolume > 0] = np.inf
    df_buyVolume = utils.roundToLot(df_buyVolume, lotSize)
    df_sellVolume = utils.roundToLot(df_sellVolume, lotSize)

    return (df_buyVolume, df_sellVolume)