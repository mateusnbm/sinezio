
'''

scrapper_scrap.py

python3 scrapper_scrap.py LWSA3 19/06/2021 ../data/

'''

import sys
import json
import time

from datetime import datetime, timedelta
from scrapper_main import get_month_quote


timeseries = []

ticker = sys.argv[1]
date_string = sys.argv[2]
output_path = sys.argv[3]

date_format = '%d/%m/%Y'
given_date = datetime.strptime(date_string, date_format).date()
loop_date = datetime(given_date.year, given_date.month, 1)
current_date = datetime.now()

while loop_date < current_date:

    quotes = get_month_quote(ticker, loop_date)

    if quotes == None:

        print('Unable to retrieve quotes starting from ' + str(loop_date))

    else:

        timeseries = timeseries + list(reversed(quotes))

    next_year = (loop_date.year + 1) if loop_date.month == 12 else loop_date.year
    next_month = 1 if loop_date.month == 12 else (loop_date.month + 1)
    loop_date = datetime(next_year, next_month, 1)

output_path = output_path + ticker + '.json'
output_file = open(output_path, 'w')
output_file.write(json.dumps(timeseries))
output_file.close()
