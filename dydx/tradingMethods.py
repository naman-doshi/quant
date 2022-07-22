from more_itertools import random_combination_with_replacement
from regex import D
import dydxMethods

client = dydxMethods.auth()

def findSymbol():
    markets = client.public.get_markets().data['markets']
    volDict = {}
    for k, v, in markets.items():
        if 'LUNA' not in k:
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
    # for k in volDict:
    #     if volDict[k][-1] > 0.5:
    #         coefficientDict[k] = volDict[k][0] * volDict[k][-1]
    for k in volDict:
        if volDict[k][-1] > 0.15:
            coefficientDict[k] = volDict[k][1]


    coefficientDict = dict(sorted(coefficientDict.items(), key=lambda x: x[1], reverse=True))
    symbol = next(iter(coefficientDict))
    return symbol

def buy(symbol, buyPrice, amt):
    try:
      buy = dydxMethods.buy(client, str(symbol), str(buyPrice), str(amt))
    except:
      buy = dydxMethods.buy(client, str(symbol), str(buyPrice), str(int(float(amt))))
    return buy

def sell(symbol, buyPrice, amt):
    try:
      buy = dydxMethods.sell(client, symbol, buyPrice, amt)
    except:
      buy = dydxMethods.sell(client, symbol, buyPrice, str(int(float(amt))))
    return buy

def updateBuy(symbol, current, orderID, opening=True, sellPrice=1):
    orderbook = client.public.get_orderbook(market=symbol).data
    all_orders = dydxMethods.getOrders(client, symbol)
    remainingSize = all_orders[0]['remainingSize']
    # target = float(orderbook['bids'][0]['price'])
    # targetSize = float(orderbook['bids'][0]['size'])
    # bottom = float(orderbook['bids'][1]['price'])
    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
    tickSize = float(markets['tickSize'])

    su = 0
    count = 0
    markets = client.public.get_markets().data['markets']
    t = (float(markets[symbol]['volume24H']) / float(markets[symbol]['trades24H'])) / float(markets[symbol]['indexPrice'])
    t = round(t, str(tickSize).count('0'))
    while su < t:
        su += float(orderbook['bids'][count]['size'])
        su = round(su, str(tickSize).count('0'))
        count += 1
    
    target = orderbook['bids'][count-1]['price']
    targetSize = orderbook['bids'][count-1]['size']
    bottom = orderbook['bids'][count]['price']
    target = float(target)
    bottom = float(bottom)

    if opening == True:
        if current != target:
            current = target
            cancelOrders()
            remainingSize = all_orders[0]['remainingSize']
            orderID = buy(symbol, current, remainingSize)
        elif current == target and remainingSize==str(targetSize):
            current = bottom
            cancelOrders()
            remainingSize = all_orders[0]['remainingSize']
            orderID = buy(symbol, current, remainingSize)
    else:
        if current != target:
            if target < sellPrice:
                current = target
                cancelOrders()
                remainingSize = all_orders[0]['remainingSize']
                orderID = buy(symbol, current, remainingSize)
        elif current == target:
            if remainingSize == str(targetSize):
                current = bottom
                cancelOrders()
                remainingSize = all_orders[0]['remainingSize']
                orderID = buy(symbol, current, remainingSize)
    return (orderID, current)

def updateSell(symbol, current, orderID, opening=True, buyPrice=1):
    orderbook = client.public.get_orderbook(market=symbol).data
    all_orders = dydxMethods.getOrders(client, symbol)
    remainingSize = all_orders[0]['remainingSize']
    # target = float(orderbook['asks'][0]['price'])
    # targetSize = float(orderbook['asks'][0]['size'])
    # top = float(orderbook['asks'][1]['price'])
    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
    tickSize = float(markets['tickSize'])

    su = 0
    count = 0
    markets = client.public.get_markets().data['markets']
    t = (float(markets[symbol]['volume24H']) / float(markets[symbol]['trades24H'])) / float(markets[symbol]['indexPrice'])
    t = round(t, str(tickSize).count('0'))
    while su < t:
        su += float(orderbook['asks'][count]['size'])
        su = round(su, str(tickSize).count('0'))
        count += 1
    
    target = orderbook['asks'][count-1]['price']
    targetSize = orderbook['asks'][count-1]['size']
    top = orderbook['asks'][count]['price']
    target = float(target)
    top = float(top)

    if opening == True:
        if current != target:
            current = target
            cancelOrders()
            remainingSize = all_orders[0]['remainingSize']
            orderID = sell(symbol, current, remainingSize)
        elif current == target and remainingSize==str(targetSize):
            current = top
            cancelOrders()
            remainingSize = all_orders[0]['remainingSize']
            orderID = sell(symbol, current, remainingSize)
    else:
        if current != target:
            if target > buyPrice:
                current = target
                cancelOrders()
                remainingSize = all_orders[0]['remainingSize']
                orderID = sell(symbol, current, remainingSize)
        elif current == target:
            if remainingSize == str(targetSize):
                current = top
                cancelOrders()
                remainingSize = all_orders[0]['remainingSize']
                orderID = sell(symbol, current, remainingSize)
    return (orderID, current)

def determineDirection(): 
    markets = client.public.get_markets().data['markets']
    
    allChanges = []
    for i in markets:
        stat = client.public.get_stats(market=i).data
        openPrice = float(stat['markets'][i]['open'])
        closePrice = float(stat['markets'][i]['close'])
        try:
            change = (closePrice-openPrice)/openPrice
        except:
            change = 0
        allChanges.append(change*100)
        
    avg = sum(allChanges) / len(allChanges)

    if avg >= 0:
        direction = 'BUY'
    else:
        direction = 'SELL'
    
    return direction

def isPositionOpen():
    return len(client.private.get_positions(status='OPEN').data['positions']) != 0 

def isOrderOpen():
    return len(client.private.get_orders(status='OPEN').data['orders']) != 0 

def computeAmount(symbol, direction, initial):
    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
    stepSize = float(markets['stepSize'])
    orderbook = client.public.get_orderbook(market=symbol).data

    if direction == 'BUY':
        price = float(orderbook['bids'][0]['price'])
    else:
        price = float(orderbook['asks'][0]['price'])

    amt = str(round((initial/price)*9, str(stepSize).count('0')))

    return (price, amt)


def stopLoss(direction, symbol, price, remainingSize):
    import time 
    account_response = client.private.get_account()
    position_id = account_response.data['account']['positionId']
    order_params = {
      'position_id': position_id,
      'market': symbol,
      'side': direction,
      'order_type': 'STOP',
      'post_only': False,
      'size': str(remainingSize),
      'price': str(price),
      'limit_fee': '0.0005',
      'expiration_epoch_seconds': time.time() + 100000,
    }
    order_response = client.private.create_order(**order_params)
    order_id = order_response.data['order']['id']

    return order_id

def cancelOrders():
    all_orders = client.private.get_orders().data['orders']
    for i in all_orders:
        if i['type'] == 'LIMIT':
            client.private.cancel_order(order_id=i['id'])

def addVolume(add):
    with open('dydx/volume.txt') as f:
        lines = f.readlines()
        vol = int(lines[0])
        vol += add
    with open('dydx/volume.txt', 'w') as f:
        f.write(str(vol))

