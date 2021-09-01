
'''

agregador.py

python3 agregador.py

'''

import sys
import json
import pandas as pd
from datetime import datetime

interval = '1m'

tickers_file = open('./ativos-selecionados.txt', 'r')
tickers = [t.strip().upper() for t in tickers_file.readlines()]
tickers_file.close()

for ticker in tickers:

    data = {}
    output = []

    input_path = './dados/yahoo/1d/' + ticker + '.json'
    input_file = open(input_path, 'r')
    timeseries = json.load(input_file)
    input_file.close()

    df = pd.DataFrame(timeseries)

    df['open']   = pd.to_numeric(df['open'])
    df['close']  = pd.to_numeric(df['close'])
    df['low']    = pd.to_numeric(df['low'])
    df['high']   = pd.to_numeric(df['high'])
    df['volume'] = pd.to_numeric(df['volume'])

    for i, session in df.iterrows():

        ck = ''
        dt = session['date']
        dt = datetime.strptime(dt, '%d-%m-%Y')

        if interval == '1w':

            week_of_the_year = dt.isocalendar()[1]
            ck = str(dt.year) + '-' + str(week_of_the_year)

        elif interval == '1m':

            ck = str(dt.year) + '-' + str(dt.month)

        if ck not in data:

            data[ck] = []

        data[ck].append(session)

    for key in data.keys():

        output.append({})

        output[-1]['date']    = data[key][0]['date']
        output[-1]['open']    = data[key][0]['open']
        output[-1]['close']   = data[key][-1]['close']
        output[-1]['low']     = min([x['low'] for x in data[key]])
        output[-1]['high']    = max([x['high'] for x in data[key]])
        output[-1]['volume']  = sum([x['volume'] for x in data[key]])

    output_path = './dados/yahoo/' + interval + '/' + ticker + '.json'
    output_file = open(output_path, 'w')
    output_file.write(json.dumps(output))
    output_file.close()
