from preprocessing import *
from order_execution import order_execution
from return_cal import return_cal
import pandas as pd
from utils import fillHolding

def SIMPLE_SIMULATE_DAILY_TRADE_CHN_STK(endDate, initialHolding, df_targetPortfolioWgt,
                                        df_markToMarketPrice, df_totalReturnFactor, df_executePrice,
                                        df_execPriceReturn, df_tradeVolume, dict_tradingParam,
                                        dict_additionalTs=None):
    (df_initialHolding, df_totalReturnFactor,
     df_executePrice, df_targetPortfolioWgt, df_buyVolume, df_sellVolume,
     tradeDates, rebDates, lotSize,
     buyCommission, sellCommission, initHoldingValue, all_codes, cash_code, share_codes) = pre_process(endDate,
                                                                                                       initialHolding,
                                                                                                       df_targetPortfolioWgt,
                                                                                                       df_markToMarketPrice,
                                                                                                       df_totalReturnFactor,
                                                                                                       df_executePrice,
                                                                                                       df_execPriceReturn,
                                                                                                       df_tradeVolume,
                                                                                                       dict_tradingParam)

    df_holdings = pd.DataFrame(0., index=tradeDates, columns=all_codes)
    df_weights = df_holdings.copy()

    df_cumRets = pd.DataFrame(0., index=tradeDates, columns=share_codes)
    df_singlePeriodRets = df_cumRets.copy()
    df_turnoverPct = df_cumRets.copy()
    df_execution = df_cumRets.copy()
    df_portfolioValue = df_holdings.copy()

    d = tradeDates[0]
    df_holdings.ix[d] = df_initialHolding.ix[d]

    if len(rebDates) < 1:
        nextd = tradeDates[-1]
        ls_adjustedHoldings = fillHolding(d, nextd, tradeDates, df_holdings, df_totalReturnFactor)
        df_holdings = ls_adjustedHoldings

    else:
        nextd = rebDates[0]
        ls_adjustedHoldings = fillHolding(d, nextd, tradeDates, df_holdings, df_totalReturnFactor)
        df_holdings = ls_adjustedHoldings

        # Path dependent
        for i in range(len(rebDates)):
            d = rebDates[i]
            s_currentHoldingValue = df_holdings.ix[d] * df_markToMarketPrice.ix[d]
            if (s_currentHoldingValue < 0).any().any():
                raise ValueError(d)
            totalValue = s_currentHoldingValue.sum()
            s_currentHoldingWgt = s_currentHoldingValue / totalValue
            s_targetHoldingWgt = df_targetPortfolioWgt.ix[d]
            targetHoldingCashWgt = s_targetHoldingWgt[cash_code]

            s_orderWgt = pd.DataFrame((s_targetHoldingWgt - s_currentHoldingWgt)[share_codes])
            cashAvail = df_holdings.ix[d, cash_code]

            # ZT: order execution should be in a separate function
            (df_execution, df_holdings, cashAvail, df_turnoverPct) = order_execution(d, s_orderWgt, s_currentHoldingWgt,
                                                                                     df_holdings, cashAvail,
                                                                                     df_execution, df_turnoverPct,
                                                                                     df_executePrice,
                                                                                     totalValue, buyCommission,
                                                                                     sellCommission, lotSize,
                                                                                     df_sellVolume, df_buyVolume,
                                                                                     share_codes, cash_code,
                                                                                     targetHoldingCashWgt)

            if i < (len(rebDates) - 1):
                nextd = rebDates[i + 1]
            else:
                nextd = tradeDates[-1]
            ls_adjustedHoldings = fillHolding(d, nextd, tradeDates, df_holdings, df_totalReturnFactor)
            df_holdings = ls_adjustedHoldings

    result = return_cal(df_portfolioValue, df_holdings, df_markToMarketPrice, tradeDates, initHoldingValue,
                        df_turnoverPct, share_codes)
    return result