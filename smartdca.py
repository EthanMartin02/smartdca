import bs4
import pandas as pd
import cbpro
import os
from dateutil import parser
from bs4 import BeautifulSoup
import urllib.request

# Specifications/limits for when to automatically
# buy/sell ethereum and bitcoin.
percentLimit = 5
btcLowerLimit = 35000
btcUpperLimit = 60000
ethLowerLimit = 2200
ethUpperLimit = 4000
btcSize = 20
ethSize = 30

# Set up cbpro API authentication with environmental variables and
# initialize the client.
def cbproAPISetup():
    apiKey = os.environ.get('cbpro_api_key')
    apiSecret = os.environ.get('cbpro_api_secret')
    apiPassword = os.environ.get('cbpro_api_pw')
    sandboxapiKey = os.environ.get('cbpro_sandbox_api_key')
    sandboxapiSecret = os.environ.get('cbpro_sandbox_api_secret')
    sandboxapiPassword = os.environ.get('cbpro_sandbox_api_pw')
    #auth_client = cbpro.AuthenticatedClient(apiKey, apiSecret, apiPassword)
    auth_client = cbpro.AuthenticatedClient(sandboxapiKey, sandboxapiSecret, sandboxapiPassword, api_url="https://api-public.sandbox.pro.coinbase.com")
    return auth_client


# Constants returned by getPercentLimitDecision.
# Represents whether the percent change of the day indicates
# to buy, sell, or do nothing.
SELL = -1
NONE = 0
BUY = 1

# Returns the decision to buy, sell, or do nothing
# based off of the percent change calculated.
def getPercentLimitDecision(open, last):
    percent = round(((last-open)/open) * 100, 2)
    if (percent > percentLimit):
        return SELL
    elif (percent < -percentLimit):
        return BUY
    return NONE

# length of date format used for comparing
# last order date to current date
TIME_FORMAT = len('xxxx-xx-xx')


# Using the limits provided, decides to either buy, sell, or
# do nothing depending on if the price and percent gain/loss
# of the day meet the proper criteria.
def smartdca(client, upperLimit, lowerLimit, orderSize, exchange):
    #balance = float(client.get_account('2d9c32ee-db22-4850-b4c8-c14857b95a1c')['balance'])
    sandboxBalance = float(client.get_account('81c7c3a7-6719-4c62-9bcd-38e7fae325af')['balance'])
    balance = sandboxBalance
    if balance >= 0:
        currStats = client.get_product_24hr_stats(exchange)
        open = float(currStats['open'])
        last = float(currStats['last'])
        fills = list(client.get_fills(product_id=exchange))
        if len(fills) > 0:
            lastFill = fills[0]
            currDay = client.get_time()['iso'][0:TIME_FORMAT]
            lastOrder = lastFill['created_at'][0:TIME_FORMAT]
            # If an order has already been placed for the day,
            # then the price of the last order will be used instead
            # of the open price.
            if currDay == lastOrder:
                open = float(lastFill['price'])
        decision = getPercentLimitDecision(open, last)
        if decision == SELL:
            if (last > upperLimit):
                client.place_market_order(product_id=exchange,
                                            side='sell',
                                            funds=str(orderSize))
                print("buy $" + str(orderSize) + " " + exchange)
        elif decision == BUY:
            if (last < lowerLimit):
                client.place_market_order(product_id=exchange,
                            side='buy',
                            funds=str(orderSize))
                print("sell $" + str(orderSize) + " " + exchange)

# Driver of the program. This is where the limits for percentages
# and prices can be set. The smartdca method can be called for
# any valid exchange as well.
def main():
    client = cbproAPISetup()
    print("run btc")
    smartdca(client, btcUpperLimit, btcLowerLimit, btcSize, 'BTC-USD')
    print("run eth")
    #smartdca(client, ethUpperLimit, ethLowerLimit, ethSize, 'ETH-USD')
    lastFill = list(client.get_orders())
    currTime = parser.parse(client.get_time()['iso'])
    

main()