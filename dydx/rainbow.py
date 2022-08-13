import bs4
import urllib.request
profit = 100

url = "https://www.blockchaincenter.net/en/bitcoin-rainbow-chart/"
url_contents = urllib.request.urlopen(url).read()

soup = bs4.BeautifulSoup(url_contents, "html")
div = soup.find("div", {"class": "legend"})
active = div.find("span", {"class": "active"})
content = str(active)

multiplier = 0
if 'Seriously' in content:
  multiplier = 0.1
elif 'FOMO' in content: 
  multiplier = 0.2
elif 'Is this a' in content:
  multiplier = 0.35
elif 'HODL' in content:
  multiplier = 0.5
elif 'cheap' in content:
  multiplier = 0.75
elif 'Accumulate' in content:
  multiplier = 1
elif 'BUY' in content: 
  multiplier = 1.5
elif 'Fire' in content:
  multiplier = 2.5

toBuy = profit*multiplier
proton = toBuy * (1/6)
bitcoin = toBuy * (5/6)
print(proton)
print(bitcoin)