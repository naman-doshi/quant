import dydxMethods
import time
import tradingMethods
import emailMethods
import time

#client 
client = dydxMethods.auth()

initial = 4000

while True:
  direction = tradingMethods.determineDirection(client)
  symbol = tradingMethods.findSymbol()

  if direction == 'BUY':
    #to buy
    compute = tradingMethods.computeAmount(client, symbol, direction, initial)
    buyPrice = compute[0]
    amount = compute[1]

    #initial buy order
    orderID = tradingMethods.buy(client, symbol, buyPrice, amount)
    start = time.time()
    client = dydxMethods.auth()

    while tradingMethods.isOrderOpen(client) == True:
      end = time.time()
      print(end-start)
      #time
      if end-start < 600 or tradingMethods.isPositionOpen(client) == True:
        try:
            all_orders = dydxMethods.getOrders(client, symbol)
            remainingSize = all_orders[0]['remainingSize']
            if float(remainingSize) != amount:
              start = time.time()
              amount = float(remainingSize)
            orderID = tradingMethods.updateBuy(client, symbol, buyPrice, orderID)
            buyPrice = orderID[1]
            orderID = orderID[0]
        except:
            break
      else:
        print('time limit exceeded')
        tradingMethods.cancelOrders(client)
        symbol = tradingMethods.findSymbol()
        compute = tradingMethods.computeAmount(client, symbol, direction, initial)
        buyPrice = compute[0]
        amount = compute[1]
        orderID = tradingMethods.buy(client, symbol, buyPrice, amount)

        start = time.time()
      
      time.sleep(3)

    
    #init sell
    print(1)
    client = dydxMethods.auth()
    orderbook = client.public.get_orderbook(market=symbol).data
    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
    all_positions = dydxMethods.getPositions(client, symbol)
    tickSize = float(markets['tickSize'])
    sellPrice = float(orderbook['asks'][0]['price'])
    buyPrice = float(all_positions[0]['entryPrice'])
    buyPrice = round(buyPrice, str(tickSize).count('0'))
    print(2)

    if sellPrice < buyPrice:
      sellPrice = buyPrice + (5*tickSize)
    
    print(3, sellPrice)
    
    all_positions = dydxMethods.getPositions(client, symbol)
    remainingSize = all_positions[0]['size']
    sellPrice = round(sellPrice, str(tickSize).count('0'))
    print(4)

    emailMethods.email(f'Bought {symbol} at average buy price of {buyPrice}')
    print(5)

    orderID = tradingMethods.sell(client, symbol, sellPrice, remainingSize)
    print(6)

    while tradingMethods.isOrderOpen(client) == True:
      try:
          orderID = tradingMethods.updateSell(client, symbol, sellPrice, orderID, opening=False, buyPrice=buyPrice)
          sellPrice = orderID[1]
          orderID = orderID[0]
          print(sellPrice, tradingMethods.isOrderOpen(client))
      except:
          break
      time.sleep(3)

    emailMethods.email(f'Closed sold {symbol} at last sell price of {sellPrice}')
  
  else:
    compute = tradingMethods.computeAmount(client, symbol, direction, initial)
    sellPrice = compute[0]
    amount = compute[1]
    client = dydxMethods.auth()

    #initial sell order
    orderID = tradingMethods.sell(client, symbol, sellPrice, amount)
    start = time.time()

    while tradingMethods.isOrderOpen(client) == True:
      end = time.time()
      print(end-start)

      #time
      if end-start < 600 or tradingMethods.isPositionOpen(client) == True:
        try:
          all_orders = dydxMethods.getOrders(client, symbol)
          remainingSize = all_orders[0]['remainingSize']
          if float(remainingSize) != amount:
            start = time.time()
            amount = float(remainingSize)
          orderID = tradingMethods.updateSell(client, symbol, sellPrice, orderID)
          sellPrice = orderID[1]
          orderID = orderID[0]
        except:
          break
      else:
        tradingMethods.cancelOrders(client)
        symbol = tradingMethods.findSymbol()
        compute = tradingMethods.computeAmount(client, symbol, direction, initial)
        sellPrice = compute[0]
        amount = compute[1]
        orderID = tradingMethods.sell(client, symbol, sellPrice, amount)

        start = time.time()
      
      time.sleep(3)
    
    print('buying over')

    client = dydxMethods.auth()
    print('buying over1')
    orderbook = client.public.get_orderbook(market=symbol).data
    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
    all_positions = dydxMethods.getPositions(client, symbol)
    tickSize = float(markets['tickSize'])
    buyPrice = float(orderbook['bids'][0]['price'])
    sellPrice = float(all_positions[0]['entryPrice'])
    sellPrice = round(sellPrice, str(tickSize).count('0'))
    print('buying over2')

    if sellPrice < buyPrice:
      buyPrice = sellPrice - (5*tickSize)
    
    all_positions = dydxMethods.getPositions(client, symbol)
    remainingSize = str(float(all_positions[0]['size'])*-1)
    buyPrice = round(buyPrice, str(tickSize).count('0'))
    

    print('emailed')
    
    emailMethods.email(f'Sold {symbol} at average sell price of {sellPrice}')
    print('emailed')

    client = dydxMethods.auth()
    orderID = tradingMethods.buy(client, symbol, buyPrice, remainingSize)
    print('selling now..')

    while tradingMethods.isOrderOpen(client) == True:
      try:
          orderID = tradingMethods.updateBuy(client, symbol, buyPrice, orderID, opening=False, sellPrice=sellPrice)
          buyPrice = orderID[1]
          orderID = orderID[0]
          print(orderID)
      except:
          break
      
      time.sleep(3)

    emailMethods.email(f'Closed bought {symbol} at last buy price of {buyPrice}')














