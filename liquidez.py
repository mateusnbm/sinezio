
'''

liquidez.py

python3 liquidez.py

'''

import json
import pandas as pd

data = []

tickers_file = open('./ativos-ibovespa.txt', 'r')

for line in tickers_file.readlines():

    ticker = line.strip().upper()

    input_path = './dados/yahoo/1d/' + ticker + '.json'
    input_file = open(input_path, 'r')
    timeseries = json.load(input_file)
    input_file.close()

    df = pd.DataFrame(timeseries)

    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])

    n_rows = len(df.index)
    v_mean = int(df['volume'].tail(min(n_rows, 100)).mean())

    data.append([ticker, n_rows, v_mean])

data.sort(key=lambda x: x[2], reverse=True)

for i, entry in enumerate(data):

    print('{:3d} {:6s} {:5d} {:12.2f}'.format(i, entry[0], entry[1], entry[2]))

tickers_file.close()
