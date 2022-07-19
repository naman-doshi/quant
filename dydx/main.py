from ast import excepthandler
import time
from dydx3 import Client
from sklearn.metrics import jaccard_score
from web3 import Web3
import operator
import matplotlib.pyplot as plt
import numpy as np
import dydxMethods
import time
import tradingMethods
import emailMethods
import time


client = dydxMethods.auth()

initial = 800
direction = 'BUY'

while True:
    symbol = tradingMethods.findSymbol()
    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
    tickSize = float(markets['tickSize'])
    stepSize = float(markets['stepSize'])
    orderbook = client.public.get_orderbook(market=symbol).data

    if direction == 'BUY':
        buyPrice = float(orderbook['bids'][0]['price'])
        amt = str(round((initial/buyPrice)*9, str(stepSize).count('0')))
        all_positions = dydxMethods.getPositions(client, symbol)

        if len(all_positions) == 0:
            try:
                buy = dydxMethods.buy(client, symbol, buyPrice, amt)
            except:
                buy = dydxMethods.buy(client, symbol, buyPrice, str(int(float(amt))))
            
            start = time.time()

            orderID = buy[0]
            all_orders = dydxMethods.getOrders(client, symbol)
            
            while len(all_orders) != 0:
                end = time.time()

                if end-start < 600:
                    try:   
                        all_orders = dydxMethods.getOrders(client, symbol)
                        remainingSize = all_orders[0]['remainingSize']
                        orderID = tradingMethods.updateBuy(client, symbol, buyPrice, orderID, buy[2])
                        buyPrice = orderID[1]
                        orderID = orderID[0]
                    except IndexError:
                        break
                else:
                    a = client.private.cancel_order(order_id=orderID)
                    symbol = tradingMethods.findSymbol()
                    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
                    tickSize = float(markets['tickSize'])
                    stepSize = float(markets['stepSize'])
                    orderbook = client.public.get_orderbook(market=symbol).data
                    buyPrice = float(orderbook['bids'][0]['price'])
                    amt = str(round((initial/buyPrice)*9, str(stepSize).count('0')))
                    try:
                        buy = dydxMethods.buy(client, symbol, buyPrice, amt)
                    except:
                        buy = dydxMethods.buy(client, symbol, buyPrice, str(int(float(amt))))
                    orderID = buy[0]
                    start = time.time()
                all_orders = dydxMethods.getOrders(client, symbol)
                        

        orderbook = client.public.get_orderbook(market=symbol).data
        sellPrice = float(orderbook['asks'][0]['price'])

        while sellPrice <= buyPrice:
            sellPrice += tickSize
        
        all_positions = dydxMethods.getPositions(client, symbol)
        remainingSize = all_positions[0]['size']
        buyPrice = float(all_positions[0]['entryPrice'])
        buyPrice = round(buyPrice, str(tickSize).count('0'))
        sellPrice = round(sellPrice, str(tickSize).count('0'))


        emailMethods.email(f'Bought {symbol} at average buy price of {buyPrice}')

        
        try:
            sell = dydxMethods.sell(client, symbol, sellPrice, remainingSize)
        except:
            sell = dydxMethods.sell(client, symbol, str(int(sellPrice)), remainingSize)

        orderID = sell[0]
        all_orders = dydxMethods.getOrders(client, symbol)

        while len(all_orders) != 0:
            try:
                all_orders = dydxMethods.getOrders(client, symbol)
                orderID = tradingMethods.updateSell(client, symbol, sellPrice, orderID, sell[2], opening=False, buyPrice=buyPrice)
                sellPrice = orderID[1]
                orderID = orderID[0]
                time.sleep(5)
                all_orders = dydxMethods.getOrders(client, symbol)
                print('sell')
            except IndexError:
                break

        

        emailMethods.email(f'Sold {symbol} at last sell price of {sellPrice}')

    

            
#trying uppercutting for now, if unprofitable it might have to match target
#cumulative size thingy
#use avgbuy instead of buyPrice

    





