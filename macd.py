
'''

macd.py

python3 macd.py

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

    # Calcular as médias móveis exponenciais (curta e longa).

    fast_length = 12
    slow_length = 26

    fast_moving_average = [df['close'].iloc[0]]
    slow_moving_average = [df['close'].iloc[0]]

    for i, session in df.iterrows():

        if i == 0: continue

        close = session['close']

        l = fast_moving_average[-1]
        m = (close - l) * (2 / (1 + fast_length)) + l

        fast_moving_average.append(m)

        l = slow_moving_average[-1]
        m = (close - l) * (2 / (1 + slow_length)) + l

        slow_moving_average.append(m)

    # Determinar os pontos de cruzamento (cruzando linha do 0).

    crossovers = []

    for i, session in df.iterrows():

        if i == 0: continue
        if i < (slow_length-1): continue

        date = session['date']
        current_close = session['close']

        current_fma = fast_moving_average[i]
        current_sma = slow_moving_average[i]
        current_diff = current_fma - current_sma

        previous_fma = fast_moving_average[i-1]
        previous_sma = slow_moving_average[i-1]
        previous_diff = previous_fma - previous_sma

        if previous_diff < 0 and current_diff > 0:

            crossovers.append([date, 'buy', current_close, i])

        elif previous_diff > 0 and current_diff < 0:

            crossovers.append([date, 'sell', current_close, i])

    # Determinar as operações.

    budget = 1000
    amount = budget

    count = 0
    success = 0
    purchases = 0
    sells = 0
    best_win = 0
    worst_loss = 0

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

            amount = (amount / trade_price) * price

            if amount < 100:

                print('FUCK')
                exit()

            count += 1
            success += 1 if profit > 0 else 0
            purchases += trade_price
            sells += price
            best_win = max(best_win, result)
            worst_loss = min(worst_loss, result)

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

            #purchases += price
            #sells += trade_price

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

    fst_price = df['close'].iloc[0]
    lst_price = df['close'].iloc[-1]

    success_rate = success / count
    average_gain_per_trade = (sells / purchases) - 1
    estrategy_result = (amount / budget) - 1
    buy_n_hold_result = (lst_price / fst_price) - 1

    output  = ticker                                        + ';'
    output += str(success_rate).replace('.', ',')           + ';'
    output += str(average_gain_per_trade).replace('.', ',') + ';'
    output += str(amount).replace('.', ',')                 + ';'
    output += str(estrategy_result).replace('.', ',')       + ';'
    output += str(buy_n_hold_result).replace('.', ',')      + ';'
    output += str(best_win).replace('.', ',')               + ';'
    output += str(worst_loss).replace('.', ',')

    print(output)
