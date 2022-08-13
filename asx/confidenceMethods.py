from audioop import mul
from torch import negative, positive
import praw
import pandas as pd
from collections import Counter
import bs4
import urllib.request
from scipy import interpolate
import requests
from pytrends.request import TrendReq
import ta
import yfinance as yf

class Macro:
    def __init__(self, symbol):
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        x_points = [46, 53, 60, 80, 100]
        y_points = [1, -1, 0, 1, -1]
        self.tck = interpolate.splrep(x_points, y_points)
        self.symbol = symbol

    def f(self, x):
        return interpolate.splev(x, self.tck) if x >= 46 else 1



class TA:
    def __init__(self, symbol):
        ticker = yf.Ticker(symbol)  
        self.df = ticker.history(period="max")
        
    def rsi(self):
        rsi = ta.momentum.RSIIndicator(close = self.df['Close'], window = 14).rsi()
        rsi = float(rsi.iloc[-1]) - float(rsi.iloc[-8])
        return rsi/100
    
    def tsi(self):
        tsi = float(ta.momentum.TSIIndicator(close = self.df['Close']).tsi().iloc[-1])
        return tsi/100
    
    def macd(self):
        macd = float(ta.trend.MACD(close = self.df['Close']).macd().iloc[-1])
        return macd/100
        
def coefficientDict(client):
        markets = client.public.get_markets().data['markets']
        volDict = {}
        for k, v, in markets.items():
            if 'LUNA' not in k:
                    volDict[k] = [float(v['volume24H'])]
                    volDict[k].append(int(v['trades24H']))
                    volDict[k].append(float(v['indexPrice']))
                    orderbook = client.public.get_orderbook(market=k).data
                    asks = orderbook['asks']
                    bids = orderbook['bids']
                    diff = float(asks[0]['price']) - float(bids[0]['price'])
                    diff = round(diff/float(volDict[k][2])*100, 2)
                    volDict[k].append(diff)

        coefficientDict = {}
        for k in volDict:
            if volDict[k][-1] > 0.2 and volDict[k][1] > 300:
                coefficientDict[k] = volDict[k][0]

        coefficientDict = dict(sorted(coefficientDict.items(), key=lambda x: x[1], reverse=True))
        return coefficientDict


def findSymbol(initial):
    client = dydxMethods.auth()
    dic = coefficientDict(client)
    print(dic)
    newDic = {}
    for i in dic:
        macro = Macro(i)
        t_a = TA(i)
        superboost = macro.superBoost()
        multiplier = macro.getMultiplier()
        fng = macro.fearAndGreed()
        trend = macro.googleTrend()
        rsi = t_a.rsi()
        tsi = t_a.tsi()
        macd = t_a.macd()
        
        #calculations
        macroScore = ((superboost/10) + multiplier + fng + trend)/4
        microScore = (macro.f(rsi) + tsi*3 + macd)/5
        score = (microScore + macroScore) / 2
        score = dic[i]/(1-score)
        print(i, score)
        newDic[i] = score
        
    newDic = dict(sorted(newDic.items(), key=lambda x: x[1], reverse=True))
    

    nnewDic = {}
    for i in newDic:
        nnewDic[i] = newDic[i]*-1
    nnewDic = dict(sorted(nnewDic.items(), key=lambda x: x[1], reverse=True))

    symbol = next(iter(newDic))
    symbolC = newDic[symbol]
    symbo = next(iter(nnewDic))
    symboC = nnewDic[symbo]

    if symboC  > symbolC:
        s = symbo
        direction = 'SELL'
    else:
        s = symbol
        direction = 'BUY'
    
    while float(client.public.get_markets(market=s).data['markets'][s]['baselinePositionSize']) < float(tradingMethods.computeAmount(s, direction, initial)[1]):
        print(float(client.public.get_markets(market=s).data['markets'][s]['baselinePositionSize']), float(tradingMethods.computeAmount(s, direction, initial)[1]))
        nnewDic[s] = 0
        newDic[s] = 0
        newDic = dict(sorted(newDic.items(), key=lambda x: x[1], reverse=True))
        nnewDic = dict(sorted(nnewDic.items(), key=lambda x: x[1], reverse=True))
        symbol = next(iter(newDic))
        symbolC = newDic[symbol]
        symbo = next(iter(nnewDic))
        symboC = nnewDic[symbo]

        if symboC  > symbolC:
            s = symbo
            direction = 'SELL'
        else:
            s = symbol
            direction = 'BUY'
    
    print(s, direction)
    return [s, direction]



