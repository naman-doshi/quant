# quant — a general repository for all my quantitative analysis/trading projects. Work in progress.

## dydx
Cryptocurrency bot that works on the exchange dYdX, and trades cryptocurrencies that have a high bid/ask spread, have sufficient volume, have strong technicals, and more. A dynamic algorithm then determines the optimal place to set a limit order (opening the trade) to maximise profitability and minimise idle time. After a position is opened at roughly the maximum permissible leverage for that market, a very similar dynamic algorithm is used to close the position. Ideally, the bot can quickly buy near the top of the orderbook and sell near the bottom of the orderbook while still making a profit.

Factors used in finding a symbol
 - Popularity on r/CryptoCurrency
 - Popularity on Google (using Google Trends)
 - The Fear and Greed index, and using a cubic spline function to turn it into a buy/sell signal
 - Technicals: RSI, TSI, and MACD for now
 - Spread
 - Volume

Libraries used
 - Scipy
 - PRAW
 - ta-lib
 - smtplib
 - dydx3
 - Web3

Disclaimer: I am still testing it with paper funds and it is not fully profitable yet, while there are a few bugs I need to fix. I would not recommend running this bot.

## ASX
A program that I am currently using to preliminarily screen stocks of interest for the ongoing ASX Sharemarket Game. It technically analyses all in-game stocks using RSI, TSI, and MACD, and sorts then them in a dictionary for my viewing.

