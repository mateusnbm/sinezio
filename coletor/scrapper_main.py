
'''

scrapper_main.py

'''

import os
import time
import json
import errno

from bs4 import BeautifulSoup
from mechanize import Browser
from datetime import datetime, timedelta

from scrapper_conveniences import is_number
from scrapper_conveniences import format_advfn_date, format_advfn_number

def get_advfn_code(ticker):

    browser = Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', 'Linux i686; en-US')]
    browser.open('https://br.advfn.com/bolsa-de-valores/busca')

    browser.select_form(nr=0)
    browser["symbol"] = ticker
    browser.submit()

    url = browser.geturl()
    url_components = url.split('/')

    return (url_components[-2] if url_components[-1] == 'cotacao' else None)

def get_quote_on_advfn(advfn_code, date):

    quotes = []

    quotes_page_url  = 'https://br.advfn.com/bolsa-de-valores/bovespa/'
    quotes_page_url += advfn_code + '/'
    quotes_page_url += 'historico/mais-dados-historicos'

    browser = Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', 'Linux i686; en-US')]
    browser.open(quotes_page_url)

    date_format = '%d/%m/%y'

    start_date = datetime(date.year, date.month, 1)
    end_year = (date.year + 1) if date.month == 12 else date.year
    end_month = 1 if date.month == 12 else (date.month + 1)
    end_date = datetime(end_year, end_month, 1) - timedelta(days=1)

    start_date_string = start_date.strftime(date_format)
    end_date_string = end_date.strftime(date_format)

    browser.select_form(nr=1)
    browser["Date1"] = start_date_string
    browser["Date2"] = end_date_string

    response = browser.submit()

    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find(class_='histo-results')

    if table is None:

        return quotes

    for row in table.find_all('tr')[1:]:

        cols = row.find_all('td')

        if len(cols) < 8: continue

        row_date    = format_advfn_date(cols[0].text.strip())
        row_close   = format_advfn_number(cols[1].text.strip())
        row_open    = format_advfn_number(cols[4].text.strip())
        row_high    = format_advfn_number(cols[5].text.strip())
        row_low     = format_advfn_number(cols[6].text.strip())
        row_volume  = format_advfn_number(cols[7].text.strip())

        if row_date == None:

            print('[quoter_quote] get_quote_on_advfn() - Unable to format date.')
            print('[quoter_quote] get_quote_on_advfn() - Date: ' + str(date) + '.')

        elif is_number(row_close) == False:

            print('[quoter_quote] get_quote_on_advfn() - Unable to format numbers.')
            print('[quoter_quote] get_quote_on_advfn() - Date: ' + str(date) + '.')

        elif int(row_volume.replace('.', '')) > 0:

            quotes.append({})

            quotes[-1]['date']      = row_date
            quotes[-1]['open']      = row_open
            quotes[-1]['close']     = row_close
            quotes[-1]['low']       = row_low
            quotes[-1]['high']      = row_high
            quotes[-1]['volume']    = row_volume

    return quotes

def get_month_quotes(ticker, date, advfn_code=None):

    result = None
    database = {}

    date_format = '%d/%m/%Y'
    date_string = date.strftime(date_format)

    if advfn_code is None: advfn_code = get_advfn_code(ticker)
    if advfn_code is None: return None

    return get_quote_on_advfn(advfn_code, date)
