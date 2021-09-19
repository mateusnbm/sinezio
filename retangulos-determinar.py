
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

# ...

for r in rectangles:

    new_fst_i = r[0] - 5
    new_lst_i = r[1] + 5

    new_r_i = 5
    new_r_j = 5 + r[1] - r[0]

    new_fst_date = df.iloc[new_fst_i]['date']
    new_lst_date = df.iloc[new_lst_i]['date']

    clipped_volume_moving_average = volume_moving_average[new_fst_i:new_lst_i+1]

    clipped_df = df[(df['date'] >= new_fst_date) & (df['date'] <= new_lst_date)]
    clipped_df = clipped_df.reset_index(drop=True)

    x = np.arange(0, len(clipped_df))

    # ...

    dates_indexes = []
    dates_labels = []

    months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

    for i, session in clipped_df.iterrows():

        date = session['date']

        if i == 0:

            month = months[date.month-1]
            label = month + '/' + str(date.year)[-2:]

            dates_indexes.append(i)
            dates_labels.append(label)

        elif date.month != clipped_df.iloc[i-1]['date'].month:

            month = months[date.month-1]
            label = month

            dates_indexes.append(i)
            dates_labels.append(label)

        elif i - dates_indexes[-1] > 5:

            mi = min(len(clipped_df)-1, i+4)

            if date.month == clipped_df.iloc[mi]['date'].month:

                dates_indexes.append(i)
                dates_labels.append(date.strftime("%d"))

    # ...

    grid_specs = {
        'height_ratios': [4, 1],
        'hspace':0
        }

    figure, (pri_ax, vol_ax) = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(12, 6),
        gridspec_kw=grid_specs
        )

    for i, session in clipped_df.iterrows():

        date    = session['date']
        open    = session['open']
        high    = session['high']
        low     = session['low']
        close   = session['close']
        volume  = session['volume']

        b_color = '#2CA453' if close > open else '#F04730'

        pri_ax.plot([i, i], [low, high], linewidth=1, color=b_color)
        pri_ax.plot([(i - 0.15), (i + 0.00)], [open, open], color=b_color)
        pri_ax.plot([(i + 0.10), (i + 0.20)], [close, close], color=b_color)

        vol_ax.plot([i, i], [0, volume], linewidth=1, color='lightgrey')

    max_volume = clipped_df['volume'].max() * 1.1
    volume_y_ticks = np.arange(0, (max_volume + 1), (max_volume / 4))
    volume_y_labels = ['{:.0f} mi'.format(i/1000000) for i in volume_y_ticks]

    pri_ax.set_title(ticker)

    vol_ax.set_xticks(dates_indexes)
    vol_ax.set_xticklabels(dates_labels)

    vol_ax.plot(x, clipped_volume_moving_average, linewidth=1, color='orange')

    #plt.yticks(volume_y_ticks[1:-1], volume_y_labels[1:-1])
    #plt.ylim(0, max_volume)

    pri_ax.plot([new_r_i-0.5, new_r_j+0.5], [r[2], r[2]], color='black')
    pri_ax.plot([new_r_i-0.5, new_r_j+0.5], [r[3], r[3]], color='black')
    pri_ax.plot([new_r_i-0.5, new_r_i-0.5], [r[2], r[3]], color='black')
    pri_ax.plot([new_r_j+0.5, new_r_j+0.5], [r[2], r[3]], color='black')

    #plt.draw()
    plt.show()
