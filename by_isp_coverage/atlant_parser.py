import json

import requests
import grequests
from bs4 import BeautifulSoup as bs

from .point import Point


class AtlantParser(object):
    PARSER_NAME = "atlant"
    PARSER_URL = "http://telecom.by/internet/minsk/ethernet"
    STREET_SEARCH_URL = "http://telecom.by/at/zone/autocomplete/streets/2"

    def get_points(self):
        return []

    def get_street_names(self):
        """Obtain all streets with available internet connection"""
        street_names = []
        ltrs = "0123456789абвгдеёжзийклмнопрстуфхцчшщэюя"
        urls = ("/".join([self.STREET_SEARCH_URL, l]) for l in ltrs)
        rs = (grequests.get(u) for u in urls)
        results = grequests.map(rs)
        for r in results:
            street_names.extend(r.json())
        return street_names

    def get_house_list_for_street(self, street_name):
        pass


def main():
    parser = AtlantParser()
    points = parser.get_points()
    points = parser.get_street_names()
    print(points)


if __name__ == '__main__':
    main()
