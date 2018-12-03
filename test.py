import numpy as np
import pandas as pd
import tushare as ts

if __name__ == '__main__':
    api = ts.get_apis()
    stock = ts.bar('000651', api, start_date='2017-12-1', end_date='2018-8-1')
    stock = stock.sort_index(ascending=True)
    stock_code = stock['code'][0]
    cash_code = 'RMB'
    dict_tradingParam = {'canTradeOnSuspend': 1, 'RiseLimitThres': 0.1, 'FallLimitThres': -0.1, 'VolumeLimitPct': 0.1,
                         'cash_code': 'RMB', 'lotSize': 100}
    beginDate = stock.index[0]
    endDate = stock.index[-1]

    df_targetPortfolioWgt = pd.DataFrame(np.ones((len(stock.index), 2)) * 0.5, index=stock.index,
                                         columns=[stock_code, cash_code])
    initialHolding = pd.DataFrame(np.array([[20000, 1000000]]), pd.date_range(beginDate, periods=1),
                                  columns=[stock_code, cash_code])
    df_markToMarketPrice = pd.DataFrame(stock['close'])
    df_markToMarketPrice.columns = [stock_code]
    df_markToMarketPrice[cash_code] = np.ones(len(stock['close']))

    df_totalReturnFactor = pd.DataFrame(np.ones((len(stock['close']), 2)), stock.index, columns=[stock_code, cash_code])
    df_executePrice = pd.DataFrame(df_markToMarketPrice[stock_code])
    df_execPriceReturn = pd.DataFrame(np.random.randn(len(stock['close'])), stock.index, columns=[stock_code])
    df_tradeVolume = pd.DataFrame(stock['vol'])
    df_tradeVolume.columns = [stock_code]

