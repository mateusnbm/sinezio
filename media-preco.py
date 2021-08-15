
'''

media-preco.py

python3 media-preco.py

'''

import sys
import json

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from datetime import datetime

results = []

tickers_file = open('./ativos.txt', 'r')
tickers = [t.strip().upper() for t in tickers_file.readlines()]
tickers_file.close()

for ticker in tickers:

    input_path = './data/' + ticker + '.json'
    input_file = open(input_path, 'r')
    timeseries = json.load(input_file)
    input_file.close()

    df = pd.DataFrame(timeseries)

    df["close"] = pd.to_numeric(df["close"])

    # Calcular a média móvel.

    length = 200
    moving_average = []

    for i, session in df.iterrows():

        close = session['close']

        d = length if i >= length else (i + 1)
        v = df.iloc[(i-d+1):(i+1)]['close'].tolist()
        s = sum(v)

        moving_average.append(s / d)

    # Determinar os pontos de cruzamento.

    crossings = []

    for i, session in df.iterrows():

        if i == 0: continue
        if i < (length-1): continue

        date = session['date']
        current_close = session['close']
        previous_close = df.iloc[i-1]['close']

        current_ma = moving_average[i]
        previous_ma = moving_average[i-1]

        if previous_ma > previous_close and current_close > current_ma:

            crossings.append([date, 'buy', current_close, i])

        elif previous_close > previous_ma and current_ma > current_close:

            crossings.append([date, 'sell', current_close, i])

    # Determinar as operações.

    if len(crossings) < 2:

        print(ticker + ';0;0')

        continue 

    count = 0
    success = 0
    purchases = 0
    sells = 0

    trade_date = crossings[0][0]
    trade_side = crossings[0][1]
    trade_price = crossings[0][2]
    trade_session = crossings[0][3]

    for cross in crossings[1:]:

        date  = cross[0]
        side  = cross[1]
        price = cross[2]
        session = cross[3]

        if trade_side == 'buy':

            profit = price - trade_price
            result = (price / trade_price) - 1
            duration = session - trade_session

            purchases += trade_price
            sells += price

            count += 1
            success += 1 if profit > 0 else 0

        elif trade_side == 'sell':

            profit = trade_price - price
            result = (trade_price / price) - 1
            duration = session - trade_session

            #purchases += price
            #sells += trade_price

            #count += 1
            #success += 1 if profit > 0 else 0

        trade_date = date
        trade_side = side
        trade_price = price
        trade_session = session

        #count += 1
        #success += 1 if profit > 0 else 0

    #print('count: ' + str(count))
    #print('success: ' + str(success))
    #print('result: ' + str((sells/purchases)-1))

    output  = ticker + ';'
    output += str(success/count).replace('.', ',') + ';'
    output += str((sells/purchases)-1).replace('.', ',')

    print(output)
