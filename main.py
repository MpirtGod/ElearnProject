import table_out
import report_out

"""Дает пользователю возможность выбора что печатать и использует report_out и table_out для печати.
"""

type_out = input("Введите вид формирования данных: ")
if type_out == 'Вакансии':
    table_out.get_table()
elif type_out == 'Статистика':
    report_out.get_table()
else:
    print('Неверный ввод!')