import numpy as np
import pandas as pd


def do_trade(w, price, commission,init_portfolio=None):
    """
    :param init_portfolio: t-1 时刻的 post trade 的 portfolio weight
    :param target_portfolio: t 时刻（及 t 以后时刻） portfolio weight，RL是每次给一期
    :param price: 后复权的价格
    :param commission: 交易费率，long 、short 的费率相同
    :return: t时刻开始的 NAV，仅在 portfolio 的 t 时刻有值
    """

    # t_portfolio = t_portfolio + t_minus_one_portfolio[-1] #把上一期叠到  target_portfolio 中
    # price = price.ix[t_portfolio.index]
    # ret = price / price.lag(1)
    # nav_pre = t_portfolio * price
    # cost =  sum( (t_portfolio - t_portfolio.lag(1) ) * price ) * commission
    # nav = nav - cost
    # return nav
    if init_portfolio:
        target_portfolio = target_portfolio + init_portfolio.ix[-1]
    price = price.ix[w.index]

    ret = price / price.shift(1)
    w__ = w.shift(1) * ret
    w__sum = w__.sum(axis=1)
    w_ = w__ / w__sum
    cost_ret = ((w - w_)).abs().sum(axis=1) * commission
    raw_ret = w__sum
    raw_ret.ix[0] = 1
    after_cost = raw_ret * (1 - cost_ret)
    after_cost_accu_ret = after_cost.prod()

    return after_cost_accu_ret



def batch_trade(target_port_wgt,price,commission,batch_size = 1000,init_portfolio_wgt=None):
    size = len(target_port_wgt.index)
    print(size)
    rets = []
    start = 0
    end = batch_size
    while start < size-1:
        if end <= (size-1):
            ret = do_trade(target_port_wgt[start:end],price,commission)
            rets.append(ret)
            start = end - 1
            end += batch_size
        else:
            ret = do_trade(target_port_wgt[start:size-1],price,commission)
            print(start)
            rets.append(ret)
            start = end-1
    result = np.array(rets).prod()-1

    return result

