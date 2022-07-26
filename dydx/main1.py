import dydxMethods
import time
import tradingMethods
import emailMethods
import time
import confidenceMethods

initial = 3000

while True:
  client = dydxMethods.auth()
  symbol = confidenceMethods.findSymbol(initial)
  direction = symbol[1]
  symbol = symbol[0]
  markets = client.public.get_markets(market=symbol).data['markets'][symbol]
  tickSize = float(markets['tickSize'])
  

  if direction == 'BUY':
    #to buy
    compute = tradingMethods.computeAmount(symbol, direction, initial)
    buyPrice = compute[0]
    amount = compute[1]
    print(compute)

    #initial buy order
    orderID = tradingMethods.buy(symbol, buyPrice, amount)
    start = time.time() 

    while tradingMethods.isOrderOpen() == True:
      end = time.time()
      print(end-start)
      #time
      if end-start < 600 or tradingMethods.isPositionOpen() == True:
        if tradingMethods.isOrderOpen() == True:
          try:
              orderID = tradingMethods.updateBuy(symbol, buyPrice, orderID)
              buyPrice = orderID[1]
              orderID = orderID[0]
          except:
              break
        else:
          break
      else:
        print('time limit exceeded')
        tradingMethods.cancelOrders()
        symbol = confidenceMethods.findSymbol(initial)
        symbol = symbol[0]
        markets = client.public.get_markets(market=symbol).data['markets'][symbol]
        tickSize = float(markets['tickSize'])
        compute = tradingMethods.computeAmount(symbol, direction, initial)
        buyPrice = compute[0]
        amount = compute[1]
        orderID = tradingMethods.buy(symbol, buyPrice, amount)

        start = time.time()
      

    
    #init sell
    orderbook = client.public.get_orderbook(market=symbol).data
    sellPrice = float(orderbook['asks'][0]['price'])
    all_positions = dydxMethods.getPositions(client, symbol)
    buyPrice = float(all_positions[0]['entryPrice'])
    buyPrice = round(buyPrice, str(tickSize).count('0'))

    if sellPrice < buyPrice:
      sellPrice = buyPrice + (5*tickSize)
    
    all_positions = dydxMethods.getPositions(client, symbol)
    remainingSize = all_positions[0]['size']
    amt = remainingSize
    tradingMethods.addVolume(float(amt)*float(buyPrice))
    sellPrice = round(sellPrice, str(tickSize).count('0'))

    emailMethods.email(f'Bought {symbol} at average buy price of {buyPrice}')

    orderID = tradingMethods.sell(symbol, sellPrice, remainingSize)

    while tradingMethods.isOrderOpen() == True:
      try:
          orderID = tradingMethods.updateSell(symbol, sellPrice, orderID, opening=False, buyPrice=buyPrice)
          sellPrice = orderID[1]
          orderID = orderID[0]
          print(sellPrice, tradingMethods.isOrderOpen())
      except:
          break
    
    time.sleep(10)
    pos = client.private.get_positions(market=symbol, status='CLOSED')
    sellPrice = pos.data['positions'][0]['exitPrice']

    tradingMethods.addVolume(float(amt)*float(sellPrice))

    emailMethods.email(f'Closed sold {symbol} at last sell price of {sellPrice}')
  
  else:
    compute = tradingMethods.computeAmount(symbol, direction, initial)
    sellPrice = compute[0]
    amount = compute[1]
    print(compute)

    #initial sell order
    orderID = tradingMethods.sell(symbol, sellPrice, amount)
    start = time.time()

    while tradingMethods.isOrderOpen() == True:
      end = time.time()
      print(end-start)

      #time
      if end-start < 600 or tradingMethods.isPositionOpen() == True:
        if tradingMethods.isOrderOpen() == True:
          try:
            orderID = tradingMethods.updateSell(symbol, sellPrice, orderID)
            sellPrice = orderID[1]
            orderID = orderID[0]
          except:
            break
        else:
          break
      else:
        tradingMethods.cancelOrders()
        symbol = confidenceMethods.findSymbol(initial)
        symbol = symbol[0]
        markets = client.public.get_markets(market=symbol).data['markets'][symbol]
        tickSize = float(markets['tickSize'])
        compute = tradingMethods.computeAmount(symbol, direction, initial)
        sellPrice = compute[0]
        amount = compute[1]
        orderID = tradingMethods.sell(symbol, sellPrice, amount)

        start = time.time()
 
    
    orderbook = client.public.get_orderbook(market=symbol).data
    markets = client.public.get_markets(market=symbol).data['markets'][symbol]
    all_positions = dydxMethods.getPositions(client, symbol)
    tickSize = float(markets['tickSize'])
    buyPrice = float(orderbook['bids'][0]['price'])
    sellPrice = float(all_positions[0]['entryPrice'])
    sellPrice = round(sellPrice, str(tickSize).count('0'))

    if sellPrice < buyPrice:
      buyPrice = sellPrice - (5*tickSize)
    
    all_positions = dydxMethods.getPositions(client, symbol)
    remainingSize = str(float(all_positions[0]['size'])*-1)
    amt = remainingSize
    tradingMethods.addVolume(float(amt)*float(sellPrice))
    buyPrice = round(buyPrice, str(tickSize).count('0'))
    

    emailMethods.email(f'Sold {symbol} at average sell price of {sellPrice}')

    orderID = tradingMethods.buy(symbol, buyPrice, remainingSize)

    while tradingMethods.isOrderOpen() == True:
      try:
          orderID = tradingMethods.updateBuy(symbol, buyPrice, orderID, opening=False, sellPrice=sellPrice)
          buyPrice = orderID[1]
          orderID = orderID[0]
          print(orderID)
      except:
          break
      
    time.sleep(10)
    pos = client.private.get_positions(market=symbol, status='CLOSED')
    buyPrice = pos.data['positions'][0]['exitPrice']
    tradingMethods.addVolume(float(amt)*float(buyPrice))

    emailMethods.email(f'Closed bought {symbol} at last buy price of {buyPrice}')














