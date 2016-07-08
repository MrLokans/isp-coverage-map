import unittest


from ..connection import Connection
from ..validators import ConnectionValidator


class TestCityFormatting(unittest.TestCase):

    def setUp(self):
        self.validator = ConnectionValidator()

    def create_connection(self, region="test", city="test",
                          street="test", provider="test",
                          house="1", status=""):
        return Connection(region=region, city=city, street=street,
                          provider=provider, house=house, status=status)

    def test_correctly_format_city_remains_the_same(self):
        city = "Сенница"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(city, validated)

    def test_single_word_uppercase_city_transformed_correctly(self):
        city = "СЕННИЦА"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(validated, "Сенница")

    def test_multiple_word_uppercase_city_transformed_correctly(self):
        city = "СЕННИЦА БОЛЬШАЯ"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(validated, "Сенница Большая")

    def test_removes_abbreviations(self):
        options = [
            ('Хотимск г.п.', 'Хотимск'),
            ('Шклов г.', 'Шклов'),
            ('Межисятки аг.', 'Межисятки'),
            ('Вязынь д.', 'Вязынь'),
            ('Мачулищи п.г.т', 'Мачулищи'),
            ('д. Сосновая', 'Сосновая'),
            ('Нарочь к.', 'Нарочь'),
            ('Жемчужный агр.', 'Жемчужный'),
        ]
        for opt in options:
            validated = self.validator.validate_city_field(opt[0])[0]
            self.assertEqual(validated, opt[1])

    def test_converts_to_correct_case_with_abbreviations(self):
        options = [
            ('ХОТИМСК г.п.', 'Хотимск'),
            ('МЕЖИСЯТКИ МЕЖДУНАРОДНЫЕ аг.', 'Межисятки Международные'),
            ('д. СОСНОВАЯ', 'Сосновая'),
        ]
        for opt in options:
            validated = self.validator.validate_city_field(opt[0])[0]
            self.assertEqual(validated, opt[1])

    def test_extra_cases(self):
        city = "САМОХВАЛОВИЧИ п"
        validated = self.validator.validate_city_field(city)[0]
        self.assertEqual(validated, "Самохваловичи")

    def test_city_connections_validated(self):
        options = [
            ('ХОТИМСК г.п.', 'Хотимск'),
            ('МЕЖИСЯТКИ МЕЖДУНАРОДНЫЕ аг.', 'Межисятки Международные'),
            ('д. СОСНОВАЯ', 'Сосновая'),
        ]
        expected_results = [self.create_connection(city=o[1]) for o in options]
        test_data = [self.create_connection(city=o[0]) for o in options]
        self.assertEqual(list(self.validator._validate_city(test_data)),
                         expected_results)

    def test_artificial_person_simple_upper(self):
        test_c = self.create_connection(house="2 ЮР. ЛИЦА", status="Here I am")
        validated = list(self.validator._validate_house([test_c]))
        expected_result = self.create_connection(house="2", status="Here I am (юридические лица)")
        self.assertEqual(validated, [expected_result])
