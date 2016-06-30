import re
import unittest

from .base import TestCaseBase
from ..parsers.mts_parser import MTS_Parser


class TestMTSParser(TestCaseBase):

    def test_point_coordinate_reges_is_correct(self):
        text = """
var placemark91179 = new YMaps.Placemark(new YMaps.GeoPoint(31.015536,52.447689), {style: s, hideIcon: false});
"""
        match = re.findall(MTS_Parser.YA_MAPS_POINT_REGEX, text)
        self.assertTrue(match, msg="Match should exist")
        coord = match[0]
        self.assertEqual(str(coord[0]), '91179')
        self.assertEqual(str(coord[1]), '31.015536')
        self.assertEqual(str(coord[2]), '52.447689')

    def test_point_description_correctly_extracted(self):
        text = """
            placemark92882.description = "Адрес: Минск, ул. Голодеда, 16<BR/>";"""

        match = re.findall(MTS_Parser.YA_MAPS_POINT_DESCRIPTION_REGEX, text)
        self.assertTrue(match, msg="Match should exist")
        coord = match[0]
        self.assertEqual(str(coord[0]), '92882')
        self.assertEqual(str(coord[1]), 'Адрес: Минск, ул. Голодеда, 16<BR/>')

    def test_point_name_correctly_extracted(self):
        text = """
            placemark92882.name = "Подключен";"""

        match = re.findall(MTS_Parser.YA_MAPS_POINT_NAME_REGEX, text)
        self.assertTrue(match, msg="Match should exist")
        coord = match[0]
        self.assertEqual(str(coord[0]), '92882')
        self.assertEqual(str(coord[1]), 'Подключен')


if __name__ == '__main__':
    unittest.main()
