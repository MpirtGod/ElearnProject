import json
import time
import pandas as pd
import numpy as np
import math
import requests


def get_page(page, half_day):
    if half_day:
        params = {
            "specialization": 1,
            "found": 1,
            "per_page": 100,
            "page": page,
            "date_from": f"2022-12-23T12:00:00+0300",
            "date_to": f"2022-12-23T23:59:00+0300"
        }
    else:
        params = {
            "specialization": 1,
            "found": 1,
            "per_page": 100,
            "page": page,
            "date_from": f"2022-12-23T00:00:00+0300",
            "date_to": f"2022-12-23T11:59:00+0300"
        }
    try:
        req = requests.get('https://api.hh.ru/vacancies', params)
        vacancies = req.content.decode()
        req.close()
    except:
        return get_page(page, half_day)
    return vacancies

def get_vacancies():
    columns = ["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]
    df = pd.DataFrame(columns=columns)
    result = []
    for half_day in [False, True]:
        for page in range(0, 999):
            js_obj = json.loads(get_page(page, half_day))
            result.append(js_obj)
            if (js_obj['pages'] - page) <= 1:
                break
            time.sleep(2)
    for page in result:
        for vac in page["items"]:
            if vac["salary"] is None:
                df.loc[len(df)] = [vac["name"], None,
                                   None, None,
                                   vac["area"]["name"], vac["published_at"]]
            else:
                df.loc[len(df)] = [vac["name"], vac["salary"]["from"],
                                   vac["salary"]["to"], vac["salary"]["currency"],
                                   vac["area"]["name"], vac["published_at"]]
    df.to_csv("hh_vacs.csv", index=False)


def make_currency_data(currency_request):
    currency_request['Date'] = currency_request['Date'].apply(lambda x: f'{x[6:]}-{x[3:5]}')
    currency_request['Value'] = pd.to_numeric(currency_request['Value'].str.replace(',', '.'))
    currency_request = currency_request.groupby('Date').aggregate({'Value': 'mean', 'Nominal': 'mean'})
    currency_request['Value'] = currency_request['Value'].div(currency_request['Nominal'].values, axis=0)
    return currency_request.drop(['Nominal'], axis=1).rename(columns={'Value': currency})



def combine_salary_columns(df):
    df.salary_from = df[['salary_from', 'salary_to']].mean(axis=1)
    df['date'] = df.published_at.str.extract(pat = '([0-9]......)')
    df['salary_from'] = df.apply(
        lambda x: round(x['salary_from'] * currency_data.at[x['date'], x['salary_currency']])
        if (x['salary_currency'] != 'RUR' and not np.isnan(x['salary_from']))
        else x['salary_from'], axis=1)
    df = df.assign(salary_from=lambda df_: df_["salary_from"].astype("float32"))
    return df.drop(['salary_to', 'date', 'salary_currency'], axis=1).rename(columns={'salary_from': 'salary'})


if __name__ == "__main__":
    get_vacancies()
    file_name = 'hh_vacs.csv'
    pd.set_option('expand_frame_repr', False)
    df = pd.read_csv(file_name)
    df = df.assign(area_name=lambda df_: df_["area_name"].astype("category"))
    currency_to_localid = pd.read_xml('http://www.cbr.ru/scripts/XML_valFull.asp', encoding='windows-1251')
    currency_to_localid.loc[(currency_to_localid.ISO_Char_Code == 'BYN'), 'ISO_Char_Code'] = 'BYR'
    valid_currency = (df['salary_currency'].value_counts())
    valid_currency = [i for i in list(valid_currency.index) if '''valid_currency[i] >= 5000''' and i != 'RUR']
    # df = df[df.salary_currency.isin(valid_currency+['RUR', float('nan')]) == True]
    startvac, endvac = df['published_at'].min(), df['published_at'].max()

    currency_data = []
    for currency in valid_currency:
        ParentCode = currency_to_localid.loc[currency_to_localid['ISO_Char_Code'] == currency, 'ParentCode'].iloc[0]
        currency_request = pd.read_xml(f'http://www.cbr.ru/scripts/XML_dynamic.asp?'
                                       f'date_req1={startvac[8:10]}/{startvac[5:7]}/{startvac[:4]}&'
                                       f'date_req2={endvac[8:10]}/{endvac[5:7]}/{endvac[:4]}&'
                                       f'VAL_NM_RQ={ParentCode}')
        currency_data.append(make_currency_data(currency_request))
    currency_data = pd.concat(currency_data,axis=1)
    currency_data.to_csv('currency_data.csv')
    df = combine_salary_columns(df)
    # df.head(100).to_csv('first100vacancies.csv')
    df.to_csv('vacs_from_hh.csv')