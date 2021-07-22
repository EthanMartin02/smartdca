import pandas as pd
import cbpro
import os

# turn all your magic numbers into variables here for easier tweaking
# ex: percentLimit = 5, upperLimit = 60000, etc.

# Set up cbpro API authentication with environmental variables and
# initialize the client.
def cbproAPISetup():
    apiKey = os.environ.get('cbpro_api_key')
    apiSecret = os.environ.get('cbpro_api_secret')
    apiPassword = os.environ.get('cbpro_api_pw')
    auth_client = cbpro.AuthenticatedClient(apiKey, apiSecret, apiPassword)
    return auth_client

# Generates the percent gain/loss for the current day.
def getPercent(open, last):
    return round(((last-open)/open) * 100, 2)

# Using the limits provided, decides to either buy, sell, or
# do nothing depending on if the price and percent gain/loss
# of the day meet the proper criteria.
def smartdca(client, percentLimit, upperLimit, lowerLimit, orderSize, exchange):
    # check the last purchase date
    # if < 24 hours:
        # if down 5% from last buy:
            # smart dca again
        # else:
            # quit
    # else:
    # below code is fine
    currStats = client.get_product_24hr_stats(exchange)
    open = float(currStats['open'])
    last = float(currStats['last'])
    percent = getPercent(open, last)
    if (abs(percent) >= percentLimit):
        if (percent > 0):
            if (last > upperLimit):
                print("buy $" + orderSize + " " + exchange)
        else:
            if (last < lowerLimit):
                print("sell $" + orderSize + " " + exchange)

# Driver of the program. This is where the limits for percentages
# and prices can be set. The smartdca method can be called for
# any valid exchange as well.
def main():
    client = cbproAPISetup()
    print("run btc")
    smartdca(client, 5, 60000, 35000, 20, 'BTC-USD')
    print("run eth")
    smartdca(client, 5, 3000, 2200, 30, 'ETH-USD')
    

main()