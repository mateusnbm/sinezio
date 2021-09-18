
'''

media-media.py

Uso:

    python3 media-media.py 1d 9 21

Sobre:

    Calcula a efetividade da estratégia média-média para um conjunto de ativos.

    Ponto de compra: Média curta cruza a longa para cima.
    Ponto de venda: Média curta cruza a longa para baixo.

    Dados computados:

        1. Número de operações
        2. Taxa de operações bem sucedidas (com lucro)
        3. Montante final (mil reais sendo reinvestidos continuamente)
        4. Retorno com a estratégia média-preço
        5. Retorno com a estratégia Buy & Hold
        6. Maior ganho com média-preço
        7. Maior perda com média-preço

    Os registros de todas as operações por ativo são salvos em:

        './operacoes/media-preço/MM{CURTA}-MM{LONGA}/{INTERVALO}/{TICKER}.json'.

    O agregado de todos os ativos é salvo no arquivo:

        './operacoes/media-preço/MM{CURTA}-MM{LONGA}/{INTERVALO}/agregado.txt'.

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
# Comprimento da média móvel cruta.
# Comprimento da média móvel longa.

interval    = sys.argv[1]
fast_length = int(sys.argv[2])
slow_length = int(sys.argv[3])

# Cria os diretórios no caminho de escrita dos arquivos.

output_path  = './operacoes/media-media/'
output_path += 'MM' + str(fast_length) + '-'
output_path += 'MM' + str(slow_length) + '/'
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

    df["close"] = pd.to_numeric(df["close"])

    # Calcular as médias móveis (curta e longa).

    fast_moving_average = []
    slow_moving_average = []

    for i, session in df.iterrows():

        close = session['close']

        d = fast_length if i >= fast_length else (i + 1)
        v = df.iloc[(i-d+1):(i+1)]['close'].tolist()
        s = sum(v)

        fast_moving_average.append(s / d)

        d = slow_length if i >= slow_length else (i + 1)
        v = df.iloc[(i-d+1):(i+1)]['close'].tolist()
        s = sum(v)

        slow_moving_average.append(s / d)

    # Determinar os pontos de cruzamento.

    crossovers = []

    for i, session in df.iterrows():

        if i == 0: continue
        if i < (slow_length-1): continue

        date = session['date']
        current_close = session['close']

        current_fma = fast_moving_average[i]
        previous_fma = fast_moving_average[i-1]

        current_sma = slow_moving_average[i]
        previous_sma = slow_moving_average[i-1]

        if previous_sma > previous_fma and current_fma > current_sma:

            crossovers.append([date, 'buy', current_close, i])

        elif previous_fma > previous_sma and current_sma > current_fma:

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

    fst_price = df['close'].iloc[0]
    lst_price = df['close'].iloc[-1]

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
