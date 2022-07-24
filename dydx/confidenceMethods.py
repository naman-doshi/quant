from audioop import mul
from torch import negative, positive
import dydxMethods
import praw
import pandas as pd
import detectEnglish as de
from collections import Counter
import bs4
import urllib.request
from scipy import interpolate
import requests
from pytrends.request import TrendReq
import ta
import tradingMethods

class Macro:
    def __init__(self, symbol):
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        self.client = dydxMethods.auth()
        x_points = [46, 53, 60, 80, 100]
        y_points = [1, -1, 0, 1, -1]
        self.tck = interpolate.splrep(x_points, y_points)
        self.symbol = symbol

    def superBoost(self):
        #reddit login
        reddit = praw.Reddit(client_id='oXQCvleWbdbBCwf4zQGoQQ', \
                            client_secret='AXjJ0RjwBnVAUfjOct37S5ADVB-Ogg', \
                            user_agent='cryptosentiment', \
                            username='aerobull-', \
                            password='aerobull2006')
        
        subreddit = reddit.subreddit('CryptoCurrency')
        top_subreddit = subreddit.new(limit = 2500)

        topics_dict = { "title":[], \
                        "score":[], \
                        "created":[], \
                        "body":[]}

        for submission in top_subreddit:
            topics_dict["title"].append(submission.title)
            topics_dict["score"].append(submission.score)
            topics_dict["created"].append(submission.created)
            topics_dict["body"].append(submission.selftext)

        topics_data = pd.DataFrame(topics_dict)

        titles = topics_data['title'].tolist()
        all_titles = ' '.join(titles)

        all_titles = de.removeNonLetters(all_titles)
        all_titles = all_titles.split(" ")
        new_all_titles = []
        m = ''.join(self.client.public.get_markets().data['markets'].keys())

        #filtering out common phrases that could throw off the algorithm
        for i in all_titles:
            try:
                if i.isupper() == True and len(i) > 2 and len(i) < 5 and i in  m and i != 'USD' and i != 'USDT' and i != 'USDC' and i != 'SDF':
                    new_all_titles.append(i)
            except:
                pass

        c = Counter(new_all_titles)
        common = [i[0] for i in c.most_common(10)]

        ind = 1
        if self.symbol in common:
            ind = 10 - common.index(self.symbol)
        
        return ind

    def getMultiplier(self):
        url = "https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/"
        url_contents = urllib.request.urlopen(url).read()
        soup = bs4.BeautifulSoup(url_contents, features="lxml")
        div = soup.find("div", {"class": "legend"})
        active = div.find("span", {"class": "active"})
        content = str(active)

        multiplier = 0
        if 'Seriously' in content:
            multiplier = -2
        elif 'FOMO' in content: 
            multiplier = 1.5
        elif 'Is this a' in content:
            multiplier = 0.5
        elif 'HODL' in content:
            multiplier = 0.1
        elif 'cheap' in content:
            multiplier = -0.5
        elif 'Accumulate' in content:
            multiplier = -1.5
        elif 'BUY' in content: 
            multiplier = 1
        elif 'Fire' in content:
            multiplier = 2
        
        return multiplier

    def fearAndGreed(self):
        r = requests.get('https://api.alternative.me/fng/')
        r = r.json()
        r = int(r['data'][0]['value'])
        return interpolate.splev(r, self.tck) if r >= 46 else 1

    def googleTrend(self):
        pytrend = TrendReq()
        pytrend.build_payload(kw_list=[self.symbol.replace('-USD','')], timeframe="now 7-d")
        df = pytrend.interest_over_time()
        trend = int(df[self.symbol.replace('-USD','')].iloc[-1])*0.01
        return trend

    def f(self, x):
        return interpolate.splev(x, self.tck) if x >= 46 else 1



class TA:
    def __init__(self, symbol):
        client = dydxMethods.auth()
        candles = client.public.get_candles(market=symbol,resolution='5MINS').data['candles']
        
        lis = []
        for i in candles:
            lis.append([i['startedAt']] + list(map(float, [i['open'], i['high'], i['low'], i['close'], i['baseTokenVolume']])))
        df = pd.DataFrame(data=lis, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        self.df = df.iloc[::-1]
        
    def rsi(self):
        rsi = float(ta.momentum.RSIIndicator(close = self.df['Close'], window = 13).rsi().iloc[-1])
        return rsi
    
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



