import pandas as pd
import numpy as np

def return_cal(df_portfolioValue,df_holdings,df_markToMarketPrice,tradeDates,initHldValue,df_turnoverPct,share_codes):
    df_portfolioValue.ix[:, 0] = (df_holdings * df_markToMarketPrice.ix[tradeDates]).sum(axis=1)
    df_weights = (df_holdings * df_markToMarketPrice.ix[tradeDates]).div(df_portfolioValue.ix[:,0], axis=0)
    df_cumRets = df_portfolioValue / initHldValue - 1
    df_cumRets = df_cumRets[share_codes]
    df_singlePeriodRets = df_portfolioValue/ df_portfolioValue.shift(1) - 1
    df_singlePeriodRets.ix[0,0] = df_portfolioValue.ix[0, 0] / initHldValue - 1
    df_singlePeriodRets = df_singlePeriodRets[share_codes]

    result = {}
    result['Holding'] = df_holdings.replace(0, np.nan)
    result['PortfolioValue'] = df_portfolioValue
    result['Weights'] = df_weights.replace(0, np.nan)
    result["SinglePeriodReturn"] = df_singlePeriodRets
    result["CumulativeReturn"] = df_cumRets
    result["Turnover"] = df_turnoverPct
    return result