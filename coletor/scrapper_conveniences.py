
'''

scrapper-conveniences.py

'''

'''

Determines if a string can be cast to a number.
Returnes True if it can or, else, returns False.

'''

def is_number(string):

    try:

        float(string)

        return True

    except ValueError:

        return False

'''

Formats numbers from ADVFN's website.
Removes thousands separators (dots).
Replaces commas with dots as decimal separators.

Some examples:

    4,25 ----->    4.25
    4.250 ----> 4250.00
    4.250,25 -> 4250.25

'''

def format_advfn_number(number_string):

    return number_string.strip().replace('.', '').replace(',', '.')

'''

Formats dates from ADVFN's website.
Replaces the name of the months with their respective numbers.
Concatenates day, month and year separated by slashes.

Some examples:

    01 Jan 2020 -> 01/01/2020
    01 Abr 2021 -> 01/04/2021
    01 Zoo 2022 -> None

'''

def format_advfn_date(date_string):

    month = None
    formatted_date = None

    components = date_string.split(' ')
    day = components[0]
    month_name = components[1]
    year = components[2]

    if month_name == 'Jan': month = '01'
    if month_name == 'Fev': month = '02'
    if month_name == 'Mar': month = '03'
    if month_name == 'Abr': month = '04'
    if month_name == 'Mai': month = '05'
    if month_name == 'Jun': month = '06'
    if month_name == 'Jul': month = '07'
    if month_name == 'Ago': month = '08'
    if month_name == 'Set': month = '09'
    if month_name == 'Out': month = '10'
    if month_name == 'Nov': month = '11'
    if month_name == 'Dez': month = '12'

    if month is not None:

        formatted_date = (day + '/' + month + '/' + year)

    return formatted_date
