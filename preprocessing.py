import numpy as np
import pandas as pd
import datetime
import utils
from get_volume import *
'''
df_targetPortfolioWgt = df_targetPortfolioWgt.as_matrix()
df_markToMarketPrice = df_markToMarketPrice.as_matrix()
df_totalReturnFactor = df_totalReturnFactor.as_matrix()
df_executePrice = df_executePrice.as_matrix()
df_execPriceReturn = df_execPriceReturn.as_matrix()
df_tradeVolume = df_tradeVolume.as_matrix()
'''

def pre_process(endDate, initialHolding, df_targetPortfolioWgt,
                df_markToMarketPrice, df_totalReturnFactor, df_executePrice,
                df_execPriceReturn, df_tradeVolume, dict_tradingParam,
                dict_additionalTs=None):
    cash_code = utils.getParameter(dict_tradingParam, 'cash_code', 'RMB')
    lotSize = utils.getParameter(dict_tradingParam, 'lotSize', 100)
    buyCommission = utils.getParameter(dict_tradingParam, 'buyCommission', 0.001)
    sellCommission = utils.getParameter(dict_tradingParam, 'sellCommission', 0.001)

    beginDate = initialHolding.index[0]
    allDates = df_markToMarketPrice.index
    endDate = allDates[allDates <= endDate][-1]
    tradeDates = allDates[(allDates >= beginDate) & (allDates <= endDate)]
    if len(allDates[(allDates >= beginDate) & (allDates <= endDate)]) < 1:
        raise ValueError('no trading date falls between begindate and enddate')
    if beginDate > endDate:
        raise ValueError('beginDate should be less than endDate')

    df_initialHolding = initialHolding
    if df_initialHolding.shape[0] < 1:
        raise ValueError('No initial holding is provided')

    if (df_targetPortfolioWgt < 0).any(axis=1).any():
        raise ValueError('Stock price should not be less than 0')
    if (round(df_targetPortfolioWgt.sum(axis=1), 4) > 1).any():
        raise ValueError('Total Weight is greater than 1')
    df_targetPortfolioWgt = df_targetPortfolioWgt.dropna(axis=[0, 1], how='all')

    sigDates = df_targetPortfolioWgt.index
    rebDates = sigDates
    rebDates = rebDates[(rebDates >= beginDate) & (rebDates <= endDate)]
    df_targetPortfolioWgt = df_targetPortfolioWgt.ix[rebDates]

    all_codes = np.unique(df_initialHolding.columns)
    share_codes = np.unique(np.setdiff1d(df_initialHolding.columns, cash_code))
    holding_codes = np.array([])
    holding_codes = np.unique(np.setdiff1d(df_initialHolding.columns, cash_code))

    priceDates = allDates[(allDates >= beginDate - datetime.timedelta(days=20)) & (allDates <= endDate)]
    df_markToMarketPrice = df_markToMarketPrice.reindex(priceDates, all_codes, fill_value=np.nan)
    df_totalReturnFactor = df_totalReturnFactor.reindex(priceDates, all_codes, fill_value=np.nan)
    df_executePrice = df_executePrice.reindex(priceDates, holding_codes, fill_value=np.nan)
    df_execPriceReturn = df_execPriceReturn.reindex(priceDates, holding_codes, fill_value=np.nan)
    df_tradeVolume = df_tradeVolume.reindex(priceDates, holding_codes, fill_value=np.nan)
    df_targetPortfolioWgt = df_targetPortfolioWgt.reindex(rebDates, all_codes, fill_value=0.).fillna(0.)
    initHoldingValue = float((df_initialHolding * df_markToMarketPrice.ix[df_initialHolding.index]).sum(axis=1))

    df_buyVolume = df_tradeVolume.copy().fillna(0)
    df_sellVolume = df_buyVolume.copy()
    (df_buyVolume, df_sellVolume) = get_volume(dict_tradingParam, df_buyVolume, df_sellVolume, df_execPriceReturn,
                                               lotSize)

    return (df_initialHolding, df_totalReturnFactor,
            df_executePrice, df_targetPortfolioWgt, df_buyVolume, df_sellVolume,
            tradeDates, rebDates, lotSize,
            buyCommission, sellCommission, initHoldingValue, all_codes, cash_code, share_codes)




