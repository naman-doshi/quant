import dydxMethods

client = dydxMethods.auth()

markets = client.public.get_markets().data['markets']
volDict = {}
for k, v, in markets.items():
    volDict[k] = [float(v['volume24H'])]
    volDict[k].append(float(v['trades24H']))
    volDict[k].append(float(v['indexPrice']))
    orderbook = client.public.get_orderbook(market=k).data
    asks = orderbook['asks']
    bids = orderbook['bids']
    diff = float(asks[0]['price']) - float(bids[0]['price'])
    diff = round(diff/float(volDict[k][2])*100, 2)
    volDict[k].append(diff)

coefficientDict = {}
for k in volDict:
    if volDict[k][-1] > 0.15:
        coefficientDict[k] = volDict[k][1]


coefficientDict = dict(sorted(coefficientDict.items(), key=lambda x: x[1], reverse=True))
