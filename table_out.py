import csv
import re
import var_dump
from datetime import datetime
from prettytable import PrettyTable

def Prepare(key, vacancy_string, columns_names):
    if key != 'key_skills' and key != 'salary':
        vacancy_string = re.sub(r"<[^>]+>", '', vacancy_string)
        vacancy_string = "; ".join(vacancy_string.split('\n'))
        vacancy_string = ' '.join(vacancy_string.split())
    key, vacancy_string, columns_names = russificate(key, vacancy_string, columns_names)
    return key, vacancy_string, columns_names

def russificate(key, vacancy_string, columns_names):
    for substitution in dic_naming.keys():
        if vacancy_string == substitution:
            vacancy_string = dic_naming[substitution]
        if key == substitution:
            key = dic_naming[substitution]
    columns_names.append(key)
    return key, vacancy_string, columns_names

class InputConect:
    def __init__(self):
        self.file_name = input('Введите название файла: ')
        self.filter_param = input('Введите параметр фильтрации: ').split(': ')
        self.sort_param = input('Введите параметр сортировки: ')
        self.reversed_sort = input('Обратный порядок сортировки (Да / Нет): ')
        self.rows_print = input('Введите диапазон вывода: ').split()
        self.columns_print = input('Введите требуемые столбцы: ')
        InputConect.check_data(self.filter_param, self.sort_param, self.reversed_sort)

    @staticmethod
    def check_data(filter_param, sort_param, reversed_sort):
        if len(filter_param) != 2 and filter_param != ['']:
            print('Формат ввода некорректен')
            exit()
        if filter_param != [''] and filter_param[0] not in dic_naming.values():
            print('Параметр поиска некорректен')
            exit()
        if reversed_sort not in answer_to_bool.keys():
            print('Порядок сортировки задан некорректно')
            exit()
        if sort_param not in dic_naming.values() and sort_param != '':
            print('Параметр сортировки некорректен')
            exit()

    @staticmethod
    def print_table(table, row_beg, row_fin, columns_to_print):
        table.hrules = 1
        table.align = 'l'
        if len(columns_to_print) == 0:
            print(table[row_beg:row_fin])
        else:
            print(table[row_beg:row_fin].get_string(fields=['№'] + columns_to_print.split(", ")))

    @staticmethod
    def prepare_table(dataset, filter_param, sort_param, reversed_sort, rows_print, columns_to_print):
        global mytable
        sort_index = 0
        mytable = PrettyTable()
        all_vacancies = []
        is_empty = True
        have_data = False
        if rows_print:
            beg, fin = (int(rows_print[0]) - 1, int(rows_print[1]) - 1) if len(rows_print) == 2 else (
            int(rows_print[0]) - 1, None)
        else:
            beg, fin = None, None
        for vacancy in dataset.vacancies_objects:
            vacancy_without_key = []
            formatted_row = InputConect.formatter(vacancy.__dict__, filter_param, sort_param)
            if len(formatted_row) != 0:
                is_empty = False
                i = 0
                for key, vacancy_string in formatted_row.items():
                    if key == 'Навыки':
                        skills = vacancy_string
                        vacancy_string = '\n'.join(vacancy_string)
                    if key != 'Оклад':
                        if len(vacancy_string) > 100:
                            vacancy_string = vacancy_string[:100] + '...'
                    vacancy_without_key.append(vacancy_string)
                    if sort_param == key:
                        sort_index = i
                    if key == 'Дата публикации вакансии':
                        have_data = True
                    i += 1
                all_vacancies.append(vacancy_without_key)
                if sort_param == 'Навыки':
                    all_vacancies[-1] += [skills]
        all_vacancies = tuple(InputConect.sort_table(all_vacancies, sort_param, reversed_sort, sort_index))
        for i, vacancy in enumerate(all_vacancies, 1):
            if sort_param == 'Навыки':
                vacancy.pop()
            if have_data:
                vacancy[-1] = datetime.strptime(vacancy[-1], '%Y-%m-%dT%H:%M:%f%z').strftime('%d.%m.%Y')
                vacancy[-3].salary_from = '{:,}'.format(int(float(vacancy[-3].salary_from))).replace(',', ' ')
                vacancy[-3].salary_to = '{:,}'.format(int(float(vacancy[-3].salary_to))).replace(',', ' ')
                vacancy[-3] = f'{vacancy[-3].salary_from} - {vacancy[-3].salary_to} ({currency[vacancy[-3].salary_currency]}) ({dic_salary_gross[vacancy[-3].salary_gross]})'
            else:
                vacancy[-2].salary_from = '{:,}'.format(int(float(vacancy[-2].salary_from))).replace(',', ' ')
                vacancy[-2].salary_to = '{:,}'.format(int(float(vacancy[-2].salary_to))).replace(',', ' ')
                vacancy[-2] = f'{vacancy[-2].salary_from} - {vacancy[-2].salary_to} ({currency[vacancy[-2].salary_currency]}) ({dic_salary_gross[vacancy[-2].salary_gross]})'
            mytable.add_row([i] + vacancy)
        if is_empty:
            print("Ничего не найдено")
            exit()
        return mytable, beg, fin, columns_to_print

    @staticmethod
    def formatter(row, filter_param, sort_param):
        result = {}
        columns_names = []
        for key, vacancy_string in row.items():
            key, vacancy_string, columns_names = Prepare(key, vacancy_string, columns_names)
            if key == 'Навыки':
                '; '.join(vacancy_string)
                result[key] = vacancy_string
            elif key == 'salary':
                curr = currency[vacancy_string.salary_currency]
                payroll = [float(vacancy_string.salary_from), float(vacancy_string.salary_to)]
                result['Оклад'] = vacancy_string
            elif vacancy_string in experience.keys():
                vacancy_string = experience[vacancy_string]
                result[key] = vacancy_string
            elif key == 'Дата публикации вакансии':
                result['Дата публикации вакансии'] = vacancy_string
                date = datetime.strptime(vacancy_string, '%Y-%m-%dT%H:%M:%f%z').strftime('%d.%m.%Y')
            else:
                result[key] = vacancy_string
        flag = 0
        if filter_param == ['']:
            flag = 1
        else:
            if filter_param[0] in result.keys() or filter_param[0] == 'Идентификатор валюты оклада':
                if filter_param[0] == 'Оклад':
                    if int(filter_param[1]) >= payroll[0] and int(filter_param[1]) <= payroll[1]: flag = 1
                elif filter_param[0] == 'Идентификатор валюты оклада':
                    if filter_param[1] == curr: flag = 1
                elif filter_param[0] == 'Навыки':
                    if all(x in result[filter_param[0]] for x in filter_param[1].split(', ')): flag = 1
                elif filter_param[0] == 'Дата публикации вакансии':
                    if date == filter_param[1]: flag = 1
                else:
                    if result[filter_param[0]] == filter_param[1]: flag = 1
            else:
                flag = 0
        mytable.field_names = ['№'] + list(result.keys())
        max_width = dict.fromkeys(list(result.keys()), 20)
        mytable._max_width = max_width
        return result if flag == 1 else {}

    @staticmethod
    def sort_table(all_vacancies, sort_param, reversed_sort, sort_index):
        reversed_sort = answer_to_bool[reversed_sort]
        if len(sort_param) == 0: return all_vacancies
        if sort_param == 'Оклад':
            return sorted(all_vacancies, key=lambda vacancy: float(vacancy[sort_index].currency_to_rub(vacancy[sort_index].salary_from, vacancy[sort_index].salary_to, vacancy[sort_index].salary_currency)), reverse=reversed_sort)
        elif sort_param == 'Навыки':
            return sorted(all_vacancies, key=lambda vacancy: len(vacancy[-1]), reverse=reversed_sort)
        elif sort_param == 'Опыт работы':
            return sorted(all_vacancies, key=lambda vacancy: experience_to_int[vacancy[sort_index]], reverse=reversed_sort)
        else:
            return sorted(all_vacancies, key=lambda vacancy: vacancy[sort_index], reverse=reversed_sort)


class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.vacancies_objects = DataSet.prepare_data(file_name)

    @staticmethod
    def prepare_data(file_name):
        columns, vacancies = DataSet.csv_reader(file_name)
        processed = [x for x in vacancies if len(x) == len(columns) and '' not in x]
        people_data = []
        for line in processed:
            vacancies_list = []
            salary = []
            for i,item in enumerate(line):
                if columns[i] in ['salary_from', 'salary_to', 'salary_gross', 'salary_currency']:
                    salary.append(Prepare(None, item, [])[1])
                    if len(salary) == 4:
                        vacancies_list.append(Salary(salary[0], salary[1], salary[2], salary[3]))
                else:
                    vacancies_list.append(Prepare(None, item, [])[1])
            people_data.append(Vacancy(vacancies_list))
        return people_data

    @staticmethod
    def csv_reader(file_name):
        csv_read = csv.reader(open(file_name, encoding="utf_8_sig"))
        list_data = [x for x in csv_read]
        if len(list_data) == 1:
            print("Нет данных")
            exit()
        if len(list_data) == 0:
            print("Пустой файл")
            exit()
        columns = list_data[0]
        vacancies = list_data[1:]
        return columns, vacancies

class Salary:
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    @staticmethod
    def currency_to_rub(salary_from, salary_to, salary_currency):
        return (float(salary_from)+float(salary_to))/2 * currency_to_rub[salary_currency]


class Vacancy:
    def __init__(self, data_array):
        self.name = data_array[0]
        self.description = data_array[1]
        self.key_skills = data_array[2].split('; ')
        self.experience_id = data_array[3]
        self.premium = data_array[4]
        self.employer_name = data_array[5]
        self.salary = data_array[6]
        self.area_name = data_array[7]
        self.published_at = data_array[8]


dic_salary_gross = {'Да': 'Без вычета налогов',
                    'Нет': 'С вычетом налогов'
                    }

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
              'Оклад' : 'Оклад',
              'False': 'Нет',
              'True': 'Да',
              'FALSE': 'Нет',
              'TRUE': 'Да'
              }

currency = {"AZN": "Манаты",
            "BYR": "Белорусские рубли",
            "EUR": "Евро",
            "GEL": "Грузинский лари",
            "KGS": "Киргизский сом",
            "KZT": "Тенге",
            "RUR": "Рубли",
            "UAH": "Гривны",
            "USD": "Доллары",
            "UZS": "Узбекский сум"
            }

experience = {"noExperience": "Нет опыта",
              "between1And3": "От 1 года до 3 лет",
              "between3And6": "От 3 до 6 лет",
              "moreThan6": "Более 6 лет"
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

answer_to_bool = {
    'Да' : True,
    'Нет': False,
    '': False
    }

experience_to_int = {
    "Нет опыта" : 0,
    "От 1 года до 3 лет" : 1,
    "От 3 до 6 лет" : 3,
    "Более 6 лет" : 6
    }

def get_table():
    parameters = InputConect()
    dataset = DataSet(parameters.file_name)
    prepared_table = InputConect.prepare_table(dataset,parameters.filter_param,parameters.sort_param,parameters.reversed_sort,parameters.rows_print,parameters.columns_print)
    InputConect.print_table(prepared_table[0], prepared_table[1],prepared_table[2],prepared_table[3])