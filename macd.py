
'''

macd.py

Uso:

    python3 macd.py 1d 12 26

Sobre:

    Calcula a efetividade da estratégia MACD para um conjunto de ativos.

    Ponto de compra: Diferença entre as médias se torna positiva.
    Ponto de venda: Diferença entre as médias se torna negativa.

    Dados computados:

        1. Número de operações
        2. Taxa de operações bem sucedidas (com lucro)
        3. Montante final (mil reais sendo reinvestidos continuamente)
        4. Retorno com a estratégia média-preço
        5. Retorno com a estratégia Buy & Hold
        6. Maior ganho com média-preço
        7. Maior perda com média-preço

    O agregado de todos os ativos é salvo no arquivo:

        './operacoes/macd/MACD-{CURTA}-{RÁPIDA}/{INTERVALO}/agregado.txt'.

'''

import sys
import json
import pandas as pd

from pathlib import Path

# Variáveis e demais definições globais.

tickers_path    = './ativos-selecionados.txt'
timeseries_path = './dados/yahoo/'
trades_path     = './operacoes/'

# Parâmetros de entrada do programa:
# Intervalo dos candles (dia, semana ou mês).
# Comprimento da média móvel curta.
# Comprimento da média móvel longa.

interval  = sys.argv[1]
fast_length = int(sys.argv[2])
slow_length = int(sys.argv[3])

# Cria os diretórios no caminho de escrita dos arquivos.

output_path  = './operacoes/macd/MACD-'
output_path += str(fast_length) + '-'
output_path += str(slow_length) + '/'
output_path += interval + '/'

Path(output_path).mkdir(parents=True, exist_ok=True)

aggregate_file_path = output_path + 'agregado.txt'
aggregate_file = open(aggregate_file_path, 'w')

# Abre a carrega a lista de tickers a partir do arquivo especificado.

tickers_file = open(tickers_path, 'r')
tickers = [t.strip().upper() for t in tickers_file.readlines()]
tickers_file.close()

# Iteramos sobre a lista de tickers executando a estratégia.

for ticker in tickers:

    # Carregar a série temporal do ativo em um dataframe da Pandas.

    input_path = (timeseries_path + interval + '/' + ticker + '.json')
    input_file = open(input_path, 'r')
    timeseries = json.load(input_file)
    input_file.close()

    df = pd.DataFrame(timeseries)

    df["adj_close"] = pd.to_numeric(df["adj_close"])

    # Calcular as médias móveis exponenciais (curta e longa).

    fast_moving_average = [df['adj_close'].iloc[0]]
    slow_moving_average = [df['adj_close'].iloc[0]]

    for i, session in df.iloc[1:].iterrows():

        close = session['adj_close']

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
        current_close = session['adj_close']

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

    trades = []

    budget = 1000
    amount = budget

    count = 0
    success = 0
    best_win = 0
    worst_loss = 0

    if len(crossovers) > 1:

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

                count += 1
                success += 1 if profit > 0 else 0
                best_win = max(best_win, result)
                worst_loss = min(worst_loss, result)

                trades.append({})

                trades[-1]['compra_data']   = trade_date
                trades[-1]['compra_preço']  = trade_price
                trades[-1]['venda_data']    = date
                trades[-1]['venda_preço']   = price
                trades[-1]['resultado']     = '{:.2f}%'.format(result * 100)
                trades[-1]['no_pregões']    = duration

            trade_date = date
            trade_side = side
            trade_price = price
            trade_session = session

    fst_price = df['adj_close'].iloc[0]
    lst_price = df['adj_close'].iloc[-1]

    success_rate = 0 if count == 0 else (success / count)
    estrategy_result = (amount / budget) - 1
    buy_n_hold_result = (lst_price / fst_price) - 1

    output  = ticker                                        + ';'
    output += str(count).replace('.', ',')                  + ';'
    output += str(success_rate).replace('.', ',')           + ';'
    output += str(amount).replace('.', ',')                 + ';'
    output += str(estrategy_result).replace('.', ',')       + ';'
    output += str(buy_n_hold_result).replace('.', ',')      + ';'
    output += str(best_win).replace('.', ',')               + ';'
    output += str(worst_loss).replace('.', ',')

    print(output)

    aggregate_file.write(output + '\n')

    # Escrever as operações em um arquivo (para conferência posterior).

    trades_log_path = output_path + ticker + '.json'
    trades_file = open(trades_log_path, 'w')
    trades_file.write(json.dumps(trades))
    trades_file.close()

# Fecha o arquivo contendo o agregado de todos os ativos.

aggregate_file.close()
