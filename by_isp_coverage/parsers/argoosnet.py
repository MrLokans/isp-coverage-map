import json
import logging
import queue
import re

import requests
from bs4 import BeautifulSoup as bs

from by_isp_coverage.parsers.base import BaseParser
from by_isp_coverage.point import Point
from by_isp_coverage.connection import Connection


class ArgoosnetParser(BaseParser):
    PARSER_NAME = "argoosnet"
    PARSER_URL = "http://www.argoosnet.by/"
    DEFAULT_CITY = "Молодечно"
    START_URL = 'http://www.argoosnet.by/connection'
    SEARCH_URL = 'http://www.argoosnet.by/index.php?option=com_fabrik&format=raw&controller=plugin&task=pluginAjax&plugin=fabrikcascadingdropdown&method=ajax_getOptions&element_id=17&lang=ru'

    def __init__(self, coordinate_obtainer=None, validator=None):
        self.coordinate_obtainer = coordinate_obtainer
        self.validator = validator
        self.soup = self._get_soup()

    def _get_soup(self):
        return bs(requests.get(self.START_URL).text, "html.parser")

    def get_points(self):
        return []

    def get_connections(self):
        select = self.soup.find('select', id='conn_connections___StreetName')
        options = select.find_all('option',
                                  value=re.compile(r"\d+"))
        streets = {o.text: o.get('value')
                   for o in options
                   if o.text != 'Другая'}
        for street_name, street_id in streets.items():
            for house in self.get_street_houses(street_id):
                yield Connection(self.PARSER_NAME, "", self.DEFAULT_CITY,
                                 street_name, house, "Подключен")

    def get_street_houses(self, street_id):
        r = requests.post(self.SEARCH_URL, data={
                "conn_connections___StreetName": street_id,
                "conn_connections___StreetName_raw": street_id,
                "v": street_id,
                "formid": 4
        })
        r = r.json()
        houses = [i['value']
                  for i in r
                  if i['value'] not in ('', 'Другой')]
        return houses

if __name__ == '__main__':
    parser = ArgoosnetParser()
    for c in parser.get_connections():
        print(c)
