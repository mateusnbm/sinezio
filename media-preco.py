
'''

media-preco.py

python3 media-preco.py

'''

import json
import pandas as pd

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

    length = 21
    moving_average = []

    for i, session in df.iterrows():

        close = session['close']

        d = length if i >= length else (i + 1)
        v = df.iloc[(i-d+1):(i+1)]['close'].tolist()
        s = sum(v)

        moving_average.append(s / d)

    # Determinar os pontos de cruzamento.

    crossovers = []

    for i, session in df.iterrows():

        if i == 0: continue
        if i < (length-1): continue

        date = session['date']
        current_close = session['close']
        previous_close = df.iloc[i-1]['close']

        current_ma = moving_average[i]
        previous_ma = moving_average[i-1]

        if previous_ma > previous_close and current_close > current_ma:

            crossovers.append([date, 'buy', current_close, i])

        elif previous_close > previous_ma and current_ma > current_close:

            crossovers.append([date, 'sell', current_close, i])

    # Determinar as operações.

    if len(crossovers) < 2:

        print(ticker + ';0;0')

        continue

    count = 0
    success = 0
    purchases = 0
    sells = 0

    trade_date = crossovers[0][0]
    trade_side = crossovers[0][1]
    trade_price = crossovers[0][2]
    trade_session = crossovers[0][3]

    for cross in crossovers[1:]:

        date = cross[0]
        side = cross[1]
        price = cross[2]
        session = cross[3]

        if trade_side == 'buy':

            profit = price - trade_price
            result = (price / trade_price) - 1
            duration = session - trade_session

            purchases += trade_price
            sells += price

            #count += 1
            #success += 1 if profit > 0 else 0

            #print('Operação comprada.')
            #print('Data da compra: ' + str(trade_date))
            #print('Preço de compra: ' + str(trade_price))
            #print('Data da venda: ' + str(date))
            #print('Preço de venda: ' + str(price))
            #print('Lucro: ' + str(profit))
            #print('Resultado: ' + str(result))
            #print('Duração: ' + str(duration))
            #print('')

        elif trade_side == 'sell':

            profit = trade_price - price
            result = (trade_price / price) - 1
            duration = session - trade_session

            purchases += price
            sells += trade_price

            #count += 1
            #success += 1 if profit > 0 else 0

            #print('Operação vendida.')
            #print('Data da venda: ' + str(trade_date))
            #print('Preço de venda: ' + str(trade_price))
            #print('Data da compra: ' + str(date))
            #print('Preço de compra: ' + str(price))
            #print('Lucro: ' + str(profit))
            #print('Resultado: ' + str(result))
            #print('Duração: ' + str(duration))
            #print('')

        trade_date = date
        trade_side = side
        trade_price = price
        trade_session = session

        count += 1
        success += 1 if profit > 0 else 0

    #print('count: ' + str(count))
    #print('success: ' + str(success))
    #print('result: ' + str((sells/purchases)-1))

    output  = ticker + ';'
    output += str(success/count).replace('.', ',') + ';'
    output += str((sells/purchases)-1).replace('.', ',')

    print(output)
