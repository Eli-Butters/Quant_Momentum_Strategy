import numpy as np
import pandas as pd
import requests
import math
from scipy.stats import percentileofscore as score
from statistics import mean

#FUNCTIONS

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def portfolio_input():
    portfolio_size = input('Enter the value of your portfolio:')

    try:
        val = float(portfolio_size)
    except ValueError: 
        print("That's not a number! /nPlease try again")
        portfolio_size = input('Enter the value of your portfolio:')
        val = float(portfolio_size)

    position_size = val/len(hqm_df.index)

    for i in range(len(hqm_df.index)):
        hqm_df.loc[i, 'Shares'] = math.floor(position_size/hqm_df.loc[i, 'Price'])

#DECLARATIONS

stocks = pd.read_csv('sp_500_stocks.csv')
IEX_CLOUD_API_TOKEN = 'sk_88ede6c864fb433a92ac08d2ab9e555a'

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

#HQM Momentum

hqm_colums = [
    'Ticker', 
    'Price', 
    'Shares', 
    'One-Year Price Return', 
    'One-Year Return Percentile', 
    'Six-Month Price Return',
    'Six-Month Return Percentile',
    'Three-Month Price Return',
    'Three-Month Return Percentile',
    'One-Month Price Return',
    'One-Month Return Percentile',
    'HQM Score'
    ]

hqm_df = pd.DataFrame(columns = hqm_colums)

count = 0
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote,stats&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        hqm_df.loc[count] = [
            symbol, 
            data[symbol]['quote']['latestPrice'], 
            'N/A', 
            data[symbol]['stats']['year1ChangePercent'], 
            'N/A', 
            data[symbol]['stats']['month6ChangePercent'],
            'N/A',
            data[symbol]['stats']['month3ChangePercent'],
            'N/A',
            data[symbol]['stats']['month1ChangePercent'],
            'N/A',
            'N/A'
        ]
        count += 1

time_periods = [
    'One-Year',
    'Six-Month',
    'Three-Month',
    'One-Month'
]

#CORRECTING ERRORS

for row in hqm_df.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Return'
        percentile_col = f'{time_period} Return Percentile'
        if hqm_df.loc[row, change_col] == None:
            hqm_df.loc[row, change_col] = 0

#CALCULATING PERCENTILEOFSCORE

for row in hqm_df.index:
    for time_period in time_periods:
        change_col = f'{time_period} Price Return'
        percentile_col = f'{time_period} Return Percentile'
        hqm_df.loc[row, percentile_col] = score(hqm_df[change_col], hqm_df.loc[row, change_col])

#ASSIGNING HQM SCORE

for row in hqm_df.index:
    momentum_percentile = []
    for time_period in time_periods:
        momentum_percentile.append(hqm_df.loc[row, f'{time_period} Return Percentile'])
    hqm_df.loc[row, 'HQM Score'] = mean(momentum_percentile)

hqm_df.sort_values('HQM Score', ascending = False, inplace = True)
hqm_df = hqm_df[:50]
hqm_df.reset_index(inplace=True, drop=True)

portfolio_input()

print(hqm_df)