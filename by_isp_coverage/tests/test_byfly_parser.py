import re
import unittest

from .base import TestCaseBase

from ..connection import Connection
from ..parsers.byfly_parser import ByflyParser, valid_connection


# 8 к.2 ЮР. ЛИЦА
# 45 (3 подъезд)
# 25А ЮР. ЛИЦА
# 20/2 ЮР. ЛИЦА
# 76А юр. лица
# 41, 41а, 58, 58-1
class TestHouseSplitting(TestCaseBase):

    def create_connection(self, region="test", city="test", street="test", provider="test", house="1", status=""):
        return Connection(region=region, city=city, street=street,
                          provider=provider, house=house, status=status)

    def test_simple_connection_returned_as_is(self):
        test_c = self.create_connection(house="20")
        result = valid_connection(test_c)
        self.assertEqual(result[0], test_c)

    def test_list_with_digital_numbers_wo_spaces_processed_correctly(self):
        test_c = self.create_connection(house="20,30,40")
        result = valid_connection(test_c)

        expected_results = [self.create_connection(house=str(i)) for i in (20, 30, 40)]
        self.assertEqual(expected_results, result)

    def test_list_with_digital_numbers_with_spaces_processed_correctly(self):
        test_c = self.create_connection(house="20,30, 40")
        result = valid_connection(test_c)

        expected_results = [self.create_connection(house=str(i)) for i in (20, 30, 40)]
        self.assertEqual(expected_results, result)

    def test_artificial_person_simple_upper(self):
        test_c = self.create_connection(house="2 ЮР. ЛИЦА", status="Here I am")
        result = valid_connection(test_c)

        expected_result = self.create_connection(house="2", status="Here I am (юридические лица)")
        self.assertEqual(result[0], expected_result)

    def test_artificial_person_long_format(self):
        test_c = self.create_connection(house="187 (юридические лица)", status="Here I am")
        result = valid_connection(test_c)

        expected_result = self.create_connection(house="187", status="Here I am (юридические лица)")
        self.assertEqual(result[0], expected_result)

    def test_building_numbers_parsed_correctly(self):
        test_c_uppercase = self.create_connection(house="29А")
        result = valid_connection(test_c_uppercase)
        expected_result = self.create_connection(house="29 (корпус А)")
        self.assertEqual(result[0], expected_result)

    def test_building_numbers_with_dash_parsed_correctly(self):
        test_with_dash = self.create_connection(house="29/1")
        result = valid_connection(test_with_dash)
        expected_result = self.create_connection(house="29 (корпус 1)")
        self.assertEqual(result[0], expected_result)

    def test_building_numbers_with_letter_parsed_correctly(self):
        test_with_letter = self.create_connection(house="8 к.4")
        result = valid_connection(test_with_letter)
        expected_result = self.create_connection(house="8 (корпус 4)")
        self.assertEqual(result[0], expected_result)

    def test_building_numbers_with_space_parsed_correctly(self):
        test_with_space = self.create_connection(house="8 Б")
        result = valid_connection(test_with_space)
        expected_result = self.create_connection(house="8 (корпус Б)")
        self.assertEqual(result[0], expected_result)

    def test_building_numbers_with_hyphen_parsed_correctly(self):
        test_with_hyphen = self.create_connection(house="8-2")
        result = valid_connection(test_with_hyphen)
        expected_result = self.create_connection(house="8 (корпус 2)")
        self.assertEqual(result[0], expected_result)

if __name__ == '__main__':
    unittest.main()
