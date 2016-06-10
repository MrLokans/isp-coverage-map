import json

import requests
from bs4 import BeautifulSoup as bs

from .point import Point


class AtlantParser(object):
    PARSER_NAME = "atlant"
    PARSER_URL = "http://telecom.by/internet/minsk/ethernet"

    def get_points(self):
        return []


def main():
    parser = AtlantParser()
    points = parser.get_points()
    print(points)


if __name__ == '__main__':
    main()
