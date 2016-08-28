import requests
from bs4 import BeautifulSoup as bs

from .base import BaseParser
from ..connection import Connection
from ..point import Point


class InfolanParser(BaseParser):
    PARSER_NAME = "infolan"
    PARSER_URL = "http://infolan.by"
    SEARCH_URL = "/".join([PARSER_URL, "uslugi/proverit-adres.html"])

    def get_street_names(self):
        r = requests.get(self.SEARCH_URL)
        soup = bs(r.text, "html.parser")
        selector = "select#selectmenuD2 option"
        streets = [s.text for s in soup.select(selector)][1:]
        return streets

    def get_points(self):
        return []

    def get_connections(self):
        return []

if __name__ == '__main__':
    parser = InfolanParser(None, None)
    print(parser.get_street_names())
