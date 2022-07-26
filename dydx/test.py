import dydxMethods
client = dydxMethods.auth()
orderbook = client.public.get_orderbook(market='BTC-USD').data
print(orderbook)