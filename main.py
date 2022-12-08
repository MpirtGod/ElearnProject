import table_out
import report_out
import csv_splitter
# import cProfile
# import pstats
# cProfile.run('csv_splitter', 'restats')
# p=pstats.Stats('restats')
# p.sort_stats(pstats.SortKey.TIME).print_stats(0)

"""Дает пользователю возможность выбора что печатать и использует report_out и table_out для печати.
"""
type_out = input("Введите вид формирования данных: ")
if type_out == 'Вакансии':
    table_out.get_table()
elif type_out == 'Статистика':
    report_out.get_table()
else:
    print('Неверный ввод!')