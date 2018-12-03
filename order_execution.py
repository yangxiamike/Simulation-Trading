import pandas as pd
import numpy as np
import utils

def order_execution(d, s_orderWgt, s_currentHoldingWgt, df_holdings, cashAvail,
                    df_execution, df_turnoverPct, df_executePrice,
                    totalValue, buyCommission, sellCommission, lotSize, df_sellVolume, df_buyVolume,
                    share_codes, cash_code, targetHoldingCashWgt):
    if (s_orderWgt < 0).any().any():
        s_sellOrderWgt = s_orderWgt.copy()
        s_sellOrderWgt[s_sellOrderWgt > 0.] = 0.
        s_currentHoldingWgt = pd.DataFrame(s_currentHoldingWgt[share_codes])
        s_currentHoldingWgt = s_currentHoldingWgt.where(s_currentHoldingWgt > 0, 1.0)
        s_sellOrder = s_sellOrderWgt / s_currentHoldingWgt * pd.DataFrame(df_holdings.ix[d, share_codes])
        s_sellOrder = -pd.concat([s_sellOrder.fillna(0).abs(), df_sellVolume.ix[d]], axis=1).min(axis=1)
        s_sellExecution = s_sellOrder.copy()
        s_sellExecution = utils.roundToLot(s_sellExecution, lotSize)
        cashAvail += (s_sellExecution.abs() * df_executePrice.ix[d]*lotSize).sum() * (1 - sellCommission)
        df_execution.ix[d] += s_sellExecution*lotSize
        df_holdings.ix[d, share_codes] += s_sellExecution*lotSize
        df_holdings.ix[d, cash_code] = cashAvail
        if (df_holdings < 0).any().any():
            raise ValueError(d)

    if (s_orderWgt > 0).any().any():
        s_buyOrderWgt = s_orderWgt.copy()
        s_buyOrderWgt[s_orderWgt < 0.] = 0.
        canBuyWgt = cashAvail / totalValue - targetHoldingCashWgt
        if canBuyWgt > 0:
            amount = min(canBuyWgt / s_buyOrderWgt.sum()[0], 1.0) * s_buyOrderWgt * totalValue / (1 + buyCommission)
            execute = pd.DataFrame(df_executePrice.ix[d])
            execute.index = amount.index
            execute.columns = amount.columns    # pd.Series 如何与 pd.DataFrame进行运算
            s_buyOrder = (amount/execute).fillna(0)
            s_buyOrder = pd.concat([s_buyOrder.fillna(0), df_buyVolume.ix[d]], axis=1).min(axis=1)
            s_buyExecution = s_buyOrder.copy()
            s_buyExecution = utils.roundToLot(s_buyExecution, lotSize)
            cost = (s_buyExecution.abs() * df_executePrice.ix[d]*lotSize).sum() * (1 + buyCommission)
            cashLeft = cashAvail - cost
            """
            if cashLeft > 0:
                cashAvail = cashLeft
                df_execution.ix[d] += s_buyExecution*lotSize
                df_holdings.ix[d, share_codes] += s_buyExecution*lotSize
                df_holdings.ix[d, cash_code] = cashAvail
                if (df_holdings < 0).any().any():
                    raise ValueError(d)
            else:
                s_buyOrder = s_buyExecution * cashAvail / cost
                s_buyExecution = s_buyOrder.copy()
                df_execution.ix[d] += s_buyExecution*lotSize
                df_holdings.ix[d, share_codes] += s_buyExecution*lotSize
                cashAvail = 0
                df_holdings.ix[d, cash_code] = cashAvail
                if (df_holdings < 0).any().any():
                    raise ValueError(d)
            """
            df_execution.ix[d] += s_buyExecution*lotSize
            df_holdings.ix[d, share_codes] += s_buyExecution*lotSize
            df_holdings.ix[d, cash_code] = cashLeft
    ##################################
    df_turnoverPct.ix[d] = (df_execution.ix[d].abs() * df_executePrice.ix[d]).sum() / totalValue
    ##################################
    return (df_execution, df_holdings, cashAvail, df_turnoverPct)