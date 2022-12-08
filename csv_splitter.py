import pathlib

import pandas as pd
from datetime import datetime
import csv
import re
import multiprocessing

import time
# start_time = time.time()

class DictionariesData:
    dic_naming = {'name': 'Название',
                  'employer_name': 'Компания',
                  'description': 'Описание',
                  'key_skills': 'Навыки',
                  'experience_id': 'Опыт работы',
                  'premium': 'Премиум-вакансия',
                  'salary_from': 'Нижняя граница вилки оклада',
                  'salary_to': 'Верхняя граница вилки оклада',
                  'salary_gross': 'Оклад указан до вычета налогов',
                  'salary_currency': 'Идентификатор валюты оклада',
                  'area_name': 'Название региона',
                  'published_at': 'Дата публикации вакансии',
                  'Оклад': 'Оклад',
                  'False': 'Нет',
                  'True': 'Да',
                  'FALSE': 'Нет',
                  'TRUE': 'Да'
                  }


    currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }

class InputConect:
    def __init__(self):
        self.file_name = input('Введите название файла: ')
        self.filter_param = input('Введите название профессии: ')

    @staticmethod
    def get_year(date):
        return int(date[:4])

    @staticmethod
    def print_data(vacancy_name, filter_param):
        pd.set_option('expand_frame_repr', False)
        df = pd.read_csv(vacancy_name)
        df['years'] = df['published_at'].apply(lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z").year)
        unique_years = df['years'].unique()

        for year in unique_years:
            data = df[df['years'] == year]
            data.drop(['years'], axis=1).to_csv(f'csv_by_years\\part_{year}.csv', index=False)

        salary_by_years = {year: 0 for year in unique_years}
        vacs_by_years = {year: 0 for year in unique_years}
        vac_salary_by_years = {year: 0 for year in unique_years}
        vac_counts_by_years = {year: 0 for year in unique_years}

        path_csv = pathlib.Path('csv_by_years\\')
        filelist = [f_name for f_name in path_csv.glob('*.csv')]
        def make_statistic(file):
            one_year_vacancies = pd.read_csv(file)
            one_year_vacancies['salary'] = one_year_vacancies[['salary_from','salary_to']].mean(axis = 1)
            year = int(file.name[-8:-4])

            salary_by_years[year] = int(one_year_vacancies.salary.mean())
            vacs_by_years[year] = one_year_vacancies.shape[0]

            vac_mean = one_year_vacancies.loc[one_year_vacancies['name'].str.contains(filter_param)]['salary']
            vac_counts_by_years[year] = vac_mean.shape[0]
            vac_salary_by_years[year] = int(vac_mean.mean())

        if __name__ == '__main__':
            with multiprocessing.Pool(multiprocessing.cpu_count() * 3) as p:
                p.map(InputConect, filelist)

        df['salary'] = df[['salary_from', 'salary_to']].mean(axis=1)
        salary_by_city_percentage = df.groupby('area_name').aggregate({'salary': 'mean'}).sort_values('salary', ascending=False)
        salary_by_city_percentage['percentage'] = df.area_name.value_counts() / df.area_name.value_counts().sum()

        salary_by_cities = {}
        for index, row in salary_by_city_percentage.iterrows():
            if (row['percentage']>=0.01 and len(salary_by_cities)<10):
                salary_by_cities[index] = int(row['salary'])

        vacs_by_cities = {}
        salary_by_city_percentage = salary_by_city_percentage.sort_values('percentage', ascending=False)
        for index, row in salary_by_city_percentage.iterrows():
            if (row['percentage']>=0.01 and len(vacs_by_cities)<10):
                vacs_by_cities[index] = row['percentage'].round(4)


        print('Динамика уровня зарплат по годам:', salary_by_years)
        print('Динамика количества вакансий по годам:', vacs_by_years)
        print('Динамика уровня зарплат по годам для выбранной профессии:', vac_salary_by_years)
        print('Динамика количества вакансий по годам для выбранной профессии:', vac_counts_by_years)
        print('Уровень зарплат по городам (в порядке убывания):', salary_by_cities)
        print('Доля вакансий по городам (в порядке убывания):', vacs_by_cities)


class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name

    @staticmethod
    def Prepare(text):
        text = re.sub(r"<[^>]+>", '', text)
        text = "; ".join(text.split('\n'))
        text = ' '.join(text.split())
        return text

class Salary:
    def __init__(self, salary_from, salary_to, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_currency = salary_currency
        self.salary_to_rub = Salary.currency_to_rub(salary_from, salary_to, salary_currency)

    @staticmethod
    def currency_to_rub(salary_from, salary_to, salary_currency):
        return (float(salary_from) + float(salary_to)) / 2 * DictionariesData.currency_to_rub[salary_currency]


class Vacancy:
    def __init__(self, name, salary, area_name, published_at):
        self.name = name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at


parameters = InputConect()
dataset = DataSet(parameters.file_name)
InputConect.print_data(parameters.file_name, parameters.filter_param)
# print("--- %s seconds ---" % (time.time() - start_time))