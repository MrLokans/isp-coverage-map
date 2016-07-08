import re
import unittest

from unittest.mock import MagicMock

from .base import TestCaseBase
from ..parsers.unet_parser import UNETParser


class TestUNETParser(TestCaseBase):

    def test_street_names_extracted_from_ajax_response(self):
        resp = MagicMock()
        resp.text = """
<a onclick='click_street.call(this,"31", "Белецкого"); return false;' href='#'>Белецкого</a>
<a onclick='click_street.call(this,"1", "Брестская "); return false;' href='#'>Брестская </a>
<a onclick='click_street.call(this,"48", "Леонида Беды"); return false;' href='#'>Леонида Беды</a>
"""
        parser = UNETParser(None)

        result = list(parser._street_tuples_from_response(resp))
        expected = [("31", "Белецкого"),
                    ("1", "Брестская"),
                    ("48", "Леонида Беды")]
        self.assertEqual(result, expected)

    def test_house_numbers_extracted_from_ajax_response(self):
        resp = MagicMock()
        resp.text = """
<a onclick='click_house.call(this,"31","792", "2к7"); return false;' href='#'>2к7</a>
<a onclick='click_house.call(this,"31","794", "2"); return false;' href='#'>2</a>
<a onclick='click_house.call(this,"31","436", "20"); return false;' href='#'>20</a>
<a onclick='click_house.call(this,"31","437", "22"); return false;' href='#'>22</a>
<a onclick='click_house.call(this,"31","438", "24"); return false;' href='#'>24</a>
<a onclick='click_house.call(this,"31","791", "26"); return false;' href='#'>26</a>
"""
        parser = UNETParser(None)

        result = list(parser._houses_from_api_response(resp))
        expected = ["2к7", "2", "20", "22", "24", "26"]
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
