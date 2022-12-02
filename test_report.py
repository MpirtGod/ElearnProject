from unittest import TestCase
import report_out
import table_out


class as_textTests(TestCase):
    def test_None(self):
        self.assertEqual(report_out.Report.as_text(None), '')
    def test_Empty(self):
        self.assertEqual(report_out.Report.as_text(''), '')
    def test_ListToStr(self):
        self.assertEqual(type(report_out.Report.as_text(['Да', 'Нет'])).__name__, 'str')
    def test_DictToStr(self):
        self.assertEqual(type(report_out.Report.as_text({'Да', 'Нет'})).__name__, 'str')
    def test_TupleToStr(self):
        self.assertEqual(type(report_out.Report.as_text(('Да', ['Нет']))).__name__, 'str')
    def test_String(self):
        self.assertEqual(report_out.Report.as_text('string'), 'string')


class report_out_PrepareTests(TestCase):
    def test_Tags(self):
        self.assertEqual(report_out.DataSet.Prepare('<div>Привет</div>'),'Привет')
    def test_Spaces(self):
        self.assertEqual(report_out.DataSet.Prepare('f    f'),'f f')
    def test_StrWithN(self):
        self.assertEqual(report_out.DataSet.Prepare('two\nstrings'),'two; strings')
    def test_Empty(self):
        self.assertEqual(report_out.DataSet.Prepare(''),'')
    def test_Usual(self):
        self.assertEqual(report_out.DataSet.Prepare('abcabc'),'abcabc')


class SalaryTests(TestCase):
    def test_salary_from(self):
        self.assertEqual(report_out.Salary(10.0, '20.0', 'RUR').salary_from, 10.0)
    def test_salary_to(self):
        self.assertEqual(report_out.Salary(10.0, '20.0', 'RUR').salary_to, '20.0')
    def test_salary_currency(self):
        self.assertEqual(report_out.Salary('10.0', '20.0', 'RUR').salary_currency, 'RUR')
    def test_salary_to_rub(self):
        self.assertEqual(report_out.Salary('10.0', '20.0', 'EUR').salary_to_rub, 898.5)


class currency_to_rubTests(TestCase):
    def test_two_strings(self):
        self.assertEqual(report_out.Salary.currency_to_rub('10.0', '20.0', 'EUR'), 898.5)
    def test_string_and_float(self):
        self.assertEqual(report_out.Salary.currency_to_rub(10.0, '20.0', 'EUR'), 898.5)
    def test_equal_string_and_float(self):
        self.assertEqual(report_out.Salary.currency_to_rub('15.0', 15.0, 'EUR'), 898.5)
    def test_equal_string_and_float_RUR(self):
        self.assertEqual(report_out.Salary.currency_to_rub('15.0', 15.0, 'RUR'), 15.0)
    def test_equal_string_and_int_RUR(self):
        self.assertEqual(report_out.Salary.currency_to_rub('15', 15, 'RUR'), 15.0)


class table_out_PrepareTests(TestCase):
    def test_Valid_key_and_vacancy_string(self):
        self.assertEqual(table_out.Prepare('name', 'TRUE', []), ('Название', 'Да', ['Название']))
    def test_Invalid_key_and_vacancy_string(self):
        self.assertEqual(table_out.Prepare('dadadadada', 'Рука', []), ('dadadadada', 'Рука', ['dadadadada']))
    def test_Empty_key_and_vacancy_string(self):
        self.assertEqual(table_out.Prepare('', '', []), ('', '', ['']))
    def test_Swaped_key_and_vacancy_string(self):
        self.assertEqual(table_out.Prepare('TRUE', 'name', []), ('Да', 'Название', ['Да']))


class check_dataTests(TestCase):
    def test_filter_param_len_equals_1(self):
        with self.assertRaises(SystemExit):
            table_out.InputConect.check_data(['one'], 'Название', 'Нет')
    def test_filter_param_len_equals_3(self):
        with self.assertRaises(SystemExit):
            table_out.InputConect.check_data(['one','two','three'], 'Название', 'Нет')
    def test_filter_param_invalid(self):
        with self.assertRaises(SystemExit):
            table_out.InputConect.check_data(['one','two'], 'Название', 'Нет')
    def test_reversed_sort_invalid(self):
        with self.assertRaises(SystemExit):
            table_out.InputConect.check_data(['Опыт работы', 'От 3 до 6 лет'], 'Название', 'Murr')
    def test_sort_param_invalid(self):
        with self.assertRaises(SystemExit):
            table_out.InputConect.check_data(['Опыт работы', 'От 3 до 6 лет'], 'Puff', 'Нет')