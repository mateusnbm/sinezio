
'''

main.py

python3 main.py LWSA3 rectangle

'''

import sys
import json

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ticker = sys.argv[1]
figure = sys.argv[2]

# Load company trading sessions dataset.

input_path = './data/' + ticker + '.json'
input_file = open(input_path, 'r')
timeseries = json.load(input_file)
input_file.close()

df = pd.DataFrame(timeseries)

df['date']  = pd.to_datetime(df['date'])
df["low"]   = pd.to_numeric(df["low"])
df["high"]  = pd.to_numeric(df["high"])
df["open"]  = pd.to_numeric(df["open"])
df["close"] = pd.to_numeric(df["close"])

# Plot the Open-high-low-close chart.

figure, axes = plt.subplots(1, figsize=(12, 6))

for i, session in df.iterrows():

    open    = session['open']
    high    = session['high']
    low     = session['low']
    close   = session['close']
    color   = '#2CA453' if close > open else '#F04730'

    plt.plot([i, i], [low, high], color=color)
    plt.plot([i, (i - 0.1)], [open, open], color=color)
    plt.plot([i, (i + 0.1)], [close, close], color=color)

# Discover rectangles.

rectangles = []

for i, session in df.iterrows():

    #if i != 3: continue

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

# Show the chart.

plt.show(block=False)

# Plot rectangles.

#rectangles.append([7, 35, 25, 28.15])

for r in rectangles:

    a = plt.plot([r[0]-0.5, r[1]+0.5], [r[2], r[2]], color='black')
    b = plt.plot([r[0]-0.5, r[1]+0.5], [r[3], r[3]], color='black')
    c = plt.plot([r[0]-0.5, r[0]-0.5], [r[2], r[3]], color='black')
    d = plt.plot([r[1]+0.5, r[1]+0.5], [r[2], r[3]], color='black')

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
