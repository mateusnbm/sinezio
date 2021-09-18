
'''

media-preco-mmm.py

Uso:

    python3 media-preco-mmm.py 1d

Sobre:

    Calcula a efetividade da estratégia média-preço para um conjunto de ativos.

    São testados múltiplos comprimentos da média móvel e o melhor é escolhido.

    Ponto de compra: Média cruza preço para cima.
    Ponto de venda: Média cruza preço para baixo.

    Dados computados:

        1. Número de operações
        2. Taxa de operações bem sucedidas (com lucro)
        3. Montante final (mil reais sendo reinvestidos continuamente)
        4. Retorno com a estratégia média-preço
        5. Retorno com a estratégia Buy & Hold
        6. Maior ganho com média-preço
        7. Maior perda com média-preço

    O agregado de todos os ativos é salvo no arquivo:

        './operacoes/media-preço/MMM/{INTERVALO}/agregado.txt'.

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

interval  = sys.argv[1]

# Cria os diretórios no caminho de escrita dos arquivos.

output_path  = './operacoes/media-preço/'
output_path += 'MMM/'
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

    # Calculamos os desempenhos com múltiplos comprimentos da média.

    performances = []

    for length in range(7, 101):

        # Calcular a média móvel.

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

        # Salvar os resultados com tal comprimento em uma lista.

        performances.append([
            length,
            count,
            success_rate,
            amount,
            estrategy_result,
            buy_n_hold_result,
            best_win,
            worst_loss
        ])

    # Ordenar a lista de resultados.

    performances.sort(key=lambda x: x[3], reverse=True)

    # Escrever o melhor resultado no arquivo de resultados agregados.

    output  = ticker                                    + ';'
    output += str(performances[0][0]).replace('.', ',') + ';'
    output += str(performances[0][1]).replace('.', ',') + ';'
    output += str(performances[0][2]).replace('.', ',') + ';'
    output += str(performances[0][3]).replace('.', ',') + ';'
    output += str(performances[0][4]).replace('.', ',') + ';'
    output += str(performances[0][5]).replace('.', ',') + ';'
    output += str(performances[0][6]).replace('.', ',') + ';'
    output += str(performances[0][7]).replace('.', ',')

    print(output)

    aggregate_file.write(output + '\n')

# Fecha o arquivo contendo o agregado de todos os ativos.

aggregate_file.close()
