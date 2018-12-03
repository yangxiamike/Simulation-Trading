import numpy as np

def getParameter(dict_parm, parmName, defaultValue):
    if parmName in dict_parm:
        return dict_parm[parmName]
    else:
        return defaultValue

def roundToLot(dataframe, lotSize):
    if lotSize >0:
        dataframe = dataframe.fillna(0)
        return np.sign(dataframe) * np.floor(np.round(np.abs(dataframe)) / max(1.,lotSize))
        print(dataframe)
    else:
        return dataframe

def fillHolding(d, nextd, tradeDates, df_holdings, df_totalReturnFactor):
    if nextd>d:
        holdingDates = tradeDates[(tradeDates>=d) & (tradeDates<=nextd)]
        df_holdings.ix[holdingDates] = np.tile(df_holdings.ix[d], (len(holdingDates), 1))
        df_holdings.ix[holdingDates] = df_holdings.ix[holdingDates] * (df_totalReturnFactor.ix[holdingDates] / df_totalReturnFactor.ix[d])
    return df_holdings

def get_date(initialHolding,df_markToMarketPrice,endDate):
    beginDate = initialHolding.index[0]
    allDates = df_markToMarketPrice.index
    endDate = allDates[allDates <= endDate][-1]
    tradeDates = allDates[(allDates >= beginDate) & (allDates <= endDate)]

    if len(allDates[(allDates >= beginDate) & (allDates <= endDate)]) < 1:
        raise ValueError('no trading date falls between begindate and enddate')
    if beginDate > endDate:
        raise ValueError('beginDate should be less than endDate')
    return (beginDate,endDate,tradeDates)


def reb_target_portfo(df_targetPortfolioWgt):
    """
    param: df_targetPortfolioWgt
    return: rebalance dates
            signalDates
            df_targetPortfolioWgt(rebalanced)
    """
    if (df_targetPortfolioWgt < 0).any(axis=1).any():
        raise ValueError('Stock price should not be less than 0')
    if (round(df_targetPortfolioWgt.sum(axis=1), 4) > 1).any():
        raise ValueError('Total Weight is greater than 1')
    df_targetPortfolioWgt = df_targetPortfolioWgt.dropna(axis=[0, 1], how='all')
    sigDates = df_targetPortfolioWgt.index
    rebDates = sigDates
    rebDates = rebDates[(rebDates >= beginDate) & (rebDates <= endDate)]
    df_targetPortfolioWgt = df_targetPortfolioWgt.ix[rebDates]

    return (df_targetPortfolioWgt, rebDates, sigDates)


def get_codes(initialHolding, cash_code):
    all_codes = np.unique(initialHolding.columns)
    share_codes = np.unique(np.setdiff1d(all_codes, cash_code))

    return (all_codes, share_codes)