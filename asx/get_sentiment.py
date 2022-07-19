#import libraries
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import pandas as pd
import matplotlib.pyplot as plt
from IPython import get_ipython
ipy = get_ipython()
if ipy is not None:
    ipy.run_line_magic('matplotlib', 'inline')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from GoogleNews import GoogleNews 
from newspaper import Article
from newspaper import Config
import pandas as pd
import nltk

def GetSentiment(tickers, p):
    global googlenews
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    config = Config()
    config.browser_user_agent = user_agent
    googlenews = GoogleNews(lang='en', period=p)
    googlenews.search(tickers)
    result = googlenews.result()
    df = pd.DataFrame(result)
    for i in range(1,10):
        googlenews.getpage(i)
        result=googlenews.result()
        df=pd.DataFrame(result)
        print(df)
    articles = []
    for score_index in df.index:
        try:
            dict={}
            article = Article(df['link'][score_index],config=config)
            article.download()
            article.parse()
            article.nlp()
            articles.append(article.summary)
        except:
            pass
            

    v = SentimentIntensityAnalyzer()

    #set column names
    columns = ['headline']

    #convert the parsed_news list into a DataFrame called 'parsed_and_scored_news'
    parsed_and_scored_news = pd.DataFrame(articles, columns=columns)

    #iterate through the headlines and get the polarity scores using vader
    scores = parsed_and_scored_news['headline'].apply(v.polarity_scores).tolist()

    comp = []

    for i in scores:
        comp.append(i.get('compound'))

    cp = sum(comp)/len(comp)
    return cp
