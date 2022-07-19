import pandas as pd
import get_sentiment

df = pd.read_csv('asx/comp.csv')

for i in df['Company name']:
  sentiment = get_sentiment.GetSentiment(i.lower(), '7d')
  print(i, sentiment)