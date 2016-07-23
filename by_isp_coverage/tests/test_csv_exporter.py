from io import StringIO
import unittest
from collections import namedtuple

from ..csv_exporter import CSV_Exporter
from ..connection import Connection
from ..point import Point


class TestCSVExporterClass(unittest.TestCase):

    def test_class_wo_fields_attr_raises_assertion_error(self):
        with self.assertRaises(AssertionError):
            CSV_Exporter.export_namedtuple_values("test", [object()])

    def test_namedtuple_data_is_written_to_csv_file_from_generator(self):
        TestCls = namedtuple('TestCls',
                             ('field_1', 'field_2', 'field_3'))

        test_sequence = (v for v in [TestCls("value_1", "value_2", "value_3"),
                                     TestCls("value_4", "value_5", "value_6")])
        output = StringIO()

        CSV_Exporter._export_namedtuple_values_fd(output, test_sequence)
        output.seek(0)
        header_line = output.readline().strip()
        self.assertEqual(header_line.split(","), ["field_1", "field_2", "field_3"])
        first_line = output.readline().strip()
        second_line = output.readline().strip()
        print("First: ", first_line)
        print("Second: ", second_line)
        self.assertEqual(first_line.split(","),
                         ["value_1", "value_2", "value_3"])
        self.assertEqual(second_line.split(","),
                         ["value_4", "value_5", "value_6"])

    def test_namedtuple_data_is_written_to_csv_file_from_list(self):
        TestCls = namedtuple('TestCls',
                             ('field_1', 'field_2', 'field_3'))

        test_sequence = [TestCls("value_1", "value_2", "value_3"),
                         TestCls("value_4", "value_5", "value_6")]
        output = StringIO()

        CSV_Exporter._export_namedtuple_values_fd(output, test_sequence)
        output.seek(0)
        header_line = output.readline().strip()
        self.assertEqual(header_line.split(","),
                         ["field_1", "field_2", "field_3"])
        first_line = output.readline().strip()
        second_line = output.readline().strip()
        print("First: ", first_line)
        print("Second: ", second_line)
        self.assertEqual(first_line.split(","),
                         ["value_1", "value_2", "value_3"])
        self.assertEqual(second_line.split(","),
                         ["value_4", "value_5", "value_6"])
