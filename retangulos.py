
'''

retangulos.py

Uso:

    python3 retangulos.py BBDC4 1d 14

Sobre:

    ...

'''

import sys
import json

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from pathlib import Path
from datetime import datetime

# Variáveis e demais definições globais.

timeseries_path = './dados/yahoo/'
trades_path     = './operacoes/'

# Parâmetros de entrada do programa:
# Ticker da empresa.
# Intervalo dos candles (dia, semana ou mês).
# Comprimento da média móvel do volume.

ticker = sys.argv[1]
interval  = sys.argv[2]
volume_ma_length = int(sys.argv[3])

# Cria os diretórios no caminho de escrita dos arquivos.

output_path  = './operacoes/retangulos/'
output_path += 'MM-VOL-' + str(volume_ma_length) + '/'
output_path += interval + '/'

Path(output_path).mkdir(parents=True, exist_ok=True)

# Carregar a série temporal do ativo em um dataframe da Pandas.

input_path = (timeseries_path + interval + '/' + ticker + '.json')
input_file = open(input_path, 'r')
timeseries = json.load(input_file)
input_file.close()

df = pd.DataFrame(timeseries)

df['date']  = pd.to_datetime(df['date'], format='%d-%m-%Y')
df["low"]   = pd.to_numeric(df["low"])
df["high"]  = pd.to_numeric(df["high"])
df["open"]  = pd.to_numeric(df["open"])
df["close"] = pd.to_numeric(df["close"])
df["volume"] = pd.to_numeric(df["volume"])

#df = df[(df['date']> "2021-01-01")]
#df = df.reset_index(drop=True)

# Calcular a média móvel do volume.

volume_moving_average = []

for i, session in df.iterrows():

    d = volume_ma_length if i >= volume_ma_length else (i + 1)
    v = df.iloc[(i-d+1):(i+1)]['volume'].tolist()
    s = sum(v)

    volume_moving_average.append(s / d)

# Descobrir retângulos.

rectangles = []

for i, session in df.iterrows():

    hits_threshold = 3
    diff_threshold = 0.0075
    wave_threshold = 0.01

    support_hits = 1
    resistance_hits = 1

    support_lock = True
    resistance_lock = True

    support = session['low']
    resistance = session['high']

    for j, next_session in df.iloc[(i+1):].iterrows():

        low = next_session['low']
        high = next_session['high']
        close = next_session['close']

        support_top_margin = support * (1 + diff_threshold)
        support_bottom_margin = support * (1 - diff_threshold)

        resistance_top_margin = resistance * (1 + diff_threshold)
        resistance_bottom_margin = resistance * (1 - diff_threshold)

        if low > support_bottom_margin and low < support_top_margin and support_lock == False:

            support_hits += 1
            support_lock = True

        elif low > (support_top_margin * (1 + wave_threshold)):

            support_lock = False

        elif low < support_bottom_margin:

            if resistance_hits >= hits_threshold and support_hits >= hits_threshold:

                fst_high = df.iloc[i]['high']

                if fst_high > resistance_bottom_margin and close < support_bottom_margin:

                    rectangles.append([i, j, support, resistance])

            support_hits = 1
            support_lock = True
            support = low

        if high > resistance_bottom_margin and high < resistance_top_margin and resistance_lock == False:

            resistance_hits += 1
            resistance_lock = True

        elif high < (resistance_bottom_margin * (1 - wave_threshold)):

            resistance_lock = False

        elif high > resistance_top_margin:

            if resistance_hits >= hits_threshold and support_hits >= hits_threshold:

                fst_low = df.iloc[i]['low']

                if fst_low < support_top_margin and close > resistance_top_margin:

                    rectangles.append([i, j, support, resistance])

            resistance_hits = 1
            resistance_lock = True
            resistance = high

data = []

for rectangle in rectangles:

    data.append([rectangle[0], rectangle[1], rectangle[2], rectangle[3]])

trades_log_path = output_path + ticker + '.json'
trades_file = open(trades_log_path, 'w')
trades_file.write(json.dumps(data))
trades_file.close()
