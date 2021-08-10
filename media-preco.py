
'''

media-preco.py

python3 media-preco.py

'''

import sys
import json

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from datetime import datetime

tickers = ['PETR4']

for ticker in tickers:

    # Carregar e transformar os dados do ativo.

    input_path = './data/' + ticker + '.json'
    input_file = open(input_path, 'r')
    timeseries = json.load(input_file)
    input_file.close()

    df = pd.DataFrame(timeseries)

    df["close"] = pd.to_numeric(df["close"])

    # Calcular as médias móveis de 7, 14 e 21 dias.

    moving_averages = {}
    moving_averages[7] = []
    moving_averages[14] = []
    moving_averages[21] = []

    for length in moving_averages.keys():

        for i, session in df.iterrows():

            close = session['close']

            d = length if i >= length else (i + 1)
            v = df.iloc[(i-d+1):(i+1)]['close'].tolist()
            s = sum(v)

            moving_averages[length].append(s / d)

    # Determinar os pontos de cruzamento e, consequentemente, as operações.

    for i, session in df.iterrows():

        if i == 0: continue

        date = session['date']
        current_close = session['close']
        previous_close = df.iloc[i-1]['close']

        print(date)
        print('')

        for length in [7]:# moving_averages.keys():

            current_ma = moving_averages[length][i]
            previous_ma = moving_averages[length][i-1]

            if previous_ma > previous_close and current_close > current_ma:

                # O preço cruzou a média móvel para cima.

                print('Cruzamento para cima.')
                print(date)
                print('')

            elif previous_close > previous_ma and current_ma > current_close:

                print('Cruzamento para baixo')
                print(date)
                print('')

exit()

# Discover rectangles.

rectangles = []

for i, session in df.iterrows():

    diff_threshold = 0.0075
    support_hits = 1
    resistance_hits = 1

    support = session['low']
    resistance = session['high']

    for j, next_session in df.iloc[(i+1):].iterrows():

        low = next_session['low']
        high = next_session['high']

        support_top_margin = support * (1 + diff_threshold)
        support_bottom_margin = support * (1 - diff_threshold)

        resistance_top_margin = resistance * (1 + diff_threshold)
        resistance_bottom_margin = resistance * (1 - diff_threshold)

        if low > support_bottom_margin and low < support_top_margin:

            support_hits += 1

        elif support > low:

            if (j - i) > 3 and resistance_hits >= 2 and support_hits >= 2:

                rectangles.append([i, j, support, resistance])

            support_hits = 1
            support = low

        if high > resistance_bottom_margin and high < resistance_top_margin:

            resistance_hits += 1

        elif resistance < high:

            if (j - i) > 3 and resistance_hits >= 2 and support_hits >= 2:

                rectangles.append([i, j, support, resistance])

            resistance_hits = 1
            resistance = high

# Plot the Open-high-low-close chart with volumes.

dates_index = []
dates_labels = []

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

for i, session in df.iterrows():

    date    = session['date']
    open    = session['open']
    high    = session['high']
    low     = session['low']
    close   = session['close']
    volume  = session['volume']

    b_color = '#2CA453' if close > open else '#F04730'
    v_color = 'lightgrey'

    pri_ax.plot([i, i], [low, high], linewidth=1, color=b_color)
    pri_ax.plot([(i - 0.15), (i + 0.00)], [open, open], color=b_color)
    pri_ax.plot([(i + 0.10), (i + 0.20)], [close, close], color=b_color)

    vol_ax.plot([i, i], [0, volume], linewidth=8, color=v_color)

    if len(dates_index) == 0 or i == (len(df) - 1):

        dates_index.append(i)
        dates_labels.append(date.strftime("%m/%Y"))

    elif i - dates_index[-1] > 3:

        dates_index.append(i)
        dates_labels.append(date.strftime("%d"))

max_volume = df['volume'].max() * 1.1
volume_y_ticks = np.arange(0, (max_volume + 1), (max_volume / 4))
volume_y_labels = ['{:.2f} mi'.format(i/1000000) for i in volume_y_ticks]

vol_ax.set_xticks(dates_index)
vol_ax.set_xticklabels(dates_labels)

vol_ax.plot(x, volume_moving_average, linewidth=1, color='orange')

plt.yticks(volume_y_ticks[1:-1], volume_y_labels[1:-1])
plt.ylim(0, max_volume)

# Show the chart (doesn't block the program).

plt.show(block=False)

pri_ax.set_title(ticker)

# Plot rectangles (on keypress, draw next rectangle).

for r in rectangles:

    a = pri_ax.plot([r[0]-0.5, r[1]+0.5], [r[2], r[2]], color='black')
    b = pri_ax.plot([r[0]-0.5, r[1]+0.5], [r[3], r[3]], color='black')
    c = pri_ax.plot([r[0]-0.5, r[0]-0.5], [r[2], r[3]], color='black')
    d = pri_ax.plot([r[1]+0.5, r[1]+0.5], [r[2], r[3]], color='black')

    plt.draw()

    input('')

    a = a.pop(0)
    b = b.pop(0)
    c = c.pop(0)
    d = d.pop(0)

    a.remove()
    b.remove()
    c.remove()
    d.remove()
