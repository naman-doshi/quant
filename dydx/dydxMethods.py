import time
from dydx3 import Client
import os


def auth():
  #connection, setup
  networkId = 3
  apiHost = 'https://api.stage.dydx.exchange'
  accAddress = '0x019c166611D65dc1299FF1C7796a18CcFd2eDeA6'
  networkID = 3
  pkey = '768d3a7cc07f58a608421d7386bddbefc0ac472e4c0c2d9bd30d1eab9cd8a8b2'

  client = Client(
      network_id=networkID,
      host=apiHost,
      default_ethereum_address=accAddress,
      eth_private_key=pkey
  )

  key = client.onboarding.derive_stark_key(
    ethereum_address=accAddress
  )

  client.stark_private_key = key['private_key']
  client.stark_public_key = key['public_key']
  client.stark_public_key_y_coordinate = key['public_key_y_coordinate']
  return client

def buy(client, symbol, price, size):
  account_response = client.private.get_account()
  position_id = account_response.data['account']['positionId']
  order_params = {
      'position_id': position_id,
      'market': symbol,
      'side': 'BUY',
      'order_type': 'LIMIT',
      'post_only': False,
      'size': str(size),
      'price': str(price),
      'limit_fee': '0.0005',
      'expiration_epoch_seconds': time.time() + 100000,
  }

  order_response = client.private.create_order(**order_params)
  order_id = order_response.data['order']['id']

  return order_id

def sell(client, symbol, price, size):
  account_response = client.private.get_account()
  position_id = account_response.data['account']['positionId']
  order_params = {
      'position_id': position_id,
      'market': symbol,
      'side': 'SELL',
      'order_type': 'LIMIT',
      'post_only': False,
      'size': str(size),
      'price': str(price),
      'limit_fee': '0.0005',
      'expiration_epoch_seconds': time.time() + 100000,
  }

  order_response = client.private.create_order(**order_params)
  order_id = order_response.data['order']['id']

  return order_id

def getPositions(client, symbol):
  return client.private.get_positions(market=symbol, status='OPEN').data['positions']

def getOrders(client, symbol):
  return client.private.get_orders(market=symbol, status='OPEN').data['orders']

def updateOrder(client, orderID, price, size, params):
  order_response = client.private.create_order(
            **dict(
                params,
                size=str(size),
                price=str(price),
                cancel_id=orderID,
            ),
        )
  orderID = order_response.data['order']['id']
  return(orderID)





