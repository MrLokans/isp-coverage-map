import re

import requests
from bs4 import BeautifulSoup as bs

from by_isp_coverage.parsers.base import BaseParser
from by_isp_coverage.connection import Connection


class InfolanParser(BaseParser):
    PARSER_NAME = "infolan"
    PARSER_URL = "http://infolan.by"
    SEARCH_URL = "/".join([PARSER_URL, "uslugi/proverit-adres.html"])

    def __init__(self, coordinate_obtainer=None, validator=None):
        self.soup = self._get_page_soup()
        self.coordinate_obtainer = coordinate_obtainer
        self.validator = validator

    def _get_page_soup(self):
        r = requests.get(self.SEARCH_URL)
        return bs(r.text, "html.parser")

    def _extract_selects(self):
        house_selects = self.soup.find_all(id=re.compile(r"selectmenuD-\d+"))
        return house_selects

    def _extract_houses_from_select(self, select_soup):
        return (o.get('value') for o in select_soup.find_all('option'))

    def get_street_names(self):
        selector = "select#selectmenuD2 option"
        streets = [s.text for s in self.soup.select(selector)][1:]
        return streets

    def get_points(self):
        streets = self.get_street_names()
        selects = self._extract_selects()
        data = ((street, self._extract_houses_from_select(select))
                for street, select in zip(streets, selects))
        return self.coordinate_obtainer.get_points(data)

    def get_connections(self):
        streets = self.get_street_names()
        selects = self._extract_selects()
        for street, select in zip(streets, selects):
            for house in self._extract_houses_from_select(select):
                yield Connection(self.PARSER_NAME, "Минск", "Минск",
                                 street, house, "Есть подключение")

if __name__ == '__main__':
    parser = InfolanParser(None, None)
    for c in parser.get_connections():
        print(c)
