
'''

scrapper_yahoo.py

python3 scrapper_yahoo.py 1d  ../dados/yahoo/
python3 scrapper_yahoo.py 1mo ../dados/yahoo/
python3 scrapper_yahoo.py 3mo ../dados/yahoo/

'''

import sys
import json
import datetime
import yfinance as finance

interval = sys.argv[1]
given_path = sys.argv[2]

tickers_file = open('../ativos-ibovespa.txt', 'r')
tickers = tickers_file.readlines()
tickers_file.close()

for ticker in tickers:

    data = []

    print(ticker.strip())

    timeseries_df = finance.download(
        tickers=(ticker.strip() + '.SA'),
        start='2015-01-01',
        end='2021-07-01',
        interval=interval,
        progress=False
        )

    for index, row in timeseries_df.iterrows():

        if row.isnull().values.any(): continue

        t_open   = row['Open']
        t_close  = row['Adj Close']
        t_low    = row['Low']
        t_high   = row['High']
        t_volume = ((t_open + t_close + t_low + t_high) / 4) * row['Volume']

        data.append({})

        data[-1]['date']    = index.to_pydatetime().strftime("%d-%m-%Y")
        data[-1]['open']    = t_open
        data[-1]['close']   = t_close
        data[-1]['low']     = t_low
        data[-1]['high']    = t_high
        data[-1]['volume']  = t_volume

    output_path = given_path + interval + '/' + ticker.strip() + '.json'
    output_file = open(output_path, 'w')
    output_file.write(json.dumps(data))
    output_file.close()
