import table_out
import report_out


type_out = input("Введите вид формирования данных: ")
if type_out == 'Вакансии':
    table_out.get_table()
elif type_out == 'Статистика':
    report_out.get_table()
else:
    print('Неверный ввод!')