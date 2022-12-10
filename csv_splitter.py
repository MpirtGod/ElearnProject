import pathlib
import pandas as pd
from datetime import datetime
import multiprocessing as mp
import time

def get_year(date):
    return int(date[:4])

def make_statistic(file, vacancy_name):
    one_year_vacancies = pd.read_csv(file)
    one_year_vacancies['salary'] = one_year_vacancies[['salary_from', 'salary_to']].mean(axis=1)
    year = int(file.name[-8:-4])

    salary_by_years = int(one_year_vacancies.salary.mean())
    vacs_by_years = one_year_vacancies.shape[0]

    vac_mean = one_year_vacancies.loc[one_year_vacancies['name'].str.contains(vacancy_name)]['salary']
    vac_counts_by_years = vac_mean.shape[0]
    vac_salary_by_years = int(vac_mean.mean())
    return year, salary_by_years, vacs_by_years, vac_salary_by_years, vac_counts_by_years


if __name__ == '__main__':
    file_name = input('Введите название файла: ')
    vacancy_name = input('Введите название профессии: ')

    pd.set_option('expand_frame_repr', False)
    df = pd.read_csv(file_name)

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
    temp = []
    for file in filelist:
        temp.append((file, vacancy_name))
    start_time = time.time()
    with mp.Pool(2) as p:
        mp.freeze_support()
        result_list = p.starmap(make_statistic, temp)
        p.close()
        p.join()

    print("--- %s seconds ---" % (time.time() - start_time))

    for result in result_list:
        salary_by_years[result[0]] = result[1]
        vacs_by_years[result[0]] = result[2]
        vac_salary_by_years[result[0]] = result[3]
        vac_counts_by_years[result[0]] = result[4]

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


