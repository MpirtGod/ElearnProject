import pandas as pd

currency_to_localid = {'USD': 'R01235',
                       'KZT': 'R01335',
                       'BYR': 'R01090',
                       'UAH': 'R01720',
                       'EUR': 'R01239'}

file_name = 'vacancies_dif_currencies.csv'
pd.set_option('expand_frame_repr', False)
df = pd.read_csv(file_name)
valid_currency = (df['salary_currency'].value_counts())
valid_currency = [i for i in list(valid_currency.index) if valid_currency[i] >= 5000 and i != 'RUR']
df = df[df.salary_currency.isin(valid_currency) == True]
startvac, endvac = df['published_at'].loc[df.index[0]], df['published_at'].loc[df.index[-1]]

currency_data = []
for currency in valid_currency:
    currency_request = pd.read_xml(f'http://www.cbr.ru/scripts/XML_dynamic.asp?'
                                   f'date_req1={startvac[8:10]}/{startvac[5:7]}/{startvac[:4]}&'
                                   f'date_req2={endvac[8:10]}/{endvac[5:7]}/{endvac[:4]}&'
                                   f'VAL_NM_RQ={currency_to_localid[currency]}')
    currency_request['Date'] = currency_request['Date'].apply(lambda x: f'{x[6:]}-{x[3:5]}')
    currency_request['Value'] = pd.to_numeric(currency_request['Value'].apply(lambda x: x.replace(',','.')))
    currency_request = currency_request.groupby('Date').aggregate({'Value':'mean', 'Nominal':'mean'})
    currency_request['Value'] = currency_request['Value'].div(currency_request['Nominal'].values, axis=0)
    currency_data.append(currency_request.drop(['Nominal'], axis=1).rename(columns = {'Value':currency}))
result = pd.concat(currency_data,axis=1)
result.to_csv('currency_data.csv')