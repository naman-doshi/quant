import pandas as pd
import yfinance as yf
from confidenceMethods import *
from scipy import interpolate

def f(x):
  x_points = [46, 53, 60, 80, 100]
  y_points = [1, -1, 0, 1, -1]
  tck = interpolate.splrep(x_points, y_points)
  return interpolate.splev(x, tck) if x >= 46 else 1

df = pd.read_csv('asx/comp.csv')
dic = {}

for i in df['Code']:
  macro = Macro(i)
  stock = TA(i+'.AX')
  rsi = stock.rsi()
  tsi = stock.tsi()
  macd = stock.macd()
  avg = (rsi + tsi + macd) / 3
  if rsi > 0 and tsi > 0 and macd > 0:
    dic[i] = avg
    print(i, avg)

dic = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))
print(dic)